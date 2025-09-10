# FeediaAI Backend Deployment Guide

## Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp env.example .env

# Edit .env file and add your Google Gemini API key
nano .env
```

### 2. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Server
```bash
# Option 1: Use the startup script
./start.sh

# Option 2: Run directly
python main.py

# Option 3: Use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker Deployment

### 1. Build and Run with Docker
```bash
# Build the image
docker build -t feedia-ai-backend .

# Run the container
docker run -p 8000:8000 --env-file .env feedia-ai-backend
```

### 2. Using Docker Compose
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

## Production Deployment

### 1. Environment Variables
Set these environment variables in production:
```bash
GOOGLE_API_KEY=your_actual_api_key
HOST=0.0.0.0
PORT=8000
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Using a Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Using PM2 (Process Manager)
```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'feedia-ai-backend',
    script: 'uvicorn',
    args: 'main:app --host 0.0.0.0 --port 8000',
    cwd: '/path/to/FeediaAI-BE',
    env: {
      GOOGLE_API_KEY: 'your_api_key',
      HOST: '0.0.0.0',
      PORT: 8000,
      DEBUG: 'False'
    }
  }]
}
EOF

# Start the application
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup
```

## Testing

### 1. Run Test Suite
```bash
python test_api.py
```

### 2. Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Test image generation
curl -X POST "http://localhost:8000/api/generativeImage" \
  -F "uploaded_image=@test_image.jpg" \
  -F "prompt=Create a beautiful sunset"
```

## Monitoring

### 1. Health Checks
- Basic health: `GET /`
- Detailed health: `GET /health`

### 2. Logs
The application logs important events and errors. Check console output or configure logging to files.

### 3. API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

### Common Issues

1. **"Gemini client not available"**
   - Check GOOGLE_API_KEY is set correctly
   - Verify API key has proper permissions

2. **CORS errors**
   - Update ALLOWED_ORIGINS in .env
   - Ensure frontend URL is included

3. **Image generation fails**
   - Check image file size and format
   - Verify prompt is appropriate
   - Check Gemini API quotas

4. **Port already in use**
   - Change PORT in .env file
   - Kill existing process: `lsof -ti:8000 | xargs kill -9`

### Performance Optimization

1. **Image Processing**
   - Images are automatically resized to 2048px max
   - JPEG quality set to 95% for balance of quality/size

2. **Memory Management**
   - Temporary files are cleaned up automatically
   - Consider increasing server memory for high traffic

3. **Caching**
   - Consider adding Redis for response caching
   - Implement rate limiting for production use

## Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secret management
   - Rotate keys regularly

2. **Input Validation**
   - File type and size validation implemented
   - Consider adding more strict validation

3. **Rate Limiting**
   - Implement rate limiting for production
   - Consider using FastAPI's built-in rate limiting

4. **CORS Configuration**
   - Restrict ALLOWED_ORIGINS in production
   - Use specific domains instead of wildcards
