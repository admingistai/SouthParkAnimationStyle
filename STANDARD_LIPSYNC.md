# South Park Standard Lip-Sync Implementation

This document describes the standard South Park mouth-sprite lip-sync functionality that has been added to the talking head animator.

## Overview

The animator now supports two animation styles:

1. **Canadian Style** (`style='canadian'`) - The original flappy-head animation where the character's head splits and moves
2. **Standard Style** (`style='standard'`) - Traditional sprite-based lip-sync using mouth shape overlays

## New Features

### Mouth Sprite System

- **7 South Park mouth sprites** programmatically generated:
  - `southparkClosed(M_B_P)` - Closed mouth for M, B, P sounds
  - `southparkSmall(E_I)` - Small opening for E, I sounds  
  - `southparkMedium(E_EH)` - Medium opening for E, EH sounds
  - `southparkWide(A_AH)` - Wide opening for A, AH sounds
  - `southparkRound(O_OO)` - Round shape for O, OO sounds
  - `southparkTeeth(F_V)` - Teeth showing for F, V sounds
  - `southparkSpecial(L_TH_R)` - Special shape for L, TH, R sounds

### Enhanced Phoneme Detection

- **Rhubarb Lip Sync integration** for accurate viseme detection
- **Viseme mapping** from Rhubarb's 8-letter codes (A-H, X) to sprite names
- **Fallback system** using amplitude-based detection when Rhubarb unavailable

### Automatic Mouth Positioning

- **Intelligent mouth detection** for optimal sprite placement
- **Proportional sprite sizing** based on character dimensions
- **Manual override** option for precise mouth positioning

## Usage

### Command Line Interface

```bash
# Standard sprite-based animation
python cli_test.py --style standard --image character.png --audio speech.wav

# Canadian flappy-head animation (original)
python cli_test.py --style canadian --image character.png --audio speech.wav

# Standard with manual mouth positioning
python cli_test.py --style standard --image character.png --audio speech.wav --mouth-x 150 --mouth-y 200
```

### Python API

```python
from core.animator import TalkingHeadAnimator

animator = TalkingHeadAnimator()

# Standard sprite-based animation
output_path = animator.create_animation(
    image_path='character.png',
    audio_path='speech.wav',
    style='standard'
)

# With manual mouth positioning
output_path = animator.create_animation(
    image_path='character.png',
    audio_path='speech.wav',
    style='standard',
    mouth_anchor=(150, 200)  # (x, y) coordinates
)

# Canadian flappy-head animation
output_path = animator.create_animation(
    image_path='character.png',
    audio_path='speech.wav',
    style='canadian'
)
```

## Technical Details

### Architecture

- **MouthSpriteManager** - Handles sprite loading, caching, and scaling
- **Enhanced ImageProcessor** - Supports both sprite compositing and head splitting
- **Dual-mode VideoRenderer** - Renders both sprite-based and movement-based animations
- **Flexible Animator** - Orchestrates the entire pipeline with style switching

### Rhubarb Viseme Mapping

| Rhubarb Code | Sprite Name | Sounds |
|--------------|-------------|---------|
| A | southparkClosed | M, B, P |
| B | southparkSmall | E, I |
| C | southparkMedium | E, EH |
| D | southparkWide | A, AH |
| E | southparkRound | O, OO |
| F | southparkTeeth | F, V |
| G | southparkSpecial | L, TH, R |
| H | southparkWide | Other vowels |
| X | southparkClosed | Silence |

### Performance

- **Sprite caching** for fast frame rendering
- **Nearest-neighbor scaling** preserves pixel art aesthetic
- **Optimized compositing** using alpha blending
- **Target: <8ms per frame** on modern hardware

## File Structure

```
backend/
├── core/
│   ├── animator.py              # Main animation orchestrator
│   ├── phoneme_detector.py      # Rhubarb integration & viseme mapping
│   ├── image_processor.py       # Sprite compositing & head splitting
│   ├── video_renderer.py        # Dual-mode video rendering
│   ├── mouth_sprite_manager.py  # Sprite loading & management
│   └── generate_mouth_sprites.py # Sprite generation utility
├── assets/
│   └── mouth_sprites/           # Generated South Park mouth sprites
├── tests/
│   └── test_viseme_map.py       # Unit tests for viseme mapping
└── cli_test.py                  # Command-line testing interface
```

## Testing

Run the unit tests to verify functionality:

```bash
cd backend
python tests/test_viseme_map.py
```

All tests should pass, confirming:
- ✅ Complete viseme mapping (A-H, X)
- ✅ All sprite files loaded successfully
- ✅ Sprite scaling functionality
- ✅ Mapping consistency between components
- ✅ Fallback behavior for invalid visemes

## Backward Compatibility

The original Canadian flappy-head animation remains fully functional. All existing code and APIs continue to work unchanged by default (`style='canadian'`).

## Dependencies

- **PIL (Pillow)** - Image processing and sprite generation
- **OpenCV** - Video rendering and image manipulation
- **NumPy** - Array operations and compositing
- **Rhubarb Lip Sync** - Advanced phoneme detection (optional)
- **pydub** - Audio format conversion
- **ffmpeg** - Video encoding and audio synchronization

## Future Enhancements

- Custom sprite sets for different character styles
- Web interface for mouth positioning
- Batch processing for multiple characters
- Advanced phoneme timing adjustments
- Character-specific mouth scaling presets