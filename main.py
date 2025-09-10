from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
import tempfile
import logging
from typing import Optional
import uvicorn
import re
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    settings.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    logger.error("Please check your .env file and ensure GOOGLE_API_KEY is set correctly")

app = FastAPI(
    title="FeediaAI Backend",
    description="AI-powered image generation using Google Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
try:
    client = genai.Client()
    logger.info("Gemini client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini client: {e}")
    client = None

def create_food_image_prompt(user_prompt: str, uploaded_image: Image = None) -> str:
    """
    Create an enhanced prompt for generating authentic food images
    """
    # Extract food-related keywords from the prompt
    food_keywords = []
    food_terms = [
        'pizza', 'burger', 'pasta', 'salad', 'sandwich', 'soup', 'steak', 'chicken', 
        'fish', 'rice', 'noodles', 'bread', 'cake', 'dessert', 'fruit', 'vegetable',
        'breakfast', 'lunch', 'dinner', 'appetizer', 'main course', 'side dish',
        'italian', 'chinese', 'mexican', 'japanese', 'indian', 'french', 'thai',
        'spicy', 'sweet', 'savory', 'grilled', 'fried', 'baked', 'roasted', 'steamed'
    ]
    
    prompt_lower = user_prompt.lower()
    for term in food_terms:
        if term in prompt_lower:
            food_keywords.append(term)
    
    # Create a comprehensive food image generation prompt
    base_prompt = f"""
    Create a completely new, unique, and authentic food image based on this description: "{user_prompt}"
    
    IMPORTANT REQUIREMENTS:
    - Generate a BRAND NEW, ORIGINAL image from scratch - do NOT modify or add text to any existing image
    - Create a photorealistic, high-quality food image that looks professional and appetizing
    - Focus on the visual characteristics and presentation of the food described
    - Make the image suitable for restaurant menus, food blogs, or marketing materials
    - Ensure proper lighting, composition, and food styling
    - The image should be visually compelling and make the food look delicious
    """
    
    # Add specific styling based on food type
    if any(keyword in food_keywords for keyword in ['pizza', 'burger', 'sandwich', 'fast food']):
        base_prompt += """
        - Use casual, appetizing food photography style
        - Include natural lighting and warm tones
        - Show the food from an appealing angle (45-degree angle or top-down)
        """
    elif any(keyword in food_keywords for keyword in ['cake', 'dessert', 'sweet']):
        base_prompt += """
        - Use elegant dessert photography style
        - Include soft, diffused lighting
        - Focus on texture and visual appeal
        - Consider adding complementary colors or garnishes
        """
    elif any(keyword in food_keywords for keyword in ['salad', 'vegetable', 'healthy']):
        base_prompt += """
        - Use fresh, vibrant food photography style
        - Emphasize natural colors and crisp textures
        - Use bright, natural lighting
        - Show the freshness and quality of ingredients
        """
    elif any(keyword in food_keywords for keyword in ['steak', 'grilled', 'meat']):
        base_prompt += """
        - Use dramatic food photography style
        - Emphasize the char, grill marks, or cooking technique
        - Use warm, appetizing lighting
        - Show the texture and juiciness of the meat
        """
    
    # Add technical specifications
    base_prompt += """
    
    TECHNICAL SPECIFICATIONS:
    - High resolution and professional quality
    - Clean, uncluttered background
    - Proper depth of field to highlight the food
    - Appetizing color palette
    - No text overlays or watermarks
    - Focus on the food as the main subject
    """
    
    return base_prompt.strip()

@app.get("/")
async def root():
    return {"message": "FeediaAI Backend is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "gemini_available": client is not None}

@app.post("/api/generativeImage")
async def generate_image(
    uploaded_image: UploadFile = File(None),
    prompt: str = Form(...)
):
    """
    Generate an image using Google Gemini 2.5 Flash model
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client not available")
    
    try:
        # Check if image is provided
        if uploaded_image is not None:
            # Validate file type
            if uploaded_image.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed types: {settings.ALLOWED_IMAGE_TYPES}")
            
            # Validate file size
            if uploaded_image.size > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes")
            
            # Read and process the uploaded image
            image_data = await uploaded_image.read()
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image if too large (Gemini has size limits)
            if image.width > settings.MAX_IMAGE_SIZE or image.height > settings.MAX_IMAGE_SIZE:
                image.thumbnail((settings.MAX_IMAGE_SIZE, settings.MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
            
            # Save processed image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                image.save(temp_file.name, 'JPEG', quality=settings.IMAGE_QUALITY)
                temp_image_path = temp_file.name
            
            try:
                # Load the processed image
                processed_image = Image.open(temp_image_path)
                
                # Generate content using Gemini with uploaded image
                logger.info(f"Generating authentic food image with uploaded image and prompt: {prompt}")
                
                # Use the enhanced food-specific prompt function with image context
                enhanced_prompt = create_food_image_prompt(prompt, processed_image)
                enhanced_prompt += "\n\n- Use the uploaded image as inspiration but create something completely new and original"
                
                response = client.models.generate_content(
                    model=settings.GEMINI_IMAGE_MODEL,
                    contents=[enhanced_prompt, processed_image],
                )
            finally:
                # Clean up temporary image file
                if os.path.exists(temp_image_path):
                    os.unlink(temp_image_path)
        else:
            # Generate image without uploaded image (text-to-image only)
            logger.info(f"Generating authentic food image from text prompt only: {prompt}")
            
            # Use the enhanced food-specific prompt function
            enhanced_prompt = create_food_image_prompt(prompt)
            
            response = client.models.generate_content(
                model=settings.GEMINI_IMAGE_MODEL,
                contents=[enhanced_prompt],
            )
        
        # Process the response
        generated_image_data = None
        response_text = ""
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                response_text += part.text
            elif part.inline_data is not None:
                generated_image_data = part.inline_data.data
        
        if not generated_image_data:
            raise HTTPException(status_code=500, detail="No image generated by Gemini")
        
        # Convert generated image to base64 for frontend
        generated_image = Image.open(BytesIO(generated_image_data))
        
        # Save generated image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_generated:
            generated_image.save(temp_generated.name, 'PNG')
            generated_image_path = temp_generated.name
        
        try:
            # Read the generated image and convert to base64
            with open(generated_image_path, 'rb') as f:
                generated_image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Return the generated image as base64 data URL
            generated_image_url = f"data:image/png;base64,{generated_image_base64}"
            
            return JSONResponse(content={
                "success": True,
                "generated_image": generated_image_url,
                "response_text": response_text,
                "message": "Image generated successfully"
            })
            
        finally:
            # Clean up temporary files
            if 'temp_image_path' in locals() and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
            if os.path.exists(generated_image_path):
                os.unlink(generated_image_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.post("/api/generateImageFromText")
async def generate_image_from_text(prompt: str = Form(...)):
    """
    Generate a completely new image from text prompt only (no uploaded image)
    This is better for creating unique, authentic images
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client not available")
    
    try:
        logger.info(f"Generating new image from text prompt: {prompt}")
        
        # Create a detailed prompt for text-to-image generation
        enhanced_prompt = f"""
        Create a completely new, unique, and authentic image based on this description: {prompt}
        
        Requirements:
        - Generate a brand new, photorealistic image
        - The image should be high-quality and professional
        - Focus on the food characteristics and visual elements described
        - Create an original composition that reflects the prompt
        - Make it suitable for professional advertising/marketing use
        - Ensure the image is visually compelling and appetizing
        - Pay special attention to food presentation, lighting, and composition
        - Use professional food photography techniques
        - The image should be completely original and not based on any existing image
        """
        
        response = client.models.generate_content(
            model=settings.GEMINI_IMAGE_MODEL,
            contents=[enhanced_prompt],
        )
        
        # Process the response
        generated_image_data = None
        response_text = ""
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                response_text += part.text
            elif part.inline_data is not None:
                generated_image_data = part.inline_data.data
        
        if not generated_image_data:
            raise HTTPException(status_code=500, detail="No image generated by Gemini")
        
        # Convert generated image to base64 for frontend
        generated_image = Image.open(BytesIO(generated_image_data))
        
        # Save generated image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_generated:
            generated_image.save(temp_generated.name, 'PNG')
            generated_image_path = temp_generated.name
        
        try:
            # Read the generated image and convert to base64
            with open(generated_image_path, 'rb') as f:
                generated_image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Return the generated image as base64 data URL
            generated_image_url = f"data:image/png;base64,{generated_image_base64}"
            
            return JSONResponse(content={
                "success": True,
                "generated_image": generated_image_url,
                "response_text": response_text,
                "message": "New image generated successfully from text prompt"
            })
            
        finally:
            # Clean up temporary files
            if os.path.exists(generated_image_path):
                os.unlink(generated_image_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image from text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.post("/api/generateFoodImage")
async def generate_food_image(prompt: str = Form(...)):
    """
    Generate a unique, authentic food image using text-to-image generation
    This is the recommended endpoint for creating food images without text overlay
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client not available")
    
    try:
        # Use the enhanced food-specific prompt function
        enhanced_prompt = create_food_image_prompt(prompt)
        logger.info(f"Generating unique food image with enhanced prompt")
        
        # Generate image using text-to-image (no uploaded image)
        response = client.models.generate_content(
            model=settings.GEMINI_IMAGE_MODEL,
            contents=[enhanced_prompt],
        )
        
        # Process the response
        generated_image_data = None
        response_text = ""
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                response_text += part.text
            elif part.inline_data is not None:
                generated_image_data = part.inline_data.data
        
        if not generated_image_data:
            raise HTTPException(status_code=500, detail="No image generated by Gemini")
        
        # Convert generated image to base64 for frontend
        generated_image = Image.open(BytesIO(generated_image_data))
        
        # Save generated image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_generated:
            generated_image.save(temp_generated.name, 'PNG')
            generated_image_path = temp_generated.name
        
        try:
            # Read the generated image and convert to base64
            with open(generated_image_path, 'rb') as f:
                generated_image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Return the generated image as base64 data URL
            generated_image_url = f"data:image/png;base64,{generated_image_base64}"
            
            return JSONResponse(content={
                "success": True,
                "generated_image": generated_image_url,
                "response_text": response_text,
                "message": "Unique food image generated successfully"
            })
            
        finally:
            # Clean up temporary files
            if os.path.exists(generated_image_path):
                os.unlink(generated_image_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating food image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Food image generation failed: {str(e)}")

@app.post("/api/generateText")
async def generate_text(prompt: str = Form(...)):
    """
    Generate text using Google Gemini (fallback when no image is provided)
    """
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client not available")
    
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_TEXT_MODEL,
            contents=[prompt],
        )
        
        response_text = ""
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                response_text += part.text
        
        return JSONResponse(content={
            "success": True,
            "generated_text": response_text,
            "message": "Text generated successfully"
        })
        
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
