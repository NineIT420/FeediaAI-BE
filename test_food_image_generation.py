#!/usr/bin/env python3
"""
Test script for the new food image generation functionality
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image

def test_food_image_generation():
    """Test the new food image generation endpoint"""
    
    # Test cases for different types of food
    test_cases = [
        "A delicious margherita pizza with fresh basil and mozzarella",
        "A gourmet burger with crispy bacon and melted cheese",
        "A fresh Caesar salad with croutons and parmesan",
        "A chocolate lava cake with vanilla ice cream",
        "A grilled salmon with roasted vegetables"
    ]
    
    base_url = "http://localhost:8000"
    
    print("Testing Food Image Generation API")
    print("=" * 50)
    
    for i, prompt in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {prompt}")
        print("-" * 30)
        
        try:
            # Test the new food image generation endpoint
            response = requests.post(
                f"{base_url}/api/generateFoodImage",
                data={"prompt": prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Success: Food image generated")
                    print(f"   Message: {result.get('message')}")
                    
                    # Decode and save the image for inspection
                    image_data = result.get("generated_image", "")
                    if image_data.startswith("data:image"):
                        # Extract base64 data
                        base64_data = image_data.split(",")[1]
                        image_bytes = base64.b64decode(base64_data)
                        
                        # Save image
                        image = Image.open(BytesIO(image_bytes))
                        filename = f"test_food_image_{i}.png"
                        image.save(filename)
                        print(f"   Image saved as: {filename}")
                        print(f"   Image size: {image.size}")
                else:
                    print("❌ Failed: No image generated")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

def test_prompt_enhancement():
    """Test the prompt enhancement function"""
    from main import create_food_image_prompt
    
    test_prompts = [
        "pizza",
        "chocolate cake",
        "grilled steak",
        "fresh salad"
    ]
    
    print("\nTesting Prompt Enhancement")
    print("=" * 30)
    
    for prompt in test_prompts:
        enhanced = create_food_image_prompt(prompt)
        print(f"\nOriginal: {prompt}")
        print(f"Enhanced length: {len(enhanced)} characters")
        print(f"Enhanced preview: {enhanced[:200]}...")

if __name__ == "__main__":
    print("Food Image Generation Test Suite")
    print("=" * 50)
    
    # Test prompt enhancement first
    test_prompt_enhancement()
    
    # Test API endpoints
    test_food_image_generation()
