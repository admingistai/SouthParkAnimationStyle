#!/usr/bin/env python3
"""
Test script for Nutcracker-style animation
"""

import sys
import os
sys.path.append('backend')

from backend.core.animator import TalkingHeadAnimator
import cv2
import numpy as np

def create_test_face():
    """Create a simple test face image"""
    
    # Create a simple face image
    width, height = 400, 500
    face_img = np.zeros((height, width, 4), dtype=np.uint8)
    face_img[:, :] = [255, 255, 255, 0]  # Transparent background
    
    # Draw face oval
    center_x = width // 2
    center_y = height // 2 - 50
    face_width = 180
    face_height = 240
    
    # Face color (light skin tone)
    face_color = [255, 220, 177, 255]
    cv2.ellipse(face_img, (center_x, center_y), (face_width//2, face_height//2), 
                0, 0, 360, face_color, -1)
    
    # Draw eyes
    eye_y = center_y - 40
    eye_spacing = 50
    eye_color = [0, 0, 0, 255]
    cv2.circle(face_img, (center_x - eye_spacing//2, eye_y), 15, eye_color, -1)
    cv2.circle(face_img, (center_x + eye_spacing//2, eye_y), 15, eye_color, -1)
    
    # Draw nose
    nose_y = center_y + 10
    cv2.ellipse(face_img, (center_x, nose_y), (10, 15), 0, 0, 360, [200, 180, 160, 255], -1)
    
    # Draw mouth region (will be extracted for jaw)
    mouth_y = center_y + 60
    mouth_width = 80
    mouth_height = 60
    
    # Draw lips
    cv2.ellipse(face_img, (center_x, mouth_y), (mouth_width//2, 15), 0, 0, 180, [200, 100, 100, 255], -1)
    cv2.ellipse(face_img, (center_x, mouth_y + 10), (mouth_width//2, 10), 0, 180, 360, [200, 100, 100, 255], -1)
    
    # Draw chin
    chin_y = mouth_y + 40
    cv2.ellipse(face_img, (center_x, chin_y), (60, 20), 0, 0, 180, face_color, -1)
    
    # Add face outline
    cv2.ellipse(face_img, (center_x, center_y), (face_width//2, face_height//2), 
                0, 0, 360, [0, 0, 0, 255], 3)
    
    return face_img

def test_nutcracker_animation():
    """Test the nutcracker animation style"""
    
    print("=== Testing Nutcracker Animation Style ===")
    
    # Create test directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Create test face
    test_face = create_test_face()
    test_face_path = "temp/test_nutcracker_face.png"
    cv2.imwrite(test_face_path, cv2.cvtColor(test_face, cv2.COLOR_RGBA2BGRA))
    print(f"Created test face: {test_face_path}")
    
    # Check if we have a test audio file
    test_audio_path = "test_samples/test_audio.wav"
    if not os.path.exists(test_audio_path):
        print(f"\nPlease provide a test audio file: {test_audio_path}")
        print("You can use any WAV file with speech")
        return
    
    # Create animator
    animator = TalkingHeadAnimator()
    
    try:
        # Create animation with nutcracker style
        print("\nCreating nutcracker animation...")
        output_video = animator.create_animation(
            image_path=test_face_path,
            audio_path=test_audio_path,
            style='nutcracker'
        )
        
        print(f"\n✅ Nutcracker animation created successfully!")
        print(f"Output video: {output_video}")
        
        # Get video info
        cap = cv2.VideoCapture(output_video)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        
        print(f"\nVideo info:")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Frames: {frame_count}")
        print(f"  FPS: {fps}")
        
    except Exception as e:
        print(f"\n❌ Error creating animation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nutcracker_animation()