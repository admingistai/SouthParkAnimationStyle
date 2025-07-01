#!/usr/bin/env python3
"""
Test script to verify manual mouth coordinate functionality through web API
"""

import requests
import os

def test_manual_coordinates():
    """Test manual mouth positioning through the Flask API"""
    
    # API endpoint
    api_url = "http://localhost:5000/upload"
    
    # Files to upload
    image_path = "temp/StanMarsh.png"
    audio_path = "temp/EmojiGhostVoice.mp3"
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return False
        
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    # Test manual coordinates
    manual_x, manual_y = 150, 120
    
    print(f"🧪 Testing manual mouth coordinates: ({manual_x}, {manual_y})")
    
    # Prepare files and form data
    files = {
        'image': open(image_path, 'rb'),
        'audio': open(audio_path, 'rb')
    }
    
    form_data = {
        'style': 'standard',
        'mouth_x': str(manual_x),
        'mouth_y': str(manual_y)
    }
    
    try:
        print("📤 Sending request to Flask API...")
        response = requests.post(api_url, files=files, data=form_data, timeout=300)
        
        # Close file handles
        files['image'].close()
        files['audio'].close()
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Manual coordinates test PASSED!")
                print(f"🎬 Video URL: {result.get('video_url')}")
                return True
            else:
                print(f"❌ API returned error: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server")
        print("💡 Make sure the server is running: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing manual mouth coordinate functionality...")
    success = test_manual_coordinates()
    if success:
        print("\n🎉 Manual coordinates are working correctly!")
    else:
        print("\n💥 Manual coordinates test failed!")