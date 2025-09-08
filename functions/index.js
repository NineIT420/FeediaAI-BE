const {setGlobalOptions} = require("firebase-functions");
const {onRequest} = require("firebase-functions/https");
const logger = require("firebase-functions/logger");
const functions = require("firebase-functions");
const OpenAI = require("openai");
const cors = require("cors")({ origin: true });

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || functions.config().openai?.api_key,
});

setGlobalOptions({ maxInstances: 10 });

// Image generation endpoint
exports.generateImage = onRequest(async (req, res) => {
  return cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
      const { imageBase64, prompt } = req.body;

      if (!imageBase64 || !prompt) {
        return res.status(400).json({ 
          error: 'Missing required fields: imageBase64 and prompt' 
        });
      }

      logger.info('Processing image generation request', {
        promptLength: prompt.length,
        imageBase64Length: imageBase64.length
      });

      // Validate image size (OpenAI has limits)
      const imageBuffer = Buffer.from(imageBase64, 'base64');
      const imageSizeMB = imageBuffer.length / (1024 * 1024);
      
      if (imageSizeMB > 20) {
        return res.status(400).json({
          error: 'Image too large. Please use an image smaller than 20MB.'
        });
      }

      logger.info('Image validation passed', {
        imageSizeMB: imageSizeMB.toFixed(2)
      });

      // Enhanced prompt for better promotional image generation
      const enhancedPrompt = prompt.trim() || "Create a professional promotional poster";
      
      // Call OpenAI GPT-4 Vision API with enhanced analysis
      let generatedText;
      try {
        const response = await openai.chat.completions.create({
          model: "gpt-4o",
          messages: [
            {
              role: "system",
              content: "You are a professional marketing expert and graphic designer. Analyze the provided image and create detailed promotional content descriptions that will be used to generate high-quality marketing materials. Focus on visual elements, brand appeal, target audience, and marketing effectiveness."
            },
            {
              role: "user",
              content: [
                {
                  type: "text",
                  text: `Analyze this image and create a comprehensive promotional strategy description. 

User Request: "${enhancedPrompt}"

Please provide:
1. Detailed visual analysis of the image (colors, composition, subjects, mood)
2. Target audience identification
3. Marketing angle and key selling points
4. Visual style recommendations for promotional materials
5. Specific design elements that would work well in promotional content
6. Brand positioning suggestions

Focus on creating content that will generate compelling, professional promotional images.`
                },
                {
                  type: "image_url",
                  image_url: {
                    url: `data:image/jpeg;base64,${imageBase64}`
                  }
                }
              ]
            }
          ],
          max_tokens: 1500
        });

        generatedText = response.choices[0].message.content;
      } catch (visionError) {
        logger.warn('Vision API failed, using fallback', {
          error: visionError.message
        });
        // Enhanced fallback: generate description based on prompt only
        const fallbackResponse = await openai.chat.completions.create({
          model: "gpt-4o",
          messages: [
            {
              role: "system",
              content: "You are a professional marketing expert. Create detailed promotional content descriptions for marketing materials."
            },
            {
              role: "user",
              content: `Based on this request: "${enhancedPrompt}", create a comprehensive description for generating a professional promotional poster. 

                        Include:
                        - Visual style recommendations
                        - Target audience analysis
                        - Marketing angle and key selling points
                        - Design elements and layout suggestions
                        - Color scheme recommendations
                        - Brand positioning ideas

                        Make it detailed and actionable for creating compelling promotional materials.`
            }
          ],
          max_tokens: 1200
        });
        generatedText = fallbackResponse.choices[0].message.content;
      }

      logger.info('Successfully generated description', {
        descriptionLength: generatedText.length
      });

      // For now, we'll return the text description
      // In a real implementation, you might want to use DALL-E or another image generation model
      res.json({
        success: true,
        description: generatedText,
        originalImage: imageBase64
      });

    } catch (error) {
      logger.error('Error generating image:', {
        error: error.message,
        stack: error.stack,
        name: error.name
      });
      
      let statusCode = 500;
      let errorMessage = 'Failed to generate image';
      
      if (error.message.includes('quota') || error.message.includes('billing')) {
        statusCode = 429;
        errorMessage = 'API quota exceeded. Please check your OpenAI billing settings.';
      } else if (error.message.includes('429')) {
        statusCode = 429;
        errorMessage = 'Rate limit exceeded. Please try again later.';
      } else if (error.message.includes('401')) {
        statusCode = 401;
        errorMessage = 'Invalid API key. Please check your OpenAI configuration.';
      }
      
      res.status(statusCode).json({ 
        error: errorMessage,
        details: error.message 
      });
    }
  });
});

// Enhanced DALL-E image generation endpoint for promotional content
exports.generateDALLEImage = onRequest(async (req, res) => {
  return cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
      const { prompt, style = 'modern', aspectRatio = 'square' } = req.body;

      if (!prompt) {
        return res.status(400).json({ 
          error: 'Missing required field: prompt' 
        });
      }

      logger.info('Processing enhanced DALL-E image generation request', {
        promptLength: prompt.length,
        style: style,
        aspectRatio: aspectRatio
      });

      // Enhanced prompt with style and aspect ratio considerations
      const getStyleEnhancement = (style) => {
        const styleEnhancements = {
          modern: "Modern, minimalist design with clean lines, contemporary typography, sophisticated color palette, professional photography style",
          vibrant: "Bold, energetic design with bright colors, dynamic layouts, eye-catching visual elements, high contrast, social media optimized",
          professional: "Corporate-style design with elegant typography, professional color scheme, business-appropriate aesthetics, clean and trustworthy",
          creative: "Artistic, creative design with unique visual elements, creative typography, innovative layout, artistic photography style",
          social: "Social media optimized design with Instagram-friendly colors, trendy elements, viral-worthy appeal, mobile-first design"
        };
        return styleEnhancements[style] || styleEnhancements.modern;
      };

      const getAspectRatio = (ratio) => {
        const ratios = {
          square: "1024x1024",
          portrait: "1024x1792", // Instagram Stories
          landscape: "1792x1024", // Wide format
          instagram: "1080x1080", // Instagram post
          story: "1080x1920" // Instagram Stories
        };
        return ratios[ratio] || ratios.square;
      };

      // Create enhanced prompt for better promotional image generation
      const enhancedPrompt = `Create a professional, high-quality promotional poster with the following specifications:

${prompt}

Style Requirements: ${getStyleEnhancement(style)}

Technical Specifications:
- Professional photography or illustration quality
- High resolution and sharp details
- Vibrant, eye-catching colors suitable for marketing
- Professional marketing appeal and brand positioning
- High contrast for readability and social media visibility
- Modern design trends and contemporary aesthetics
- Suitable for business marketing and advertising campaigns
- Optimized for social media platforms and digital marketing
- Include space for text overlays and branding elements
- Professional composition and visual hierarchy

Make it visually stunning, marketing-ready, and immediately usable for promotional campaigns.`;

      // Call OpenAI GPT-Image-1 API with enhanced parameters
      const response = await openai.images.generate({
        model: "gpt-image-1",
        prompt: enhancedPrompt,
        n: 1,
        size: getAspectRatio(aspectRatio),
        quality: "hd", // Use high quality for promotional content
        style: "natural" // More natural, professional look
      });

      const imageUrl = response.data[0].url;

      logger.info('Successfully generated enhanced GPT-Image-1 promotional image', {
        imageUrl: imageUrl,
        style: style,
        aspectRatio: aspectRatio
      });

      res.json({
        success: true,
        imageUrl: imageUrl,
        prompt: enhancedPrompt,
        originalPrompt: prompt,
        style: style,
        aspectRatio: aspectRatio,
        metadata: {
          model: "gpt-image-1",
          quality: "hd",
          style: "natural",
          generatedAt: new Date().toISOString()
        }
      });

    } catch (error) {
      logger.error('Error generating enhanced GPT-Image-1 image:', {
        error: error.message,
        stack: error.stack,
        name: error.name
      });
      
      let statusCode = 500;
      let errorMessage = 'Failed to generate promotional image';
      
      if (error.message.includes('quota') || error.message.includes('billing')) {
        statusCode = 429;
        errorMessage = 'GPT-Image-1 API quota exceeded. Please check your OpenAI billing settings.';
      } else if (error.message.includes('429')) {
        statusCode = 429;
        errorMessage = 'GPT-Image-1 rate limit exceeded. Please try again later.';
      } else if (error.message.includes('401')) {
        statusCode = 401;
        errorMessage = 'Invalid API key for GPT-Image-1. Please check your OpenAI configuration.';
      } else if (error.message.includes('content_policy')) {
        statusCode = 400;
        errorMessage = 'Content policy violation. Please adjust your prompt and try again.';
      }
      
      res.status(statusCode).json({ 
        error: errorMessage,
        details: error.message 
      });
    }
  });
});

// Batch promotional image generation endpoint
exports.generateBatchPromotionalImages = onRequest(async (req, res) => {
  return cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
      const { imageBase64, styles = ['modern', 'vibrant', 'professional'], aspectRatio = 'square' } = req.body;

      if (!imageBase64) {
        return res.status(400).json({ 
          error: 'Missing required field: imageBase64' 
        });
      }

      logger.info('Processing batch promotional image generation', {
        stylesCount: styles.length,
        aspectRatio: aspectRatio
      });

      // First, analyze the image
      const analysisResponse = await openai.chat.completions.create({
        model: "gpt-4o",
        messages: [
          {
            role: "system",
            content: "You are a professional marketing expert. Analyze images and create promotional content descriptions."
          },
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Analyze this image and create a comprehensive promotional strategy description that can be used to generate multiple promotional images in different styles."
              },
              {
                type: "image_url",
                image_url: {
                  url: `data:image/jpeg;base64,${imageBase64}`
                }
              }
            ]
          }
        ],
        max_tokens: 1000
      });

      const analysis = analysisResponse.choices[0].message.content;

      // Generate images for each style
      const imagePromises = styles.map(async (style) => {
        try {
          const response = await openai.images.generate({
            model: "gpt-image-1",
            prompt: `Create a professional promotional poster based on this analysis: ${analysis}. Style: ${style}`,
            n: 1,
            size: aspectRatio === 'square' ? "1024x1024" : aspectRatio === 'portrait' ? "1024x1792" : "1792x1024",
            quality: "hd",
            style: "natural"
          });

          return {
            style: style,
            imageUrl: response.data[0].url,
            success: true
          };
        } catch (error) {
          logger.warn(`Failed to generate image for style ${style}:`, error.message);
          return {
            style: style,
            error: error.message,
            success: false
          };
        }
      });

      const results = await Promise.all(imagePromises);
      const successfulImages = results.filter(r => r.success);
      const failedImages = results.filter(r => !r.success);

      logger.info('Batch generation completed', {
        successful: successfulImages.length,
        failed: failedImages.length
      });

      res.json({
        success: true,
        analysis: analysis,
        images: successfulImages,
        failed: failedImages,
        totalGenerated: successfulImages.length,
        metadata: {
          aspectRatio: aspectRatio,
          generatedAt: new Date().toISOString()
        }
      });

    } catch (error) {
      logger.error('Error in batch promotional image generation:', {
        error: error.message,
        stack: error.stack
      });
      
      res.status(500).json({ 
        error: 'Failed to generate batch promotional images',
        details: error.message 
      });
    }
  });
});
