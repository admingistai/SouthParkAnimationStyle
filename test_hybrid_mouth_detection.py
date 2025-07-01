#!/usr/bin/env python3
"""
Test hybrid mouth detection with both cartoon and realistic faces
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.image_processor import ImageProcessor
from core.mouth_sprite_manager import MouthSpriteManager
import cv2
import numpy as np
from PIL import Image


def test_mouth_detection(image_path, expected_type):
    """Test mouth detection on a specific image"""
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print(f"Expected type: {expected_type}")
    print(f"{'='*60}")
    
    # Initialize components
    mouth_manager = MouthSpriteManager()
    
    # Load image
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    # Load with PIL then convert to numpy array
    pil_image = Image.open(image_path).convert('RGBA')
    image_array = np.array(pil_image)
    
    print(f"Image shape: {image_array.shape}")
    
    # Detect face type
    face_type = mouth_manager.detect_face_type(image_array)
    print(f"\n🎭 Detected face type: {face_type}")
    print(f"✅ Face type detection: {'CORRECT' if face_type == expected_type else 'INCORRECT'}")
    
    # Find mouth position
    mouth_position = mouth_manager.find_optimal_mouth_position(image_array)
    print(f"\n👄 Detected mouth position: {mouth_position}")
    
    # Create visualization
    vis_image = image_array.copy()
    mouth_x, mouth_y = mouth_position
    
    # Draw crosshair at mouth position
    cv2.line(vis_image, (mouth_x - 20, mouth_y), (mouth_x + 20, mouth_y), (255, 0, 0, 255), 2)
    cv2.line(vis_image, (mouth_x, mouth_y - 20), (mouth_x, mouth_y + 20), (255, 0, 0, 255), 2)
    
    # Add text
    cv2.putText(vis_image, f"Type: {face_type}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0, 255), 2)
    cv2.putText(vis_image, f"Mouth: ({mouth_x}, {mouth_y})", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0, 255), 2)
    
    # Save visualization
    output_path = f"temp/hybrid_detection_{os.path.basename(image_path)}"
    cv2.imwrite(output_path, cv2.cvtColor(vis_image, cv2.COLOR_RGBA2BGR))
    print(f"\n📸 Saved visualization: {output_path}")
    
    return {
        'image': image_path,
        'detected_type': face_type,
        'expected_type': expected_type,
        'mouth_position': mouth_position,
        'success': face_type == expected_type
    }


def main():
    """Run tests on both cartoon and realistic faces"""
    print("🧪 Testing Hybrid Mouth Detection System")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        ("temp/StanMarsh.png", "cartoon"),
        ("temp/Screenshot_2025-06-30_at_10.35.40_AM.png", "realistic")  # Saddam image
    ]
    
    results = []
    
    for image_path, expected_type in test_cases:
        result = test_mouth_detection(image_path, expected_type)
        if result:
            results.append(result)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {os.path.basename(result['image'])}: "
              f"Expected {result['expected_type']}, Got {result['detected_type']}, "
              f"Mouth at {result['mouth_position']}")
    
    print(f"\n🎯 Overall: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Hybrid detection is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the detection logic.")
    
    print("\n💡 Check the visualization images in the temp/ folder to see mouth positioning.")


if __name__ == "__main__":
    main()