#!/usr/bin/env python3
"""
Command-line interface for testing South Park animation styles
Usage: python cli_test.py --style [standard|canadian] --image path/to/image.png --audio path/to/audio.wav
"""

import argparse
import os
import sys
from core.animator import TalkingHeadAnimator

def main():
    parser = argparse.ArgumentParser(description='South Park Talking Head Animator')
    parser.add_argument('--style', choices=['standard', 'canadian'], default='canadian',
                       help='Animation style: standard (sprite-based) or canadian (flappy-head)')
    parser.add_argument('--image', required=True, help='Path to character image')
    parser.add_argument('--audio', required=True, help='Path to audio file')
    parser.add_argument('--mouth-x', type=int, help='X coordinate for mouth anchor (standard style only)')
    parser.add_argument('--mouth-y', type=int, help='Y coordinate for mouth anchor (standard style only)')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        return 1
    
    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        return 1
    
    # Set up mouth anchor for standard style
    mouth_anchor = None
    if args.style == 'standard' and args.mouth_x is not None and args.mouth_y is not None:
        mouth_anchor = (args.mouth_x, args.mouth_y)
        print(f"Using manual mouth anchor: {mouth_anchor}")
    
    # Create animator and run
    print(f"Starting South Park animation...")
    print(f"Style: {args.style}")
    print(f"Image: {args.image}")
    print(f"Audio: {args.audio}")
    
    try:
        animator = TalkingHeadAnimator()
        output_path = animator.create_animation(
            image_path=args.image,
            audio_path=args.audio,
            style=args.style,
            mouth_anchor=mouth_anchor
        )
        
        print(f"\n✅ Animation completed successfully!")
        print(f"Output video: {output_path}")
        
        # Check output file
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"File size: {file_size} bytes")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Animation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())