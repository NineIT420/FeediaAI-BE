#!/usr/bin/env python3
"""
Test script for FeediaAI Backend API
"""

import requests
import json
import os
from PIL import Image
import io

# Configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_image.jpg"

def create_test_image():
    """Create a simple test image"""
    # Create a simple 100x100 red square
    img = Image.new('RGB', (100, 100), color='red')
    img.save(TEST_IMAGE_PATH)
    print(f"✅ Created test image: {TEST_IMAGE_PATH}")

def test_health_endpoints():
    """Test health check endpoints"""
    print("\n🔍 Testing health endpoints...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        print(f"GET / - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        print(f"GET /health - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing health endpoints: {e}")
        return False
    
    return True

def test_image_generation():
    """Test image generation endpoint"""
    print("\n🎨 Testing image generation...")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        create_test_image()
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'uploaded_image': f}
            data = {'prompt': 'Create a beautiful sunset landscape'}
            
            response = requests.post(f"{BASE_URL}/api/generativeImage", files=files, data=data)
            
        print(f"POST /api/generativeImage - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image generation successful!")
            print(f"Response text: {result.get('response_text', 'No text response')}")
            print(f"Generated image URL length: {len(result.get('generated_image', ''))}")
            
            # Save generated image
            if 'generated_image' in result:
                generated_data = result['generated_image']
                if generated_data.startswith('data:image'):
                    # Extract base64 data
                    base64_data = generated_data.split(',')[1]
                    import base64
                    image_data = base64.b64decode(base64_data)
                    
                    with open('generated_test_image.png', 'wb') as f:
                        f.write(image_data)
                    print("✅ Generated image saved as 'generated_test_image.png'")
        else:
            print(f"❌ Image generation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing image generation: {e}")

def test_text_generation():
    """Test text generation endpoint"""
    print("\n📝 Testing text generation...")
    
    try:
        data = {'prompt': 'Write a short poem about artificial intelligence'}
        response = requests.post(f"{BASE_URL}/api/generateText", data=data)
        
        print(f"POST /api/generateText - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Text generation successful!")
            print(f"Generated text: {result.get('generated_text', 'No text generated')}")
        else:
            print(f"❌ Text generation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing text generation: {e}")

def cleanup():
    """Clean up test files"""
    print("\n🧹 Cleaning up...")
    if os.path.exists(TEST_IMAGE_PATH):
        os.remove(TEST_IMAGE_PATH)
        print(f"✅ Removed {TEST_IMAGE_PATH}")

def main():
    """Run all tests"""
    print("🚀 FeediaAI Backend API Test Suite")
    print("=" * 50)
    
    # Test health endpoints first
    if not test_health_endpoints():
        print("\n❌ Health check failed. Please start the server first.")
        print("Run: python main.py")
        return
    
    # Test image generation
    test_image_generation()
    
    # Test text generation
    test_text_generation()
    
    # Cleanup
    cleanup()
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    main()
