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


// Direct image generation endpoint (no uploaded image required)
exports.generateDirectImage = onRequest(async (req, res) => {
  return cors(req, res, async () => {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
      const { prompt, style = 'natural', aspectRatio = 'square' } = req.body;

      if (!prompt) {
        return res.status(400).json({ 
          error: 'Missing required field: prompt' 
        });
      }

      logger.info('Processing direct image generation request', {
        promptLength: prompt.length,
        style: style,
        aspectRatio: aspectRatio
      });

      // Get aspect ratio dimensions
      const getAspectRatio = (ratio) => {
        const ratios = {
          square: "1024x1024",
          portrait: "1024x1792",
          landscape: "1792x1024",
          instagram: "1080x1080",
          story: "1080x1920"
        };
        return ratios[ratio] || ratios.square;
      };

      // Create enhanced prompt for realistic image generation
      const enhancedPrompt = `Create a realistic, high-quality image with the following specifications:

${prompt}

Technical Requirements:
- Photorealistic quality with sharp details
- Professional photography style
- Natural lighting and composition
- High resolution and clarity
- Realistic textures and materials
- Professional color grading
- Suitable for commercial use

Make it visually stunning and immediately usable for professional purposes.`;

      // Call OpenAI DALL-E 3 API
      const response = await openai.images.generate({
        model: "dall-e-3",
        prompt: enhancedPrompt,
        n: 1,
        size: getAspectRatio(aspectRatio),
        quality: "hd",
        style: style
      });

      const imageUrl = response.data[0].url;

      logger.info('Successfully generated direct DALL-E 3 image', {
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
          model: "dall-e-3",
          quality: "hd",
          style: style,
          generatedAt: new Date().toISOString()
        }
      });

    } catch (error) {
      logger.error('Error generating direct DALL-E 3 image:', {
        error: error.message,
        stack: error.stack,
        name: error.name
      });
      
      let statusCode = 500;
      let errorMessage = 'Failed to generate image';
      
      if (error.message.includes('quota') || error.message.includes('billing')) {
        statusCode = 429;
        errorMessage = 'DALL-E 3 API quota exceeded. Please check your OpenAI billing settings.';
      } else if (error.message.includes('429')) {
        statusCode = 429;
        errorMessage = 'DALL-E 3 rate limit exceeded. Please try again later.';
      } else if (error.message.includes('401')) {
        statusCode = 401;
        errorMessage = 'Invalid API key for DALL-E 3. Please check your OpenAI configuration.';
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

