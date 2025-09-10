"""
Configuration settings for FeediaAI Backend
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Server Configuration
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Image Processing
    MAX_IMAGE_SIZE = 2048  # Maximum width/height in pixels
    IMAGE_QUALITY = 95     # JPEG quality (1-100)
    
    # Gemini Model Configuration
    GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image-preview"
    GEMINI_TEXT_MODEL = "gemini-2.5-flash"
    
    # File Upload
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        if cls.GOOGLE_API_KEY == "your_google_api_key_here":
            raise ValueError("Please set a valid GOOGLE_API_KEY in your .env file")

# Create settings instance
settings = Settings()
