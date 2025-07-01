#!/usr/bin/env python3
"""
Visualize mouth detection results
Creates an image showing where the mouth anchor is detected
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from core.image_processor import ImageProcessor
import cv2
import numpy as np

def visualize_mouth_detection():
    """Create a visualization showing mouth detection results"""
    
    print("Creating mouth detection visualization...")
    
    # Initialize components
    image_processor = ImageProcessor()
    
    # Load test character
    character_path = "temp/StanMarsh.png"
    if not os.path.exists(character_path):
        print(f"Character image not found: {character_path}")
        return
    
    # Prepare character for sprites (this runs the detection)
    character_data = image_processor.prepare_character_for_sprites(character_path)
    
    # Get the detected mouth position
    mouth_anchor = character_data['mouth_anchor']
    sprite_size = character_data['sprite_size']
    
    print(f"Detected mouth anchor: {mouth_anchor}")
    print(f"Sprite size: {sprite_size}")
    
    # Load the base image
    base_image = character_data['base_image'].copy()
    
    # Draw mouth anchor and sprite area
    mouth_x, mouth_y = mouth_anchor
    sprite_w, sprite_h = sprite_size
    
    # Calculate sprite bounds
    sprite_x1 = mouth_x - sprite_w // 2
    sprite_y1 = mouth_y - sprite_h // 2
    sprite_x2 = sprite_x1 + sprite_w
    sprite_y2 = sprite_y1 + sprite_h
    
    # Draw crosshair at mouth anchor (red)
    cv2.line(base_image, (mouth_x - 20, mouth_y), (mouth_x + 20, mouth_y), (255, 0, 0, 255), 2)
    cv2.line(base_image, (mouth_x, mouth_y - 20), (mouth_x, mouth_y + 20), (255, 0, 0, 255), 2)
    
    # Draw sprite area rectangle (green)
    cv2.rectangle(base_image, (sprite_x1, sprite_y1), (sprite_x2, sprite_y2), (0, 255, 0, 255), 2)
    
    # Add text labels
    cv2.putText(base_image, f"Mouth: ({mouth_x}, {mouth_y})", 
                (mouth_x + 25, mouth_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0, 255), 1)
    cv2.putText(base_image, f"Sprite: {sprite_w}x{sprite_h}", 
                (sprite_x1, sprite_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0, 255), 1)
    
    # Save visualization
    output_path = "temp/mouth_detection_visualization.png"
    
    # Convert RGBA to BGR for OpenCV
    frame_bgr = cv2.cvtColor(base_image, cv2.COLOR_RGBA2BGR)
    cv2.imwrite(output_path, frame_bgr)
    
    print(f"✅ Saved mouth detection visualization: {output_path}")
    print("Red crosshair = detected mouth position")
    print("Green rectangle = sprite placement area")

if __name__ == "__main__":
    visualize_mouth_detection()