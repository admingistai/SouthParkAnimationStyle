import cv2
import numpy as np
import os
import subprocess
import tempfile
from .image_processor import ImageProcessor

class VideoRenderer:
    def __init__(self):
        self.image_processor = ImageProcessor()
        
    def render(self, character_data, keyframes, audio_path, fps=24, style='canadian'):
        """Render the final video with audio"""
        
        print(f"\n=== Starting video render ===")
        print(f"Animation style: {style}")
        print(f"Character data keys: {character_data.keys()}")
        print(f"Keyframes count: {len(keyframes)}")
        print(f"Audio path: {audio_path}")
        
        # Create temporary video file
        temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
        print(f"Temp video file: {temp_video}")
        
        # Configure canvas based on animation style
        char_height = character_data['height']
        char_width = character_data['width']
        
        if style == 'standard':
            # Standard sprite-based animation needs minimal padding
            PADDING = {
                'top': 40,
                'bottom': 40,
                'left': 40,
                'right': 40
            }
            SCALE_FACTOR = 1.0  # No scaling needed for sprite-based animation
        else:
            # Canadian flappy-head animation needs more space for movement
            PADDING = {
                'top': 120,    # Extra space for upward head movement
                'bottom': 60,
                'left': 60,
                'right': 60
            }
            SCALE_FACTOR = 0.7  # Scale down to make room for movement
        
        # New video dimensions
        video_width = char_width + PADDING['left'] + PADDING['right']
        video_height = char_height + PADDING['top'] + PADDING['bottom']
        
        print(f"Canvas: {video_width}x{video_height} (from {char_width}x{char_height})")
        print(f"Character scale: {SCALE_FACTOR}")
        
        # Store these for frame composition
        character_data['padding'] = PADDING
        character_data['scale_factor'] = SCALE_FACTOR
        character_data['video_width'] = video_width
        character_data['video_height'] = video_height
        character_data['style'] = style
        
        # Set up video writer with H.264 codec for better browser compatibility
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
        out = cv2.VideoWriter(temp_video, fourcc, fps, (video_width, video_height))
        
        # Fallback to mp4v if avc1 doesn't work
        if not out.isOpened():
            print("avc1 codec failed, trying mp4v...")
            out.release()
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (video_width, video_height))
        
        if not out.isOpened():
            raise Exception("Failed to open video writer")
        
        # Calculate total duration based on animation style
        if style == 'standard':
            # For sprite animation, duration is based on keyframe data
            duration = max(kf.get('start_time', 0) + kf.get('duration', 0.2) for kf in keyframes) if keyframes else 1.0
        else:
            # For movement animation, use existing logic
            duration = keyframes[-1]['time'] + 0.5 if keyframes else 1.0
        
        total_frames = int(duration * fps)
        
        print(f"Video specs: {video_width}x{video_height}, {fps}fps, {total_frames} frames, {duration:.2f}s")
        
        # Render each frame
        print(f"Rendering {total_frames} frames...")
        for frame_num in range(total_frames):
            current_time = frame_num / fps
            
            # Composite frame based on animation style
            debug_frame = frame_num < 3  # Debug first 3 frames
            
            if style == 'standard':
                # Sprite-based animation
                viseme_code = self.get_current_viseme(keyframes, frame_num)
                if frame_num % 50 == 0:
                    print(f"Frame {frame_num}/{total_frames}: time={current_time:.2f}s, viseme={viseme_code}")
                frame = self.render_sprite_frame(character_data, viseme_code, debug=debug_frame)
            else:
                # Movement-based animation (Canadian style)
                movement = self.interpolate_movement(keyframes, current_time)
                if frame_num % 50 == 0:
                    print(f"Frame {frame_num}/{total_frames}: time={current_time:.2f}s, movement={movement}")
                frame = self.image_processor.composite_frame_with_movement(character_data, movement, debug=debug_frame)
            
            # Check frame content before conversion
            if frame_num == 0:  # Log first frame details
                print(f"First frame shape: {frame.shape}")
                print(f"First frame dtype: {frame.dtype}")
                print(f"First frame min/max: {frame.min()}/{frame.max()}")
                unique_colors = len(np.unique(frame.reshape(-1, frame.shape[-1]), axis=0))
                print(f"Unique colors in first frame: {unique_colors}")
                
                # Save first frame as debug image
                debug_path = os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'debug_frame_0.png')
                cv2.imwrite(debug_path, cv2.cvtColor(frame, cv2.COLOR_RGBA2BGRA))
                print(f"Saved debug frame: {debug_path}")
            
            # Convert RGBA to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            
            # Write frame
            out.write(frame_bgr)
        
        # Release video writer
        out.release()
        print(f"Video rendering complete: {temp_video}")
        
        # Check if temp video file was created and has content
        if os.path.exists(temp_video):
            temp_size = os.path.getsize(temp_video)
            print(f"Temp video size: {temp_size} bytes")
            if temp_size == 0:
                raise Exception("Generated video file is empty")
        else:
            raise Exception("Failed to create temp video file")
        
        # Combine with audio using ffmpeg
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'talking_head_{os.getpid()}.mp4')
        
        try:
            self.add_audio_to_video(temp_video, audio_path, output_path)
            
            # Check final output
            if os.path.exists(output_path):
                final_size = os.path.getsize(output_path)
                print(f"Final video size: {final_size} bytes")
                if final_size == 0:
                    print("WARNING: Final video file is empty!")
            else:
                print("WARNING: Final video file was not created!")
                
        except Exception as e:
            print(f"Audio encoding failed: {e}")
            # If audio encoding fails, just copy the video without audio
            import shutil
            shutil.copy(temp_video, output_path)
            print(f"Copied video without audio to: {output_path}")
        
        # Clean up
        os.unlink(temp_video)
        
        return output_path
    
    def interpolate_movement(self, keyframes, time):
        """Get discrete movement at given time (no smooth interpolation for South Park style)"""
        if not keyframes:
            return {'top_y': 0, 'top_x': 0, 'bottom_y': 0}
        
        # Find the most recent keyframe (discrete positions, no interpolation)
        current_movement = {'top_y': 0, 'top_x': 0, 'bottom_y': 0}
        
        for kf in keyframes:
            if kf['time'] <= time:
                current_movement = kf['movement']
            else:
                break
        
        return current_movement
    
    def get_current_viseme(self, keyframes, frame_num):
        """Get the current viseme code for sprite-based animation"""
        if not keyframes:
            return 'X'  # Default to silence
        
        # Find the active keyframe for this frame
        current_viseme = 'X'
        
        for kf in keyframes:
            if kf['frame'] <= frame_num < kf['frame'] + kf['duration_frames']:
                current_viseme = kf['viseme']
                break
        
        return current_viseme
    
    def render_sprite_frame(self, character_data, viseme_code, debug=False):
        """Render a single frame using sprite-based animation"""
        
        # Create canvas with background
        canvas_width = character_data['video_width']
        canvas_height = character_data['video_height']
        padding = character_data['padding']
        
        # Create white background
        canvas = np.full((canvas_height, canvas_width, 4), [255, 255, 255, 255], dtype=np.uint8)
        
        # Get base character image
        base_image = character_data['base_image']
        
        # Calculate character position on canvas (centered)
        char_x = padding['left']
        char_y = padding['top']
        
        if debug:
            print(f"Rendering sprite frame: viseme={viseme_code}")
            print(f"Canvas size: {canvas_width}x{canvas_height}")
            print(f"Character position: ({char_x}, {char_y})")
        
        # Place base character on canvas
        self.image_processor.paste_with_alpha(canvas, base_image, char_x, char_y)
        
        # Composite mouth sprite
        sprite_frame = self.image_processor.composite_sprite_frame(character_data, viseme_code, debug=debug)
        
        # Replace the character area with the sprite-composited version
        char_height, char_width = base_image.shape[:2]
        canvas[char_y:char_y+char_height, char_x:char_x+char_width] = sprite_frame
        
        return canvas
    
    def add_audio_to_video(self, video_path, audio_path, output_path):
        """Use ffmpeg to add audio to video"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # More robust ffmpeg command for better browser compatibility
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'libx264',           # Re-encode video with H.264
            '-preset', 'fast',           # Fast encoding
            '-crf', '23',                # Good quality
            '-c:a', 'aac',               # AAC audio
            '-b:a', '128k',              # Audio bitrate
            '-movflags', '+faststart',   # Enable web streaming
            '-shortest',                 # Match shortest stream
            '-y',                        # Overwrite output
            output_path
        ]
        
        print(f"Running ffmpeg: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("FFmpeg completed successfully")
            if result.stderr:
                print(f"FFmpeg stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error (exit code {e.returncode}): {e.stderr}")
            raise Exception(f"FFmpeg failed: {e.stderr}")