import os
import cv2
import numpy as np
from PIL import Image
import subprocess
import json
import tempfile
from .phoneme_detector import PhonemeDetector
from .image_processor import ImageProcessor
from .video_renderer import VideoRenderer

class TalkingHeadAnimator:
    def __init__(self):
        self.phoneme_detector = PhonemeDetector()
        self.image_processor = ImageProcessor()
        self.video_renderer = VideoRenderer()
        
        # Mouth position mapping - South Park Canadian translation style
        # Now includes base backward tilt - left/right tilt is added randomly
        self.mouth_positions = {
            'A': {'top_y': 0, 'top_x': 0, 'bottom_y': 0, 'tilt': 0},      # Closed mouth
            'B': {'top_y': -15, 'top_x': 5, 'bottom_y': 5, 'tilt': -3},    # Small opening
            'C': {'top_y': -35, 'top_x': 10, 'bottom_y': 10, 'tilt': -5},  # Medium opening  
            'D': {'top_y': -60, 'top_x': 15, 'bottom_y': 15, 'tilt': -8},  # Wide opening
            'E': {'top_y': -30, 'top_x': 8, 'bottom_y': 8, 'tilt': -4},    # Round shape
            'F': {'top_y': -20, 'top_x': 6, 'bottom_y': 6, 'tilt': -3},    # Teeth showing
            'G': {'top_y': -25, 'top_x': 7, 'bottom_y': 7, 'tilt': -4},    # Other consonants
            'H': {'top_y': -40, 'top_x': 12, 'bottom_y': 12, 'tilt': -6},  # Other vowels
            'X': {'top_y': 0, 'top_x': 0, 'bottom_y': 0, 'tilt': 0}       # Silence - closed
        }
    
    def create_animation(self, image_path, audio_path, style='canadian', mouth_anchor=None):
        """Main pipeline to create talking head animation"""
        
        print(f"Creating animation with style: {style}")
        
        # Step 1: Extract phonemes from audio
        print("Extracting phonemes...")
        phoneme_data = self.phoneme_detector.extract_phonemes(audio_path)
        
        # Step 2: Process character image based on style
        print("Processing character image...")
        if style == 'standard':
            character_data = self.image_processor.prepare_character_for_sprites(image_path, mouth_anchor)
        else:  # canadian style
            character_data = self.image_processor.split_character(image_path)
        
        # Step 3: Generate keyframes based on style
        print("Generating animation keyframes...")
        if style == 'standard':
            keyframes = self.generate_sprite_keyframes(phoneme_data, fps=24)
        else:  # canadian style
            keyframes = self.generate_keyframes(phoneme_data, style)
        
        # Step 4: Render video
        print("Rendering video...")
        output_path = self.video_renderer.render(
            character_data,
            keyframes,
            audio_path,
            fps=24,
            style=style
        )
        
        return output_path
    
    def generate_keyframes(self, phoneme_data, style):
        """Convert phonemes to animation keyframes"""
        import random
        keyframes = []
        
        # Track positions for cycling through left/center/right
        position_cycle = ['left', 'center', 'right']
        position_index = 0
        
        for i, entry in enumerate(phoneme_data):
            time = entry['start'] + 0.1  # Increased delay to 100ms before each movement
            phoneme = entry['value']
            
            # Map phoneme to viseme
            viseme = self.phoneme_to_viseme(phoneme)
            
            # Get mouth position offsets
            base_position = self.mouth_positions.get(viseme, self.mouth_positions['X'])
            
            # Copy base position and adjust for style
            movement = base_position.copy()
            
            if style == 'canadian':
                # Exaggerate Canadian style movements even more
                movement['top_y'] = int(movement['top_y'] * 2.5)  # Increased from 2.0 to 2.5
                movement['top_x'] = int(movement['top_x'] * 2.5) 
                movement['bottom_y'] = int(movement['bottom_y'] * 2.5)
                
                # Add upward movement (negative y moves up)
                # Move top part further up to separate from bottom part
                movement['top_y'] -= 60  # Move head top up by 60 pixels
                movement['bottom_y'] -= 40  # Move head bottom up by 40 pixels (less than top)
                
                # Cycle through left/center/right positions
                current_position = position_cycle[position_index % len(position_cycle)]
                if current_position == 'left':
                    movement['top_x'] -= 25  # Move left
                    movement['bottom_x'] = movement.get('bottom_x', 0) - 25
                elif current_position == 'right':
                    movement['top_x'] += 25  # Move right
                    movement['bottom_x'] = movement.get('bottom_x', 0) + 25
                # center position uses default x values
                
                position_index += 1
                
                # Reduce tilt to prevent image cutoff
                base_tilt = movement.get('tilt', 0) * 1.0  # Reduced from 2.0
                lateral_tilt = random.randint(-5, 5)  # Reduced from -15 to 15
                movement['tilt'] = base_tilt + lateral_tilt
                
                # Add some randomness for South Park-like jerkiness
                movement['top_y'] += random.randint(-3, 3)  # Reduced randomness
                movement['top_x'] += random.randint(-2, 2)
            
            keyframes.append({
                'time': time,
                'movement': movement,
                'viseme': viseme
            })
            
            # Add quick closing frames after open mouth positions
            if viseme in ['C', 'D', 'E', 'H'] and style == 'canadian':  # Medium to wide openings
                # Look ahead to see when next phoneme starts
                next_time = phoneme_data[i + 1]['start'] if i + 1 < len(phoneme_data) else time + 0.2
                
                # Add a much longer delayed snap-close frame after opening
                close_time = time + min(0.4, (next_time - time) * 0.8)  # Close after 400ms or 80% of duration
                
                # Create closing movement (snap back to closed or small)
                close_movement = {
                    'top_y': random.randint(-5, 5),  # Nearly closed with small random offset
                    'top_x': random.randint(0, 2),
                    'bottom_y': random.randint(0, 2),
                    'tilt': random.randint(-10, 10)  # Random tilt for variety
                }
                
                keyframes.append({
                    'time': close_time,
                    'movement': close_movement,
                    'viseme': 'A'  # Closed mouth
                })
        
        return keyframes
    
    def generate_sprite_keyframes(self, phoneme_data, fps=24):
        """Generate keyframes for sprite-based lip-sync (standard South Park style)"""
        keyframes = []
        
        # Get viseme mapping from phoneme detector
        viseme_mapping = self.phoneme_detector.get_rhubarb_viseme_mapping()
        
        for i, entry in enumerate(phoneme_data):
            start_time = entry['start']
            viseme_code = entry['value']  # Rhubarb returns viseme codes directly
            duration = entry.get('duration', 0.2)
            
            # Convert time to frame number
            start_frame = round(start_time * fps)
            duration_frames = max(1, round(duration * fps))
            
            # Map viseme code to sprite name
            sprite_name = viseme_mapping.get(viseme_code, viseme_mapping['X'])
            
            keyframes.append({
                'frame': start_frame,
                'viseme': viseme_code,
                'sprite': sprite_name,
                'duration_frames': duration_frames,
                'start_time': start_time,
                'duration': duration
            })
        
        # Sort by frame number to ensure proper order
        keyframes.sort(key=lambda x: x['frame'])
        
        return keyframes
    
    def phoneme_to_viseme(self, phoneme):
        """Map phoneme to simplified viseme for South Park style"""
        mapping = {
            # Closed mouth
            'M': 'A', 'B': 'A', 'P': 'A',
            # Small opening
            'IY': 'B', 'IH': 'B', 'EY': 'B',
            # Medium opening  
            'AA': 'C', 'AE': 'C', 'AH': 'C',
            # Wide opening
            'AW': 'D', 'AY': 'D', 'OW': 'D',
            # Round shape
            'UW': 'E', 'UH': 'E', 'OY': 'E',
            # Teeth showing
            'F': 'F', 'V': 'F',
            # Other consonants
            'L': 'G', 'R': 'G', 'S': 'H', 'Z': 'H',
            # Silence
            'SIL': 'X'
        }
        
        return mapping.get(phoneme, 'A')