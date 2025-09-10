# FeediaAI Backend

A FastAPI-based backend service that integrates with Google Gemini AI to generate high-quality images from text prompts and uploaded images.

## Features

- 🎨 **AI Image Generation**: Uses Google Gemini 2.5 Flash model for image generation
- 📸 **Image Upload Support**: Accepts image uploads and processes them with AI
- 🔄 **CORS Enabled**: Ready for frontend integration
- 🛡️ **Error Handling**: Comprehensive error handling and validation
- 📝 **Text Generation**: Fallback text generation when no image is provided
- 🚀 **FastAPI**: Modern, fast web framework for building APIs

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FeediaAI-BE
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your Google Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

## Getting a Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Running the Server

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/` - Basic health check
- **GET** `/health` - Detailed health status including Gemini availability

### Image Generation

#### With Uploaded Image
- **POST** `/api/generativeImage`
  - **Body**: `multipart/form-data`
    - `uploaded_image`: Image file (optional)
    - `prompt`: Text prompt (required)
  - **Response**: Generated image as base64 data URL
  - **Note**: Creates a new image inspired by the uploaded image

#### Text-to-Image Only (Recommended for Unique Images)
- **POST** `/api/generateImageFromText`
  - **Body**: `application/x-www-form-urlencoded`
    - `prompt`: Text prompt (required)
  - **Response**: Generated image as base64 data URL
  - **Note**: Creates completely new, unique images without requiring an uploaded image

### Text Generation
- **POST** `/api/generateText`
  - **Body**: `application/x-www-form-urlencoded`
    - `prompt`: Text prompt (required)
  - **Response**: Generated text

## Example Usage

### Using curl
```bash
# Generate image with uploaded image
curl -X POST "http://localhost:8000/api/generativeImage" \
  -F "uploaded_image=@path/to/your/image.jpg" \
  -F "prompt=Create a picture of my cat eating a nano-banana in a fancy restaurant under the Gemini constellation"

# Generate completely new image from text only (recommended for unique images)
curl -X POST "http://localhost:8000/api/generateImageFromText" \
  -d "prompt=Create a beautiful, professional food photography of a gourmet burger with crispy fries, shot with professional lighting and composition"
```

### Using Python requests
```python
import requests

# Generate image with uploaded image
with open('image.jpg', 'rb') as f:
    files = {'uploaded_image': f}
    data = {'prompt': 'Your prompt here'}
    response = requests.post('http://localhost:8000/api/generativeImage', files=files, data=data)
    result = response.json()
    print(result['generated_image'])  # Base64 data URL

# Generate completely new image from text only (recommended for unique images)
data = {'prompt': 'Create a beautiful, professional food photography of a gourmet burger with crispy fries, shot with professional lighting and composition'}
response = requests.post('http://localhost:8000/api/generateImageFromText', data=data)
result = response.json()
print(result['generated_image'])  # Base64 data URL
```

## Frontend Integration

The backend is designed to work seamlessly with the provided React frontend. The frontend can use two approaches:

1. **With Image Upload**: Send image uploads and prompts to the `/api/generativeImage` endpoint
2. **Text-to-Image Only**: Send only text prompts to the `/api/generateImageFromText` endpoint for completely new, unique images

Both endpoints return generated images as base64 data URLs. For creating authentic, unique food images, the text-to-image endpoint (`/api/generateImageFromText`) is recommended as it generates completely new images rather than modifying existing ones.

### CORS Configuration

The backend includes CORS middleware that allows requests from any origin in development. For production, update the `ALLOWED_ORIGINS` in your `.env` file:

```
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400` - Bad Request (invalid file type, missing parameters)
- `500` - Internal Server Error (Gemini API issues, processing errors)

## Image Processing

- Images are automatically resized if they exceed 2048px in width or height
- Images are converted to RGB format for compatibility
- Temporary files are automatically cleaned up after processing

## Development

### Project Structure
```
FeediaAI-BE/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
└── README.md           # This file
```

### Adding New Features

1. Add new endpoints in `main.py`
2. Update `requirements.txt` if new dependencies are needed
3. Update this README with new endpoint documentation

## Troubleshooting

### Common Issues

1. **"Gemini client not available"**
   - Check that your `GOOGLE_API_KEY` is set correctly
   - Verify the API key is valid and has the necessary permissions

2. **"No image generated by Gemini"**
   - The prompt might not be suitable for image generation
   - Try a different prompt or check the uploaded image

3. **CORS errors in frontend**
   - Ensure the backend is running on the correct port
   - Check that the frontend is making requests to the correct URL

### Logs

The application logs important events and errors. Check the console output for debugging information.

## License

This project is part of the FeediaAI application suite.
