# FeediaAI Backend Setup

## Prerequisites
1. Node.js 22 or higher
2. Firebase CLI installed
3. OpenAI API key

## Setup Instructions

### 1. Install Dependencies
```bash
cd functions
npm install
```

### 2. Set Environment Variables
Create a `.env` file in the functions directory with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Deploy Functions
```bash
firebase deploy --only functions
```

## API Endpoints

### Generate Image (GPT-4 Vision + DALL-E)
- **URL**: `https://us-central1-feediaai.cloudfunctions.net/generateImage`
- **Method**: POST
- **Body**: 
  ```json
  {
    "imageBase64": "base64_encoded_image",
    "prompt": "description of what to create"
  }
  ```

### Generate DALL-E Image
- **URL**: `https://us-central1-feediaai.cloudfunctions.net/generateDALLEImage`
- **Method**: POST
- **Body**:
  ```json
  {
    "prompt": "description of the image to generate"
  }
  ```

## Usage
The frontend will automatically call these endpoints when users upload images and provide prompts for promotional poster generation.
