#!/usr/bin/env python3
"""
Generate South Park style mouth sprites programmatically
Creates the 7 required mouth shapes for standard lip-sync animation
"""

from PIL import Image, ImageDraw
import os

class SouthParkMouthGenerator:
    def __init__(self, sprite_size=(80, 60)):  # Increased from 60x40 to 80x60
        self.sprite_size = sprite_size
        self.width, self.height = sprite_size
        
        # South Park color palette
        self.colors = {
            'mouth_interior': (30, 30, 30, 255),      # Dark mouth interior
            'teeth': (255, 255, 255, 255),            # White teeth
            'lips': (180, 120, 90, 255),              # Flesh-toned lips
            'tongue': (200, 100, 100, 255),           # Pink tongue
            'transparent': (0, 0, 0, 0)               # Transparent background
        }
    
    def create_base_image(self):
        """Create transparent base image"""
        return Image.new('RGBA', self.sprite_size, self.colors['transparent'])
    
    def generate_closed_mouth(self):
        """Generate closed mouth sprite (A viseme - M, B, P sounds)"""
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Draw simple horizontal line for closed mouth
        line_y = self.height // 2
        line_thickness = 2
        
        # Lips line
        draw.rectangle([
            self.width // 4, line_y - line_thickness//2,
            3 * self.width // 4, line_y + line_thickness//2
        ], fill=self.colors['lips'])
        
        return img
    
    def generate_small_opening(self):
        """Generate small mouth opening (B viseme - E, I sounds)"""
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Small oval opening
        center_x, center_y = self.width // 2, self.height // 2
        oval_width, oval_height = 16, 8
        
        # Dark interior
        draw.ellipse([
            center_x - oval_width//2, center_y - oval_height//2,
            center_x + oval_width//2, center_y + oval_height//2
        ], fill=self.colors['mouth_interior'])
        
        # Lip outline
        draw.ellipse([
            center_x - oval_width//2 - 2, center_y - oval_height//2 - 1,
            center_x + oval_width//2 + 2, center_y + oval_height//2 + 1
        ], outline=self.colors['lips'], width=2)
        
        return img
    
    def generate_medium_opening(self):
        """Generate medium mouth opening (C viseme - E, EH sounds)"""
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Medium oval opening
        center_x, center_y = self.width // 2, self.height // 2
        oval_width, oval_height = 24, 16
        
        # Dark interior
        draw.ellipse([
            center_x - oval_width//2, center_y - oval_height//2,
            center_x + oval_width//2, center_y + oval_height//2
        ], fill=self.colors['mouth_interior'])
        
        # Lip outline
        draw.ellipse([
            center_x - oval_width//2 - 2, center_y - oval_height//2 - 1,
            center_x + oval_width//2 + 2, center_y + oval_height//2 + 1
        ], outline=self.colors['lips'], width=2)
        
        return img
    
    def generate_wide_opening(self):
        """Generate wide mouth opening (D viseme - A, AH sounds)"""
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Wide oval opening
        center_x, center_y = self.width // 2, self.height // 2
        oval_width, oval_height = 32, 20
        
        # Dark interior
        draw.ellipse([
            center_x - oval_width//2, center_y - oval_height//2,
            center_x + oval_width//2, center_y + oval_height//2
        ], fill=self.colors['mouth_interior'])
        
        # Bottom teeth (just a hint)
        teeth_y = center_y + oval_height//4
        draw.rectangle([
            center_x - oval_width//3, teeth_y,
            center_x + oval_width//3, teeth_y + 3
        ], fill=self.colors['teeth'])
        
        # Lip outline
        draw.ellipse([
            center_x - oval_width//2 - 2, center_y - oval_height//2 - 1,
            center_x + oval_width//2 + 2, center_y + oval_height//2 + 1
        ], outline=self.colors['lips'], width=2)
        
        return img
    
    def generate_round_opening(self):
        """Generate round mouth opening (E viseme - O, OO sounds)"""
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Round circular opening
        center_x, center_y = self.width // 2, self.height // 2
        radius = 12
        
        # Dark interior
        draw.ellipse([
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        ], fill=self.colors['mouth_interior'])
        
        # Lip outline (slightly larger circle)
        draw.ellipse([
            center_x - radius - 2, center_y - radius - 2,
            center_x + radius + 2, center_y + radius + 2
        ], outline=self.colors['lips'], width=3)
        
        return img
    
    def generate_teeth_showing(self):
        """Generate mouth with teeth showing (F viseme - F, V sounds)"""
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Horizontal opening showing teeth
        center_x, center_y = self.width // 2, self.height // 2
        mouth_width, mouth_height = 28, 12
        
        # Dark interior
        draw.rectangle([
            center_x - mouth_width//2, center_y - mouth_height//2,
            center_x + mouth_width//2, center_y + mouth_height//2
        ], fill=self.colors['mouth_interior'])
        
        # Top teeth
        teeth_height = 4
        draw.rectangle([
            center_x - mouth_width//2 + 2, center_y - mouth_height//2,
            center_x + mouth_width//2 - 2, center_y - mouth_height//2 + teeth_height
        ], fill=self.colors['teeth'])
        
        # Bottom teeth
        draw.rectangle([
            center_x - mouth_width//2 + 2, center_y + mouth_height//2 - teeth_height,
            center_x + mouth_width//2 - 2, center_y + mouth_height//2
        ], fill=self.colors['teeth'])
        
        # Lip outline
        draw.rectangle([
            center_x - mouth_width//2 - 2, center_y - mouth_height//2 - 1,
            center_x + mouth_width//2 + 2, center_y + mouth_height//2 + 1
        ], outline=self.colors['lips'], width=2)
        
        return img
    
    def generate_special_shape(self):
        """Generate special mouth shape (G viseme - L, TH, R sounds)"""
        img = self.create_base_image()
        draw = ImageDraw.Draw(img)
        
        # Asymmetric opening for consonants
        center_x, center_y = self.width // 2, self.height // 2
        
        # Create irregular shape for tongue/consonant position
        points = [
            (center_x - 10, center_y - 6),
            (center_x + 14, center_y - 4),
            (center_x + 12, center_y + 8),
            (center_x - 8, center_y + 6)
        ]
        
        # Dark interior
        draw.polygon(points, fill=self.colors['mouth_interior'])
        
        # Hint of tongue for L/R sounds
        tongue_points = [
            (center_x - 4, center_y),
            (center_x + 6, center_y - 2),
            (center_x + 4, center_y + 4),
            (center_x - 2, center_y + 2)
        ]
        draw.polygon(tongue_points, fill=self.colors['tongue'])
        
        # Lip outline
        draw.polygon(points, outline=self.colors['lips'], width=2)
        
        return img
    
    def generate_all_sprites(self, output_dir):
        """Generate all 7 mouth sprites and save them"""
        sprites = {
            'southparkClosed(M_B_P)': self.generate_closed_mouth(),
            'southparkSmall(E_I)': self.generate_small_opening(),
            'southparkMedium(E_EH)': self.generate_medium_opening(),
            'southparkWide(A_AH)': self.generate_wide_opening(),
            'southparkRound(O_OO)': self.generate_round_opening(),
            'southparkTeeth(F_V)': self.generate_teeth_showing(),
            'southparkSpecial(L_TH_R)': self.generate_special_shape()
        }
        
        os.makedirs(output_dir, exist_ok=True)
        
        for name, sprite in sprites.items():
            file_path = os.path.join(output_dir, f"{name}.png")
            sprite.save(file_path)
            print(f"Generated: {file_path}")
        
        print(f"\nAll {len(sprites)} mouth sprites generated successfully!")
        return list(sprites.keys())

if __name__ == "__main__":
    # Generate sprites
    generator = SouthParkMouthGenerator()
    output_directory = os.path.join(os.path.dirname(__file__), '..', 'assets', 'mouth_sprites')
    sprite_names = generator.generate_all_sprites(output_directory)
    
    print(f"\nSprite files created in: {output_directory}")
    for name in sprite_names:
        print(f"  - {name}.png")