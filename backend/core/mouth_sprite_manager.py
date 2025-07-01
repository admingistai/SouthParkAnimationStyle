"""
Mouth Sprite Manager for South Park Standard Lip-Sync Animation
Handles loading, caching, and management of mouth sprite images
"""

import os
from PIL import Image
import numpy as np
import cv2

class MouthSpriteManager:
    def __init__(self, sprites_dir=None):
        if sprites_dir is None:
            sprites_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'mouth_sprites')
        
        self.sprites_dir = sprites_dir
        self.sprite_cache = {}
        self.sprite_mapping = {
            'A': 'southparkClosed(M_B_P)',
            'B': 'southparkSmall(E_I)',
            'C': 'southparkMedium(E_EH)',
            'D': 'southparkWide(A_AH)',
            'E': 'southparkRound(O_OO)',
            'F': 'southparkTeeth(F_V)',
            'G': 'southparkSpecial(L_TH_R)',
            'H': 'southparkWide(A_AH)',  # Use wide for other vowels
            'X': 'southparkClosed(M_B_P)'  # Use closed for silence
        }
        
        # Pre-load all sprites
        self._load_all_sprites()
    
    def _load_all_sprites(self):
        """Pre-load all mouth sprites into cache"""
        print(f"Loading mouth sprites from: {self.sprites_dir}")
        
        if not os.path.exists(self.sprites_dir):
            raise Exception(f"Sprites directory not found: {self.sprites_dir}")
        
        for viseme_code, sprite_name in self.sprite_mapping.items():
            sprite_path = os.path.join(self.sprites_dir, f"{sprite_name}.png")
            
            if os.path.exists(sprite_path):
                try:
                    # Load with PIL (maintains alpha channel)
                    pil_image = Image.open(sprite_path).convert('RGBA')
                    
                    # Convert to numpy array for OpenCV compatibility
                    sprite_array = np.array(pil_image)
                    
                    # Store both PIL and array versions
                    self.sprite_cache[viseme_code] = {
                        'pil': pil_image,
                        'array': sprite_array,
                        'path': sprite_path,
                        'name': sprite_name
                    }
                    
                    print(f"Loaded sprite {viseme_code}: {sprite_name}")
                    
                except Exception as e:
                    print(f"Error loading sprite {sprite_path}: {e}")
                    # Create a fallback sprite
                    self.sprite_cache[viseme_code] = self._create_fallback_sprite(viseme_code)
            else:
                print(f"Sprite file not found: {sprite_path}")
                # Create a fallback sprite
                self.sprite_cache[viseme_code] = self._create_fallback_sprite(viseme_code)
        
        print(f"Loaded {len(self.sprite_cache)} mouth sprites")
    
    def _create_fallback_sprite(self, viseme_code):
        """Create a simple fallback sprite if file loading fails"""
        # Create a 60x40 transparent image with colored rectangle
        size = (60, 40)
        fallback = Image.new('RGBA', size, (0, 0, 0, 0))
        
        # Add colored rectangle based on viseme
        colors = {
            'A': (255, 0, 0, 128),      # Red for closed
            'B': (0, 255, 0, 128),      # Green for small
            'C': (0, 0, 255, 128),      # Blue for medium
            'D': (255, 255, 0, 128),    # Yellow for wide
            'E': (255, 0, 255, 128),    # Magenta for round
            'F': (0, 255, 255, 128),    # Cyan for teeth
            'G': (128, 128, 128, 128),  # Gray for special
            'H': (255, 128, 0, 128),    # Orange for H
            'X': (64, 64, 64, 128)      # Dark gray for silence
        }
        
        color = colors.get(viseme_code, (128, 128, 128, 128))
        
        from PIL import ImageDraw
        draw = ImageDraw.Draw(fallback)
        draw.rectangle([10, 15, 50, 25], fill=color)
        
        return {
            'pil': fallback,
            'array': np.array(fallback),
            'path': f'fallback_{viseme_code}',
            'name': f'fallback_{viseme_code}'
        }
    
    def get_sprite_for_viseme(self, viseme_code):
        """Get sprite data for a given viseme code"""
        return self.sprite_cache.get(viseme_code, self.sprite_cache.get('X'))
    
    def get_sprite_array(self, viseme_code):
        """Get numpy array version of sprite"""
        sprite_data = self.get_sprite_for_viseme(viseme_code)
        return sprite_data['array']
    
    def get_sprite_pil(self, viseme_code):
        """Get PIL Image version of sprite"""
        sprite_data = self.get_sprite_for_viseme(viseme_code)
        return sprite_data['pil']
    
    def scale_sprite(self, viseme_code, scale_factor=1.0, target_size=None):
        """Get scaled version of sprite"""
        if scale_factor == 1.0 and target_size is None:
            return self.get_sprite_array(viseme_code)
        
        sprite_array = self.get_sprite_array(viseme_code)
        
        if target_size is not None:
            # Scale to specific size
            width, height = target_size
            scaled = cv2.resize(sprite_array, (width, height), interpolation=cv2.INTER_NEAREST)
        else:
            # Scale by factor
            original_height, original_width = sprite_array.shape[:2]
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            scaled = cv2.resize(sprite_array, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
        
        return scaled
    
    def get_available_visemes(self):
        """Get list of available viseme codes"""
        return list(self.sprite_cache.keys())
    
    def get_sprite_info(self):
        """Get information about loaded sprites"""
        info = {}
        for viseme_code, sprite_data in self.sprite_cache.items():
            info[viseme_code] = {
                'name': sprite_data['name'],
                'path': sprite_data['path'],
                'size': sprite_data['array'].shape[:2]  # (height, width)
            }
        return info
    
    def detect_mouth_region_size(self, character_image_array, mouth_anchor):
        """
        Detect appropriate mouth sprite size based on character proportions
        Returns (width, height) for sprite scaling
        """
        char_height, char_width = character_image_array.shape[:2]
        
        # Make mouth sprites larger and more visible
        # South Park characters need prominent mouth movement
        suggested_width = max(40, min(120, char_width // 4))  # Increased from 1/8 to 1/4
        suggested_height = max(30, min(80, char_height // 8))  # Increased from 1/12 to 1/8
        
        return (suggested_width, suggested_height)
    
    def find_optimal_mouth_position(self, character_image_array, approximate_anchor=None):
        """
        Find the optimal position for mouth sprite placement using head-focused detection
        Returns (x, y) coordinates for sprite center
        """
        if approximate_anchor is not None:
            return approximate_anchor
        
        print("🔍 Analyzing character for optimal mouth placement...")
        
        # Step 1: Detect and isolate the head region
        head_region = self._detect_head_region(character_image_array)
        
        if head_region is None:
            print("⚠️ Could not detect head region, using fallback")
            return self._fallback_mouth_position(character_image_array)
        
        # Step 2: Find mouth position within the head region
        head_mouth_x, head_mouth_y = self._find_mouth_in_head(head_region, character_image_array)
        
        print(f"🎯 Final mouth position: ({head_mouth_x}, {head_mouth_y})")
        return (int(head_mouth_x), int(head_mouth_y))
    
    def _find_character_center_mass(self, image_array):
        """Find the center of mass of non-transparent pixels"""
        # Get alpha channel
        if image_array.shape[2] == 4:
            alpha = image_array[:, :, 3]
        else:
            alpha = np.ones(image_array.shape[:2], dtype=np.uint8) * 255
        
        # Find non-transparent pixels
        y_coords, x_coords = np.where(alpha > 50)  # Threshold for semi-transparent
        
        if len(x_coords) > 0 and len(y_coords) > 0:
            center_x = int(np.mean(x_coords))
            center_y = int(np.mean(y_coords))
        else:
            # Fallback to image center
            center_x = image_array.shape[1] // 2
            center_y = image_array.shape[0] // 2
        
        print(f"📍 Character center mass: ({center_x}, {center_y})")
        return center_x, center_y
    
    def _detect_mouth_features(self, image_array):
        """Detect potential mouth features using edge detection"""
        import cv2
        
        # Convert to grayscale for feature detection
        if image_array.shape[2] == 4:
            # Handle RGBA
            gray = cv2.cvtColor(image_array[:, :, :3], cv2.COLOR_RGB2GRAY)
            mask = image_array[:, :, 3] > 50  # Use alpha as mask
        else:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            mask = np.ones(gray.shape, dtype=bool)
        
        # Apply mask to focus on character
        gray[~mask] = 255  # Set transparent areas to white
        
        # Edge detection to find features
        edges = cv2.Canny(gray, 50, 150)
        
        # Look for horizontal line features (potential mouths)
        mouth_candidates = []
        height, width = edges.shape
        
        # Focus on lower 60% of character
        start_y = int(height * 0.4)
        
        for y in range(start_y, height - 10):
            # Count horizontal edge pixels in this row
            row_edges = np.sum(edges[y, :])
            
            # Look for moderate edge activity (not too much, not too little)
            if 5 < row_edges < width * 0.3:
                # Check if this could be a mouth (some width, not too wide)
                edge_pixels = np.where(edges[y, :] > 0)[0]
                if len(edge_pixels) > 10:  # Minimum mouth width
                    mouth_center_x = int(np.mean(edge_pixels))
                    mouth_candidates.append((mouth_center_x, y, row_edges))
        
        # Sort by edge strength and position
        mouth_candidates.sort(key=lambda x: (x[2], -x[1]))  # Prefer stronger edges, lower position
        
        if mouth_candidates:
            print(f"👄 Found {len(mouth_candidates)} mouth candidates")
            return mouth_candidates[-3:]  # Return top 3 candidates
        else:
            print("🔍 No clear mouth features detected")
            return []
    
    def _estimate_mouth_from_proportions(self, image_array, center_y):
        """Estimate mouth position based on typical face proportions"""
        char_height, char_width = image_array.shape[:2]
        
        # Find the character's bounding box
        if image_array.shape[2] == 4:
            alpha = image_array[:, :, 3]
            y_coords, x_coords = np.where(alpha > 50)
        else:
            # For RGB images, find non-white pixels
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            y_coords, x_coords = np.where(gray < 240)
        
        if len(y_coords) > 0:
            char_top = np.min(y_coords)
            char_bottom = np.max(y_coords)
            char_height_actual = char_bottom - char_top
            
            # Mouth is typically 70-80% down from the top of the head
            mouth_y = char_top + int(char_height_actual * 0.75)
            
            print(f"📏 Character bounds: top={char_top}, bottom={char_bottom}")
            print(f"📐 Proportion-based mouth Y: {mouth_y}")
            
            return mouth_y
        else:
            # Fallback
            return int(char_height * 0.75)

    def _detect_head_region(self, image_array):
        """
        Detect the head region of a South Park character using multiple methods
        Returns head region info: {'top': y, 'bottom': y, 'left': x, 'right': x, 'center': (x, y)}
        """
        print("🔍 Detecting head region...")
        
        # Method 1: Color-based skin detection
        head_by_color = self._detect_head_by_skin_color(image_array)
        
        # Method 2: Shape analysis (circular/round shapes)
        head_by_shape = self._detect_head_by_shape(image_array)
        
        # Method 3: Proportion-based (top portion of character)
        head_by_proportion = self._detect_head_by_proportion(image_array)
        
        # Combine results and choose the best
        candidates = [head_by_color, head_by_shape, head_by_proportion]
        valid_candidates = [c for c in candidates if c is not None]
        
        if valid_candidates:
            # Use the head region that's highest up (most likely to be actual head)
            best_head = min(valid_candidates, key=lambda h: h['top'])
            print(f"✅ Selected head region: top={best_head['top']}, center={best_head['center']}")
            return best_head
        else:
            print("⚠️ No valid head region detected")
            return None
    
    def _detect_head_by_skin_color(self, image_array):
        """Detect head region by finding skin-colored areas"""
        try:
            # Convert to HSV for better color detection
            if image_array.shape[2] == 4:
                rgb_image = image_array[:, :, :3]
                alpha = image_array[:, :, 3]
                mask = alpha > 50
            else:
                rgb_image = image_array
                mask = np.ones(image_array.shape[:2], dtype=bool)
            
            hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)
            
            # South Park skin tone ranges (wider range to catch different characters)
            # Hue: 5-25 (yellow-orange range), Saturation: 30-255, Value: 100-255
            lower_skin = np.array([5, 30, 100])
            upper_skin = np.array([25, 255, 255])
            
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_mask = skin_mask & mask.astype(np.uint8) * 255
            
            # Find contours in skin-colored regions
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest skin-colored region (likely the face)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Validate this looks like a head (reasonable proportions)
                if w > 50 and h > 50 and 0.7 <= w/h <= 1.5:  # Roughly square-ish
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    print(f"🎨 Skin-based head: ({x}, {y}) -> ({x+w}, {y+h}), center=({center_x}, {center_y})")
                    
                    return {
                        'top': y,
                        'bottom': y + h,
                        'left': x,
                        'right': x + w,
                        'center': (center_x, center_y),
                        'method': 'skin_color'
                    }
            
            print("🎨 No valid skin regions found")
            return None
            
        except Exception as e:
            print(f"🎨 Skin detection failed: {e}")
            return None
    
    def _detect_head_by_shape(self, image_array):
        """Detect head region by finding circular/round shapes"""
        try:
            # Convert to grayscale
            if image_array.shape[2] == 4:
                gray = cv2.cvtColor(image_array[:, :, :3], cv2.COLOR_RGB2GRAY)
                alpha = image_array[:, :, 3]
                mask = alpha > 50
            else:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
                mask = np.ones(gray.shape, dtype=bool)
            
            # Apply mask
            gray[~mask] = 255
            
            # Find contours
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            head_candidates = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 1000:  # Too small to be a head
                    continue
                
                # Check if shape is roughly circular
                perimeter = cv2.arcLength(contour, True)
                if perimeter == 0:
                    continue
                    
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                
                if circularity > 0.4:  # Reasonably circular
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Should be in upper portion of image and reasonable size
                    if y < image_array.shape[0] * 0.6 and w > 60 and h > 60:
                        center_x = x + w // 2
                        center_y = y + h // 2
                        
                        head_candidates.append({
                            'top': y,
                            'bottom': y + h,
                            'left': x,
                            'right': x + w,
                            'center': (center_x, center_y),
                            'circularity': circularity,
                            'area': area
                        })
            
            if head_candidates:
                # Choose the most circular one in the upper part
                best_head = max(head_candidates, key=lambda h: h['circularity'])
                best_head['method'] = 'shape_analysis'
                
                print(f"🔵 Shape-based head: center={best_head['center']}, circularity={best_head['circularity']:.2f}")
                return best_head
            
            print("🔵 No circular head shapes found")
            return None
            
        except Exception as e:
            print(f"🔵 Shape detection failed: {e}")
            return None
    
    def _detect_head_by_proportion(self, image_array):
        """Detect head region by assuming it's in the top portion of the character"""
        try:
            char_height, char_width = image_array.shape[:2]
            
            # Find character bounds
            if image_array.shape[2] == 4:
                alpha = image_array[:, :, 3]
                y_coords, x_coords = np.where(alpha > 50)
            else:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
                y_coords, x_coords = np.where(gray < 240)
            
            if len(y_coords) == 0:
                return None
            
            char_top = np.min(y_coords)
            char_bottom = np.max(y_coords)
            char_left = np.min(x_coords)
            char_right = np.max(x_coords)
            
            char_height_actual = char_bottom - char_top
            char_width_actual = char_right - char_left
            
            # Head is typically the top 40-50% of a South Park character
            head_height = int(char_height_actual * 0.45)
            head_top = char_top
            head_bottom = char_top + head_height
            
            # Head width is usually 70-90% of character width, centered
            head_width = int(char_width_actual * 0.8)
            char_center_x = (char_left + char_right) // 2
            head_left = char_center_x - head_width // 2
            head_right = char_center_x + head_width // 2
            
            center_x = (head_left + head_right) // 2
            center_y = (head_top + head_bottom) // 2
            
            print(f"📐 Proportion-based head: top={head_top}, center=({center_x}, {center_y})")
            
            return {
                'top': head_top,
                'bottom': head_bottom,
                'left': head_left,
                'right': head_right,
                'center': (center_x, center_y),
                'method': 'proportion'
            }
            
        except Exception as e:
            print(f"📐 Proportion detection failed: {e}")
            return None
    
    def _find_mouth_in_head(self, head_region, full_image):
        """Find mouth position within the detected head region"""
        head_center_x, head_center_y = head_region['center']
        head_height = head_region['bottom'] - head_region['top']
        
        # Mouth is typically 70-85% down from top of head
        mouth_offset_y = int(head_height * 0.78)
        mouth_y = head_region['top'] + mouth_offset_y
        
        # Mouth X is usually centered horizontally with the head
        mouth_x = head_center_x
        
        print(f"👄 Head-relative mouth position: ({mouth_x}, {mouth_y})")
        print(f"🔍 Head region used: {head_region['method']}")
        
        return mouth_x, mouth_y
    
    def _fallback_mouth_position(self, image_array):
        """Fallback method when head detection fails"""
        char_height, char_width = image_array.shape[:2]
        
        # Find character bounds
        if image_array.shape[2] == 4:
            alpha = image_array[:, :, 3]
            y_coords, x_coords = np.where(alpha > 50)
        else:
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            y_coords, x_coords = np.where(gray < 240)
        
        if len(y_coords) > 0:
            char_top = np.min(y_coords)
            char_left = np.min(x_coords)
            char_right = np.max(x_coords)
            char_height_actual = np.max(y_coords) - char_top
            
            # Conservative estimate: mouth at 60% down from character top
            mouth_y = char_top + int(char_height_actual * 0.6)
            mouth_x = (char_left + char_right) // 2
            
            print(f"🔧 Fallback mouth position: ({mouth_x}, {mouth_y})")
            return mouth_x, mouth_y
        else:
            # Ultimate fallback
            return char_width // 2, int(char_height * 0.6)