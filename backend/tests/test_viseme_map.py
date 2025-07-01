#!/usr/bin/env python3
"""
Unit tests for South Park viseme mapping and sprite functionality
Tests the integration between Rhubarb viseme codes and mouth sprites
"""

import unittest
import os
import sys

# Add parent directory to path to import core modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.phoneme_detector import PhonemeDetector
from core.mouth_sprite_manager import MouthSpriteManager

class TestVisemeMapping(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.phoneme_detector = PhonemeDetector()
        self.sprite_manager = MouthSpriteManager()
    
    def test_rhubarb_viseme_mapping_complete(self):
        """Test that all Rhubarb viseme codes are mapped"""
        mapping = self.phoneme_detector.get_rhubarb_viseme_mapping()
        
        # Rhubarb uses these 9 viseme codes
        expected_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'X']
        
        for code in expected_codes:
            self.assertIn(code, mapping, f"Viseme code '{code}' is missing from mapping")
            self.assertIsNotNone(mapping[code], f"Viseme code '{code}' maps to None")
            self.assertIsInstance(mapping[code], str, f"Viseme code '{code}' should map to string")
    
    def test_sprite_files_exist(self):
        """Test that all required sprite files exist"""
        sprite_info = self.sprite_manager.get_sprite_info()
        
        # Should have sprites for all viseme codes
        expected_codes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'X']
        
        for code in expected_codes:
            self.assertIn(code, sprite_info, f"Sprite for viseme '{code}' not loaded")
            
            sprite_data = sprite_info[code]
            self.assertIn('name', sprite_data)
            self.assertIn('path', sprite_data)
            self.assertIn('size', sprite_data)
            
            # Check that sprite has reasonable dimensions
            height, width = sprite_data['size']
            self.assertGreater(height, 0, f"Sprite {code} has invalid height")
            self.assertGreater(width, 0, f"Sprite {code} has invalid width")
    
    def test_sprite_loading(self):
        """Test that sprites can be loaded for each viseme"""
        visemes = self.sprite_manager.get_available_visemes()
        
        for viseme in visemes:
            # Test getting sprite array
            sprite_array = self.sprite_manager.get_sprite_array(viseme)
            self.assertIsNotNone(sprite_array, f"Failed to get array for viseme {viseme}")
            self.assertEqual(len(sprite_array.shape), 3, f"Sprite {viseme} should be 3D array (H,W,C)")
            self.assertEqual(sprite_array.shape[2], 4, f"Sprite {viseme} should have 4 channels (RGBA)")
            
            # Test getting PIL image
            sprite_pil = self.sprite_manager.get_sprite_pil(viseme)
            self.assertIsNotNone(sprite_pil, f"Failed to get PIL image for viseme {viseme}")
    
    def test_sprite_scaling(self):
        """Test sprite scaling functionality"""
        # Test scaling by factor
        original = self.sprite_manager.get_sprite_array('A')
        scaled = self.sprite_manager.scale_sprite('A', scale_factor=2.0)
        
        self.assertEqual(scaled.shape[0], original.shape[0] * 2, "Height scaling failed")
        self.assertEqual(scaled.shape[1], original.shape[1] * 2, "Width scaling failed")
        
        # Test scaling to target size
        target_size = (80, 60)
        scaled_target = self.sprite_manager.scale_sprite('A', target_size=target_size)
        
        self.assertEqual(scaled_target.shape[1], target_size[0], "Target width scaling failed")
        self.assertEqual(scaled_target.shape[0], target_size[1], "Target height scaling failed")
    
    def test_viseme_mapping_consistency(self):
        """Test that phoneme detector and sprite manager mappings are consistent"""
        phoneme_mapping = self.phoneme_detector.get_rhubarb_viseme_mapping()
        sprite_mapping = self.sprite_manager.sprite_mapping
        
        # Both should have the same viseme codes
        phoneme_codes = set(phoneme_mapping.keys())
        sprite_codes = set(sprite_mapping.keys())
        
        self.assertEqual(phoneme_codes, sprite_codes, 
                        "Phoneme detector and sprite manager have different viseme codes")
        
        # Each sprite referenced in phoneme mapping should exist
        for viseme_code, sprite_name in phoneme_mapping.items():
            expected_sprite = sprite_mapping[viseme_code]
            self.assertEqual(sprite_name, expected_sprite,
                           f"Inconsistent sprite mapping for viseme {viseme_code}")
    
    def test_fallback_viseme(self):
        """Test fallback behavior for unknown visemes"""
        # Test with an invalid viseme code
        fallback_sprite = self.sprite_manager.get_sprite_for_viseme('INVALID')
        silence_sprite = self.sprite_manager.get_sprite_for_viseme('X')
        
        # Should fall back to silence sprite
        self.assertEqual(fallback_sprite['name'], silence_sprite['name'],
                        "Invalid viseme should fall back to silence sprite")

class TestSpriteGeneration(unittest.TestCase):
    
    def test_sprite_files_created(self):
        """Test that all expected sprite files were created"""
        sprites_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'mouth_sprites')
        
        expected_files = [
            'southparkClosed(M_B_P).png',
            'southparkSmall(E_I).png',
            'southparkMedium(E_EH).png',
            'southparkWide(A_AH).png',
            'southparkRound(O_OO).png',
            'southparkTeeth(F_V).png',
            'southparkSpecial(L_TH_R).png'
        ]
        
        for filename in expected_files:
            file_path = os.path.join(sprites_dir, filename)
            self.assertTrue(os.path.exists(file_path), f"Sprite file missing: {filename}")
            
            # Check file is not empty
            file_size = os.path.getsize(file_path)
            self.assertGreater(file_size, 0, f"Sprite file is empty: {filename}")

if __name__ == '__main__':
    unittest.main()