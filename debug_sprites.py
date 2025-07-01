#!/usr/bin/env python3
"""
Debug script to test mouth sprite application
Creates test frames with different visemes to verify sprites are working
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.mouth_sprite_manager import MouthSpriteManager
from core.image_processor import ImageProcessor
import cv2

def create_sprite_test_grid():
    """Create a test grid showing all mouth sprites on a character"""
    
    print("Creating sprite test grid...")
    
    # Initialize components
    sprite_manager = MouthSpriteManager()
    image_processor = ImageProcessor()
    
    # Load test character
    character_path = "temp/StanMarsh.png"
    if not os.path.exists(character_path):
        print(f"Character image not found: {character_path}")
        return
    
    # Prepare character for sprites
    character_data = image_processor.prepare_character_for_sprites(character_path)
    
    # Get all available visemes
    visemes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'X']
    
    print(f"Testing {len(visemes)} visemes...")
    
    # Create test frame for each viseme
    for i, viseme in enumerate(visemes):
        print(f"Creating test frame for viseme {viseme}")
        
        # Create frame with this viseme
        frame = image_processor.composite_sprite_frame(character_data, viseme, debug=True)
        
        # Save test frame
        output_path = f"temp/sprite_test_{viseme}.png"
        
        # Convert RGBA to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        cv2.imwrite(output_path, frame_bgr)
        
        print(f"Saved: {output_path}")
    
    print(f"\n✅ Created {len(visemes)} test frames in temp/ directory")
    print("Check the sprite_test_*.png files to see mouth shape variations")

if __name__ == "__main__":
    create_sprite_test_grid()