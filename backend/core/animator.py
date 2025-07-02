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
        
        # Simplified to 4 mouth positions like in the image
        # Position 1: Closed
        # Position 2: Small opening
        # Position 3: Medium opening  
        # Position 4: Wide opening
        self.mouth_positions = [
            {'top_y': 0, 'top_x': 0, 'bottom_y': 0, 'tilt': 0},        # Position 1: Closed
            {'top_y': -5, 'top_x': 0, 'bottom_y': 3, 'tilt': -2},      # Position 2: Small (slight left tilt)
            {'top_y': -10, 'top_x': 0, 'bottom_y': 5, 'tilt': 2},      # Position 3: Medium (slight right tilt)
            {'top_y': -15, 'top_x': 0, 'bottom_y': 8, 'tilt': -3},     # Position 4: Wide (more left tilt)
        ]
        
        # Energy thresholds for determining which mouth position to use
        self.energy_thresholds = {
            'silence': 0.1,    # Below this = closed mouth
            'quiet': 0.3,      # Below this = small opening
            'normal': 0.6,     # Below this = medium opening
            # Above 0.6 = wide opening
        }
    
    def create_animation(self, image_path, audio_path, style='canadian', mouth_anchor=None):
        """Main pipeline to create talking head animation"""
        
        print(f"Creating animation with style: {style}")
        
        # Step 1: Extract phonemes/energy from audio
        print("Analyzing audio...")
        if style == 'canadian':
            # For Canadian style, we'll use energy-based detection instead of phonemes
            audio_data = self.analyze_audio_energy(audio_path)
        elif style == 'nutcracker':
            # For Nutcracker style, use amplitude-based analysis
            audio_data = self.analyze_audio_amplitude(audio_path)
        else:
            # Standard style still uses phonemes
            audio_data = self.phoneme_detector.extract_phonemes(audio_path)
        
        # Step 2: Process character image based on style
        print("Processing character image...")
        if style == 'standard':
            character_data = self.image_processor.prepare_character_for_sprites(image_path, mouth_anchor)
        elif style == 'nutcracker':
            character_data = self.image_processor.split_character_nutcracker(image_path, mouth_anchor)
        else:  # canadian style
            character_data = self.image_processor.split_character(image_path)
        
        # Step 3: Generate keyframes based on style
        print("Generating animation keyframes...")
        if style == 'standard':
            keyframes = self.generate_sprite_keyframes(audio_data, fps=24)
        elif style == 'nutcracker':
            keyframes = self.generate_nutcracker_keyframes(audio_data, fps=24)
        else:  # canadian style
            keyframes = self.generate_canadian_keyframes(audio_data, fps=24)
        
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
    
    def analyze_audio_energy(self, audio_path):
        """Analyze audio energy levels for Canadian-style animation"""
        # This is a simplified version - you might want to use librosa or another audio library
        # For now, we'll use the phoneme detector but interpret it differently
        phoneme_data = self.phoneme_detector.extract_phonemes(audio_path)
        
        # Convert phonemes to energy levels (simplified)
        energy_data = []
        for entry in phoneme_data:
            # Map phonemes to energy levels
            phoneme = entry['value']
            
            # Louder/more open sounds get higher energy
            if phoneme in ['AA', 'AH', 'AW', 'AY', 'OW']:  # Open vowels
                energy = 0.8
            elif phoneme in ['IY', 'IH', 'EY', 'EH', 'AE']:  # Mid vowels
                energy = 0.5
            elif phoneme in ['M', 'B', 'P', 'F', 'V']:  # Closed consonants
                energy = 0.2
            elif phoneme in ['SIL', 'X']:  # Silence
                energy = 0.0
            else:
                energy = 0.4  # Default
            
            energy_data.append({
                'start': entry['start'],
                'duration': entry.get('duration', 0.1),
                'energy': energy
            })
        
        return energy_data
    
    def analyze_audio_amplitude(self, audio_path):
        """Analyze audio amplitude levels for Nutcracker-style animation"""
        import wave
        import struct
        
        # Open the audio file
        try:
            with wave.open(audio_path, 'rb') as wav_file:
                # Get audio parameters
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                
                # Read all frames
                frames = wav_file.readframes(n_frames)
        except:
            # If wave fails, use phoneme detector as fallback and convert to amplitude
            print("Wave file reading failed, using phoneme detector as fallback")
            return self.analyze_audio_energy(audio_path)
        
        # Convert byte data to amplitude values
        if sample_width == 1:
            fmt = f"{n_frames * channels}B"
            data = struct.unpack(fmt, frames)
            data = [float(val - 128) / 128.0 for val in data]  # Convert to -1 to 1 range
        elif sample_width == 2:
            fmt = f"{n_frames * channels}h"
            data = struct.unpack(fmt, frames)
            data = [float(val) / 32768.0 for val in data]  # Convert to -1 to 1 range
        else:
            print(f"Unsupported sample width: {sample_width}")
            return self.analyze_audio_energy(audio_path)
        
        # Calculate RMS energy using sliding window
        window_size = int(framerate * 0.05)  # 50ms window
        hop_size = int(framerate * 0.02)    # 20ms hop
        
        amplitude_data = []
        
        for i in range(0, len(data) - window_size, hop_size):
            # Get window of samples
            window = data[i:i + window_size]
            
            # Calculate RMS (Root Mean Square) energy
            rms = np.sqrt(np.mean(np.square(window)))
            
            # Convert to time
            time = i / float(framerate * channels)
            
            amplitude_data.append({
                'start': time,
                'duration': window_size / float(framerate * channels),
                'amplitude': rms,
                'energy': rms  # Keep energy field for compatibility
            })
        
        # Normalize amplitudes to 0-1 range
        if amplitude_data:
            max_amp = max(entry['amplitude'] for entry in amplitude_data)
            if max_amp > 0:
                for entry in amplitude_data:
                    entry['amplitude'] = entry['amplitude'] / max_amp
                    entry['energy'] = entry['amplitude']  # Keep synchronized
        
        return amplitude_data
    
    def generate_canadian_keyframes(self, audio_data, fps=24):
        """Generate keyframes for Canadian-style animation with 4 mouth positions"""
        keyframes = []
        
        print("\n=== Canadian Animation Keyframes ===")
        print("Time (s) | Energy | Position | Description | Used")
        print("-" * 60)
        
        # Frame rate control - only use every Nth detection
        viseme_skip_rate = 3  # Use every 3rd detection (adjust this to control speed)
        min_duration = 0.15   # Minimum duration between mouth changes (in seconds)
        
        last_used_time = -1
        last_position_index = 0  # Track last mouth position
        
        # Simple cycling pattern - we'll cycle through positions based on energy
        for i, entry in enumerate(audio_data):
            time = entry['start']
            energy = entry['energy']
            
            # Determine mouth position based on energy level
            if energy < self.energy_thresholds['silence']:
                position_index = 0  # Closed
                description = "Closed"
            elif energy < self.energy_thresholds['quiet']:
                position_index = 1  # Small opening
                description = "Small"
            elif energy < self.energy_thresholds['normal']:
                position_index = 2  # Medium opening
                description = "Medium"
            else:
                position_index = 3  # Wide opening
                description = "Wide"
            
            # Special handling for silence - always use silence frames, never skip
            is_silence = energy < self.energy_thresholds['silence']
            
            # Skip this frame if it's too soon after the last one AND it's not silence
            skip_frame = False
            if not is_silence and ((i % viseme_skip_rate != 0) or (time - last_used_time < min_duration)):
                skip_frame = True
            
            # Also force a closing frame if we detect a significant pause in audio
            if i > 0:
                prev_time = audio_data[i-1]['start'] + audio_data[i-1].get('duration', 0.1)
                gap_duration = time - prev_time
                if gap_duration > 0.3 and last_position_index > 0:  # Gap > 300ms and mouth was open
                    # Add a closing frame at the start of the gap
                    close_movement = self.mouth_positions[0].copy()  # Closed position
                    keyframes.append({
                        'time': prev_time + 0.05,  # Close shortly after previous sound ends
                        'movement': close_movement,
                        'position': 1,
                        'energy': 0,
                        'reason': 'gap_close'
                    })
                    print(f"{prev_time + 0.05:7.2f} | {0.0:6.2f} | {1:8} | {'Gap Close':11} | USED")
            
            # Print debug info for all detections
            used_status = "USED" if not skip_frame else "SKIP"
            if is_silence and skip_frame:
                used_status = "SILENCE_USED"  # Override for silence
                skip_frame = False  # Never skip silence
            
            print(f"{time:7.2f} | {energy:6.2f} | {position_index + 1:8} | {description:11} | {used_status}")
            
            # Skip this frame if we determined to skip it
            if skip_frame:
                continue
                
            last_used_time = time
            last_position_index = position_index
            
            # Get the movement values for this position
            movement = self.mouth_positions[position_index].copy()
            
            # Only apply exaggeration if not silence (keep silence completely still)
            if not is_silence:
                # Canadian style exaggeration (reduced multipliers)
                movement['top_y'] = int(movement['top_y'] * 1.2)
                movement['bottom_y'] = int(movement['bottom_y'] * 1.2)
                
                # Add the characteristic up/down movement (scaled down by 2x)
                movement['top_y'] -= 5      # Head moves up (reduced from 10)
                movement['bottom_y'] += 3   # Jaw moves down (reduced from 5)
                
                # Apply tilt to make it more dynamic
                if 'tilt' in movement:
                    movement['tilt'] = movement['tilt'] * 1.1  # Reduced tilt multiplier
            
            keyframes.append({
                'time': time,
                'movement': movement,
                'position': position_index + 1,  # 1-4 for display
                'energy': energy
            })
            
            # Add closing frame between sounds (but less frequently) - only for non-silence
            if position_index > 0 and not is_silence:  # If mouth was open and not silence
                # Calculate when to close
                duration = entry.get('duration', 0.1)
                close_time = time + min(duration * 0.7, 0.4)  # Increased close duration
                
                close_movement = self.mouth_positions[0].copy()  # Closed position
                
                keyframes.append({
                    'time': close_time,
                    'movement': close_movement,
                    'position': 1,
                    'energy': 0
                })
        
        print(f"\nGenerated {len(keyframes)} keyframes from {len(audio_data)} audio segments")
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
    
    def generate_nutcracker_keyframes(self, audio_data, fps=24):
        """Generate keyframes for Nutcracker-style jaw animation with vertical sliding"""
        keyframes = []
        
        print("\n=== Nutcracker Animation Keyframes ===")
        print("Time (s) | Amplitude | Jaw Offset | Description")
        print("-" * 50)
        
        # Configuration for jaw movement (vertical pixels)
        max_jaw_offset = 30  # Maximum jaw drop in pixels
        overshoot_offset = 35  # Overshoot for bounce effect
        attack_time = 0.1  # Time to open jaw (100ms)
        decay_time = 0.2   # Time to close jaw (200ms)
        
        # Thresholds for jaw movement
        silence_threshold = 0.1
        quiet_threshold = 0.3
        normal_threshold = 0.6
        
        last_offset = 0
        last_time = -1
        
        for i, entry in enumerate(audio_data):
            time = entry['start']
            amplitude = entry.get('amplitude', entry.get('energy', 0))
            
            # Map amplitude to jaw vertical offset
            if amplitude < silence_threshold:
                target_offset = 0  # Closed
                description = "Closed"
            elif amplitude < quiet_threshold:
                target_offset = 10  # 10 pixels down
                description = "Small"
            elif amplitude < normal_threshold:
                target_offset = 20  # 20 pixels down
                description = "Medium"
            else:
                target_offset = max_jaw_offset  # 30 pixels down
                description = "Wide"
            
            # Add overshoot for sudden loud sounds
            if amplitude > 0.8 and last_offset < 15:
                # Create overshoot keyframe
                overshoot_time = time + attack_time * 0.5
                keyframes.append({
                    'time': overshoot_time,
                    'jaw_offset_y': overshoot_offset,
                    'amplitude': amplitude,
                    'description': 'Overshoot'
                })
                print(f"{overshoot_time:7.2f} | {amplitude:9.2f} | {overshoot_offset:10} | {description} (overshoot)")
            
            # Main keyframe
            keyframes.append({
                'time': time,
                'jaw_offset_y': target_offset,
                'amplitude': amplitude,
                'description': description
            })
            
            print(f"{time:7.2f} | {amplitude:9.2f} | {target_offset:10} | {description}")
            
            # Add closing keyframe for non-silence
            if target_offset > 0:
                close_time = time + entry.get('duration', 0.1) * 0.7
                keyframes.append({
                    'time': close_time,
                    'jaw_offset_y': 0,
                    'amplitude': 0,
                    'description': 'Close'
                })
            
            last_offset = target_offset
            last_time = time
        
        print(f"\nGenerated {len(keyframes)} keyframes from {len(audio_data)} audio segments")
        return keyframes