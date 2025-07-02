import cv2
import numpy as np
from PIL import Image
from .mouth_sprite_manager import MouthSpriteManager

class ImageProcessor:
    def __init__(self):
        self.split_ratio = 0.75  # 75% top, 25% bottom - splits at mouth level for better flappy head effect
        self.mouth_sprite_manager = MouthSpriteManager()
        
    def split_character(self, image_path):
        """Split character image into top and bottom halves"""
        
        print(f"\n=== Splitting character image: {image_path} ===")
        
        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise Exception(f"Could not load image: {image_path}")
        
        print(f"Original image shape: {img.shape}")
        
        # OpenCV loads as BGR(A), we need RGBA
        if len(img.shape) == 3 and img.shape[2] == 3:
            # Convert BGR to RGB and add alpha
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            alpha = np.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
            img = np.concatenate([img, alpha], axis=2)
            print("Converted BGR to RGBA")
        elif len(img.shape) == 3 and img.shape[2] == 4:
            # Convert BGRA to RGBA
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
            print("Converted BGRA to RGBA")
        else:
            raise Exception(f"Unexpected image format: {img.shape}")
        
        height, width = img.shape[:2]
        print(f"Final image dimensions: {width}x{height}")
        
        # Calculate split point (for now, use fixed ratio)
        split_y = int(height * self.split_ratio)
        print(f"Split ratio: {self.split_ratio}, Split Y: {split_y}")
        
        # Split image
        top_half = img[:split_y, :].copy()
        bottom_half = img[split_y:, :].copy()
        
        print(f"Top half shape: {top_half.shape}")
        print(f"Bottom half shape: {bottom_half.shape}")
        
        # Validate the split parts have content
        top_nonzero = np.count_nonzero(top_half[:,:,3])  # Count non-transparent pixels
        bottom_nonzero = np.count_nonzero(bottom_half[:,:,3])
        print(f"Top half non-transparent pixels: {top_nonzero}")
        print(f"Bottom half non-transparent pixels: {bottom_nonzero}")
        
        # Find the body (everything except the head)
        # For simplicity, assume body is below a certain point
        body_start = int(height * 0.3)  # Head is roughly top 30%
        body = img[body_start:, :].copy()
        
        # Create pivot point for rotation (center of split line)
        pivot_x = width // 2
        pivot_y = split_y
        
        result = {
            'full_image': img,
            'top_half': top_half,
            'bottom_half': bottom_half,
            'body': body,
            'pivot': (pivot_x, pivot_y),
            'split_y': split_y,
            'width': width,
            'height': height
        }
        
        print(f"Character data created successfully")
        print(f"Pivot point: ({pivot_x}, {pivot_y})")
        
        return result
    
    def split_character_nutcracker(self, image_path, mouth_anchor=None):
        """Split character for nutcracker-style jaw animation"""
        
        print(f"\n=== Preparing character for nutcracker animation: {image_path} ===")
        
        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise Exception(f"Could not load image: {image_path}")
        
        # Convert to RGBA
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            alpha = np.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
            img = np.concatenate([img, alpha], axis=2)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        
        height, width = img.shape[:2]
        print(f"Image dimensions: {width}x{height}")
        
        # Extract mouth/jaw region
        jaw_data = self.extract_mouth_region(img, mouth_anchor)
        
        # Create the base face (with mouth area removed)
        base_face = img.copy()
        jaw_rect = jaw_data['jaw_rect']
        
        # Create a dark cavity where the mouth was
        cavity_color = [20, 20, 20, 255]  # Dark gray
        base_face[jaw_rect['y']:jaw_rect['y']+jaw_rect['height'], 
                  jaw_rect['x']:jaw_rect['x']+jaw_rect['width']] = cavity_color
        
        result = {
            'full_image': img,
            'base_face': base_face,
            'jaw_image': jaw_data['jaw_image'],
            'jaw_rect': jaw_rect,
            'width': width,
            'height': height,
            'mouth_cavity_bounds': {
                'x': jaw_rect['x'],
                'y': jaw_rect['y'],
                'width': jaw_rect['width'],
                'height': int(jaw_rect['height'] * 1.2)  # Slightly larger for cavity
            }
        }
        
        print(f"Nutcracker character data created successfully")
        print(f"Jaw rectangle: x={jaw_rect['x']}, y={jaw_rect['y']}, w={jaw_rect['width']}, h={jaw_rect['height']}")
        
        return result
    
    def extract_mouth_region(self, image, mouth_anchor=None):
        """Extract the mouth/jaw region from a face image"""
        
        print("Extracting mouth region...")
        height, width = image.shape[:2]
        
        # If manual mouth anchor is provided, use it to calculate mouth region
        if mouth_anchor is not None:
            print(f"Using manual mouth anchor: {mouth_anchor}")
            center_x, center_y = mouth_anchor
            
            # Calculate mouth region around the anchor point
            mouth_width = int(width * 0.3)   # 30% of image width
            mouth_height = int(height * 0.2) # 20% of image height
            
            # Center the region around the anchor point
            mouth_x = center_x - mouth_width // 2
            mouth_y = center_y - mouth_height // 2
            
            # Ensure bounds are within image
            mouth_x = max(0, min(mouth_x, width - mouth_width))
            mouth_y = max(0, min(mouth_y, height - mouth_height))
            
            print(f"Manual mouth region: x={mouth_x}, y={mouth_y}, w={mouth_width}, h={mouth_height}")
        else:
            # Try to detect face using OpenCV
            try:
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
                
                # Try to load face cascade classifier
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                face_cascade = cv2.CascadeClassifier(cascade_path)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                
                if len(faces) > 0:
                    # Use the first detected face
                    x, y, w, h = faces[0]
                    print(f"Face detected at: x={x}, y={y}, w={w}, h={h}")
                    
                    # Calculate mouth region (lower third of face)
                    mouth_y = y + int(h * 0.75)  # Start at 75% down the face (was 65%)
                    mouth_height = int(h * 0.2)  # 20% of face height (was 30%)
                    mouth_x = x + int(w * 0.35)  # Indent 35% from face edges (was 15%)
                    mouth_width = int(w * 0.3)   # 30% of face width (was 70%)
                else:
                    print("No face detected, using default proportions")
                    # Use default proportions (lower third of image)
                    mouth_y = int(height * 0.75)  # Start at 75% down (was 65%)
                    mouth_height = int(height * 0.2)  # 20% of height (was 25%)
                    mouth_x = int(width * 0.35)  # Indent 35% from edges (was 20%)
                    mouth_width = int(width * 0.3)  # 30% of width (was 60%)
            except Exception as e:
                print(f"Face detection failed: {e}, using default proportions")
                # Fallback to default proportions
                mouth_y = int(height * 0.75)  # Start at 75% down (was 65%)
                mouth_height = int(height * 0.2)  # 20% of height (was 25%)
                mouth_x = int(width * 0.35)  # Indent 35% from edges (was 20%)
                mouth_width = int(width * 0.3)  # 30% of width (was 60%)
        
        # Ensure bounds are within image
        mouth_x = max(0, mouth_x)
        mouth_y = max(0, mouth_y)
        mouth_width = min(mouth_width, width - mouth_x)
        mouth_height = min(mouth_height, height - mouth_y)
        
        # Extract jaw region
        jaw_image = image[mouth_y:mouth_y+mouth_height, mouth_x:mouth_x+mouth_width].copy()
        
        # Add smooth edges using alpha gradient
        edge_size = 3
        if jaw_image.shape[2] == 4:  # Has alpha channel
            # Create vertical gradient for top edge
            for i in range(edge_size):
                alpha_multiplier = i / edge_size
                jaw_image[i, :, 3] = (jaw_image[i, :, 3] * alpha_multiplier).astype(np.uint8)
        
        print(f"Extracted jaw region: {jaw_image.shape}")
        
        return {
            'jaw_image': jaw_image,
            'jaw_rect': {
                'x': mouth_x,
                'y': mouth_y,
                'width': mouth_width,
                'height': mouth_height
            }
        }
    
    def prepare_character_for_sprites(self, image_path, mouth_anchor=None):
        """Prepare character image for sprite-based lip-sync (standard South Park style)"""
        
        print(f"\n=== Preparing character for sprite-based animation: {image_path} ===")
        
        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise Exception(f"Could not load image: {image_path}")
        
        print(f"Original image shape: {img.shape}")
        
        # Convert to RGBA format
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            alpha = np.ones((img.shape[0], img.shape[1], 1), dtype=img.dtype) * 255
            img = np.concatenate([img, alpha], axis=2)
            print("Converted BGR to RGBA")
        elif len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
            print("Converted BGRA to RGBA")
        
        height, width = img.shape[:2]
        print(f"Final image dimensions: {width}x{height}")
        
        # Determine mouth anchor point
        if mouth_anchor is None:
            # Use automatic detection
            mouth_anchor = self.mouth_sprite_manager.find_optimal_mouth_position(img)
            print(f"Auto-detected mouth anchor: {mouth_anchor}")
        else:
            # Use manual coordinates but still run through position validation
            mouth_anchor = self.mouth_sprite_manager.find_optimal_mouth_position(img, approximate_anchor=mouth_anchor)
            print(f"Using manual mouth anchor: {mouth_anchor}")
        
        # Determine appropriate sprite size
        sprite_size = self.mouth_sprite_manager.detect_mouth_region_size(img, mouth_anchor)
        print(f"Suggested sprite size: {sprite_size}")
        
        # Create mask for mouth region (for optional mouth removal)
        mouth_mask = self.create_mouth_removal_mask(img, mouth_anchor, sprite_size)
        
        result = {
            'base_image': img,
            'mouth_anchor': mouth_anchor,
            'sprite_size': sprite_size,
            'mouth_mask': mouth_mask,
            'width': width,
            'height': height
        }
        
        print(f"Character prepared for sprite-based animation")
        print(f"Mouth anchor: {mouth_anchor}, Sprite size: {sprite_size}")
        
        return result
    
    def create_mouth_removal_mask(self, image, mouth_anchor, sprite_size):
        """Create a mask to optionally remove existing mouth from character"""
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Create elliptical mask around mouth area
        center_x, center_y = mouth_anchor
        sprite_width, sprite_height = sprite_size
        
        # Make mask slightly larger than sprite to ensure coverage
        mask_width = int(sprite_width * 1.2)
        mask_height = int(sprite_height * 1.2)
        
        cv2.ellipse(mask, (center_x, center_y), 
                   (mask_width // 2, mask_height // 2), 
                   0, 0, 360, 255, -1)
        
        return mask
    
    def composite_sprite_frame(self, character_data, viseme_code, debug=False):
        """Composite frame using sprite-based mouth animation (standard South Park style)"""
        
        if debug:
            print(f"Compositing sprite frame with viseme: {viseme_code}")
        
        # Get base image and parameters
        base_image = character_data['base_image'].copy()
        mouth_anchor = character_data['mouth_anchor']
        sprite_size = character_data['sprite_size']
        
        # Get the appropriate mouth sprite
        sprite_array = self.mouth_sprite_manager.scale_sprite(viseme_code, target_size=sprite_size)
        
        if debug:
            print(f"Using sprite for viseme {viseme_code}")
            print(f"Sprite shape: {sprite_array.shape}")
            print(f"Mouth anchor: {mouth_anchor}")
            print(f"Sprite size: {sprite_size}")
        
        # Calculate sprite position (center sprite at anchor point)
        sprite_height, sprite_width = sprite_array.shape[:2]
        sprite_x = mouth_anchor[0] - sprite_width // 2
        sprite_y = mouth_anchor[1] - sprite_height // 2
        
        # Optional: Remove existing mouth (uncomment if needed)
        # mouth_mask = character_data['mouth_mask']
        # base_image[mouth_mask == 255] = [255, 255, 255, 0]  # Make transparent
        
        # Composite sprite onto base image
        self.paste_with_alpha(base_image, sprite_array, sprite_x, sprite_y)
        
        if debug:
            print(f"Sprite placed at: ({sprite_x}, {sprite_y})")
            print(f"Final frame shape: {base_image.shape}")
        
        return base_image
    
    def rotate_image_part(self, image, angle, pivot):
        """Rotate image around pivot point for South Park flappy head effect"""
        if angle == 0:
            return image, None
        
        print(f"Rotating image by {angle}° around pivot {pivot}")
        
        # Get rotation matrix around the pivot point
        M = cv2.getRotationMatrix2D(pivot, angle, 1.0)
        
        # Get image dimensions
        height, width = image.shape[:2]
        
        # For South Park style, we don't want to expand the canvas
        # Just rotate within the original bounds
        rotated = cv2.warpAffine(image, M, (width, height), 
                                 flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT,
                                 borderValue=(0, 0, 0, 0))  # Transparent border
        
        return rotated, M
    
    def composite_frame_with_rotation(self, character_data, keyframe, debug=False):
        """Composite frame using South Park rotation (hinged at back of head)"""
        
        if debug:
            print(f"Compositing frame with rotation: angle={keyframe.get('angle', 0)}°, tilt={keyframe.get('tilt', 0)}°")
        
        # Get canvas dimensions
        canvas_width = character_data['video_width']
        canvas_height = character_data['video_height']
        scale_factor = character_data['scale_factor']
        padding = character_data['padding']
        
        # Create white background canvas
        frame = np.full((canvas_height, canvas_width, 4), [255, 255, 255, 255], dtype=np.uint8)
        
        # Scale the character parts
        top_half_scaled = self.scale_image(character_data['top_half'], scale_factor)
        bottom_half_scaled = self.scale_image(character_data['bottom_half'], scale_factor)
        
        # Calculate base positions (centered in canvas)
        char_width_scaled = int(character_data['width'] * scale_factor)
        char_height_scaled = int(character_data['height'] * scale_factor)
        split_y_scaled = int(character_data['split_y'] * scale_factor)
        
        base_x = (canvas_width - char_width_scaled) // 2
        base_y = padding['top']
        
        # Calculate pivot point (rear of head, about 45% from left edge)
        pivot_x = base_x + int(char_width_scaled * 0.05)  # 5% from left = rear of head
        pivot_y = base_y + split_y_scaled  # At the split line
        
        # Bottom half position (moves down slightly)
        bottom_x = base_x
        bottom_y = base_y + split_y_scaled + keyframe.get('bottom_y', 0)
        
        # Rotate top half around pivot
        angle = keyframe.get('angle', 0)
        if angle != 0:
            # Rotate the top half image
            top_rotated, _ = self.rotate_image_part(top_half_scaled, -angle, 
                                                   (int(char_width_scaled * 0.05), top_half_scaled.shape[0]))
            top_half_scaled = top_rotated
        
        # Apply global tilt to both parts
        tilt = keyframe.get('tilt', 0)
        if tilt != 0:
            # Apply small tilt to entire character
            # This would be done after compositing both parts
            pass  # Will implement after basic rotation works
        
        # Calculate top half position after rotation
        top_x = base_x
        top_y = base_y
        
        if debug:
            print(f"Pivot point: ({pivot_x}, {pivot_y})")
            print(f"Top half at: ({top_x}, {top_y}) rotated {angle}°")
            print(f"Bottom half at: ({bottom_x}, {bottom_y})")
        
        # Place the parts on canvas
        self.paste_with_alpha(frame, bottom_half_scaled, bottom_x, bottom_y)
        self.paste_with_alpha(frame, top_half_scaled, top_x, top_y)
        
        if debug:
            print(f"Final frame shape: {frame.shape}")
        
        return frame
    
    def composite_frame_with_movement(self, character_data, movement, debug=False):
        """Composite frame using South Park translation movement (no rotation)"""
        
        if debug:
            print(f"Compositing frame with movement: {movement}")
        
        # Get canvas dimensions (expanded for movement)
        canvas_width = character_data['video_width']
        canvas_height = character_data['video_height']
        scale_factor = character_data['scale_factor']
        padding = character_data['padding']
        
        # Create white background canvas
        frame = np.full((canvas_height, canvas_width, 4), [255, 255, 255, 255], dtype=np.uint8)
        
        if debug:
            print(f"Canvas dimensions: {canvas_width}x{canvas_height}")
            print(f"Scale factor: {scale_factor}")
            print(f"Movement offsets: {movement}")
        
        # Scale the character parts
        top_half_scaled = self.scale_image(character_data['top_half'], scale_factor)
        bottom_half_scaled = self.scale_image(character_data['bottom_half'], scale_factor)
        
        # Calculate base positions (centered in canvas)
        char_width_scaled = int(character_data['width'] * scale_factor)
        char_height_scaled = int(character_data['height'] * scale_factor)
        split_y_scaled = int(character_data['split_y'] * scale_factor)
        
        base_x = (canvas_width - char_width_scaled) // 2
        base_y = padding['top']
        
        # Calculate positions with movement offsets
        # Bottom half position (moves down slightly)
        bottom_x = base_x
        bottom_y = base_y + split_y_scaled + movement['bottom_y']
        
        # Apply tilt rotation to top half if specified
        tilt_angle = movement.get('tilt', 0)
        if tilt_angle != 0:
            # Rotate around the bottom center of the top half (the mouth line)
            pivot_x = top_half_scaled.shape[1] // 2
            pivot_y = top_half_scaled.shape[0] - 1  # Bottom of top half
            top_half_rotated, _ = self.rotate_image_part(top_half_scaled, tilt_angle, (pivot_x, pivot_y))
            top_half_scaled = top_half_rotated
        
        # Top half position (moves up and forward)
        top_x = base_x + movement['top_x']
        top_y = base_y + split_y_scaled - top_half_scaled.shape[0] + movement['top_y']
        
        if debug:
            print(f"Top half at: ({top_x}, {top_y}) with tilt: {tilt_angle}°")
            print(f"Bottom half at: ({bottom_x}, {bottom_y})")
        
        # Fill mouth cavity with black when mouth is open
        # Commented out - the large black oval doesn't match South Park style
        # if movement['top_y'] < -5:  # Mouth is open
        #     self.fill_mouth_cavity(frame, top_x, top_y, bottom_x, bottom_y, 
        #                          top_half_scaled.shape, bottom_half_scaled.shape)
        
        # Place the parts on canvas
        self.paste_with_alpha(frame, bottom_half_scaled, bottom_x, bottom_y)
        self.paste_with_alpha(frame, top_half_scaled, top_x, top_y)
        
        if debug:
            print(f"Final frame shape: {frame.shape}")
        
        return frame
    
    def scale_image(self, image, scale_factor):
        """Scale image by given factor"""
        if scale_factor == 1.0:
            return image
        
        height, width = image.shape[:2]
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
    
    def paste_with_alpha(self, canvas, image, x, y):
        """Paste image onto canvas with alpha blending"""
        h, w = image.shape[:2]
        
        # Calculate bounds
        canvas_h, canvas_w = canvas.shape[:2]
        
        # Clip to canvas bounds
        start_x = max(0, x)
        start_y = max(0, y)
        end_x = min(canvas_w, x + w)
        end_y = min(canvas_h, y + h)
        
        # Calculate image region
        img_start_x = max(0, -x)
        img_start_y = max(0, -y)
        img_end_x = img_start_x + (end_x - start_x)
        img_end_y = img_start_y + (end_y - start_y)
        
        if start_x >= end_x or start_y >= end_y:
            return  # Nothing to paste
        
        # Extract regions
        canvas_region = canvas[start_y:end_y, start_x:end_x]
        image_region = image[img_start_y:img_end_y, img_start_x:img_end_x]
        
        if image_region.shape[2] == 4:  # Has alpha channel
            # Extract alpha channels as float
            src_alpha = image_region[:, :, 3:4] / 255.0
            dst_alpha = canvas_region[:, :, 3:4] / 255.0
            
            # Compute output alpha using "over" operator
            out_alpha = src_alpha + dst_alpha * (1 - src_alpha)
            
            # Avoid division by zero - where out_alpha is 0, the result should be transparent
            out_alpha_safe = np.where(out_alpha > 0, out_alpha, 1)
            
            # Blend RGB channels using proper alpha compositing
            blended_rgb = np.where(
                out_alpha > 0,
                (image_region[:, :, :3] * src_alpha + 
                 canvas_region[:, :, :3] * dst_alpha * (1 - src_alpha)) / out_alpha_safe,
                0  # Fully transparent pixels become black
            )
            
            # Update canvas with blended result
            canvas[start_y:end_y, start_x:end_x, :3] = blended_rgb.astype(np.uint8)
            canvas[start_y:end_y, start_x:end_x, 3] = (out_alpha[:, :, 0] * 255).astype(np.uint8)
        else:
            # No alpha in source, treat as opaque
            canvas[start_y:end_y, start_x:end_x, :3] = image_region
            canvas[start_y:end_y, start_x:end_x, 3] = 255  # Set alpha to opaque
    
    def fill_mouth_cavity(self, canvas, top_x, top_y, bottom_x, bottom_y, top_shape, bottom_shape):
        """Fill black cavity between separated mouth parts"""
        # Calculate the gap between top and bottom parts
        top_bottom = top_y + top_shape[0]
        gap_height = bottom_y - top_bottom
        
        if gap_height > 2:  # Only fill if there's a significant gap
            # Fill with dark color (mouth cavity)
            cavity_color = [20, 20, 20, 255]  # Dark gray, not pure black
            
            # Calculate fill region
            fill_left = min(top_x, bottom_x)
            fill_right = max(top_x + top_shape[1], bottom_x + bottom_shape[1])
            fill_top = top_bottom
            fill_bottom = bottom_y
            
            # Create oval-shaped fill for more natural look
            center_x = (fill_left + fill_right) // 2
            center_y = (fill_top + fill_bottom) // 2
            width = fill_right - fill_left
            height = fill_bottom - fill_top
            
            # Draw filled ellipse
            cv2.ellipse(canvas, (center_x, center_y), (width//2, height//2), 
                       0, 0, 360, cavity_color, -1)
    
    def composite_frame_with_jaw_slide(self, character_data, jaw_offset_y, debug=False):
        """Composite frame using nutcracker jaw vertical sliding"""
        
        if debug:
            print(f"Compositing nutcracker frame with jaw offset: {jaw_offset_y} pixels")
        
        # Get canvas dimensions
        canvas_width = character_data['video_width']
        canvas_height = character_data['video_height']
        scale_factor = character_data['scale_factor']
        padding = character_data['padding']
        
        # Create white background canvas
        frame = np.full((canvas_height, canvas_width, 4), [255, 255, 255, 255], dtype=np.uint8)
        
        # Scale the base face
        base_face_scaled = self.scale_image(character_data['base_face'], scale_factor)
        jaw_scaled = self.scale_image(character_data['jaw_image'], scale_factor)
        
        # Calculate positions
        char_width_scaled = int(character_data['width'] * scale_factor)
        char_height_scaled = int(character_data['height'] * scale_factor)
        
        base_x = (canvas_width - char_width_scaled) // 2
        base_y = padding['top']
        
        # Place base face
        self.paste_with_alpha(frame, base_face_scaled, base_x, base_y)
        
        # Calculate jaw position
        jaw_rect = character_data['jaw_rect']
        jaw_x_scaled = base_x + int(jaw_rect['x'] * scale_factor)
        jaw_y_scaled = base_y + int(jaw_rect['y'] * scale_factor)
        
        # Scale the offset for the current scale factor
        scaled_offset = int(jaw_offset_y * scale_factor)
        
        if jaw_offset_y > 0:
            # Add white background only behind the actual jaw cutout area
            jaw_rect = character_data['jaw_rect']
            cutout_x = base_x + int(jaw_rect['x'] * scale_factor)
            cutout_y = base_y + int(jaw_rect['y'] * scale_factor)
            cutout_w = int(jaw_rect['width'] * scale_factor)
            cutout_h = int(jaw_rect['height'] * scale_factor)
            
            # Fill only the exact cutout area with solid white background
            cv2.rectangle(frame, (cutout_x, cutout_y), 
                         (cutout_x + cutout_w, cutout_y + cutout_h),
                         [255, 255, 255, 255], -1)
            

        
        # Place jaw at vertically offset position (no rotation)
        self.paste_with_alpha(frame, jaw_scaled, jaw_x_scaled, jaw_y_scaled + scaled_offset)
        
        if debug:
            print(f"Jaw placed at: ({jaw_x_scaled}, {jaw_y_scaled + scaled_offset}) with offset: {scaled_offset} pixels")
        
        return frame