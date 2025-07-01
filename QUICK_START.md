# South Park Animator - Quick Start Guide

## ✅ Setup Complete!

Your South Park animator is ready to use with both animation styles:

### 🎭 Animation Styles Available

1. **Standard Style** - Traditional sprite-based lip-sync (like Stan, Kyle, etc.)
2. **Canadian Style** - Flappy-head animation (like Terrance & Phillip)

## 🚀 Quick Usage

### Command Line Interface

```bash
# Standard sprite-based animation
python backend/cli_test.py --style standard --image path/to/character.png --audio path/to/speech.wav

# Canadian flappy-head animation  
python backend/cli_test.py --style canadian --image path/to/character.png --audio path/to/speech.wav

# Standard with manual mouth positioning
python backend/cli_test.py --style standard --image character.png --audio speech.wav --mouth-x 150 --mouth-y 200
```

### Python API

```python
from backend.core.animator import TalkingHeadAnimator

# Create animator
animator = TalkingHeadAnimator()

# Standard sprite-based animation
output_path = animator.create_animation(
    image_path='character.png',
    audio_path='speech.wav', 
    style='standard'
)

# Canadian flappy-head animation
output_path = animator.create_animation(
    image_path='character.png',
    audio_path='speech.wav',
    style='canadian'
)

print(f"Animation saved to: {output_path}")
```

## 📁 Project Structure

```
southpark-animator/
├── backend/
│   ├── core/                    # Core animation modules
│   ├── assets/mouth_sprites/    # 7 South Park mouth sprites
│   ├── tests/                   # Unit tests
│   ├── temp/                    # Temporary files
│   └── output/                  # Generated videos
├── requirements.txt             # Python dependencies
├── check_setup.py              # Setup verification
├── cli_test.py                  # Command-line interface
└── STANDARD_LIPSYNC.md         # Detailed documentation
```

## 🎬 What You Need

### Input Files
- **Character Image**: PNG with transparent background (recommended)
- **Audio File**: WAV, MP3, or other formats supported by pydub

### Supported Formats
- **Images**: PNG, JPG, JPEG, BMP
- **Audio**: WAV, MP3, M4A, OGG, FLAC
- **Output**: MP4 video with H.264 encoding

## 🔧 Advanced Options

### Hybrid Mouth Detection System
The animator now features an intelligent hybrid mouth detection system:

- **Automatic Face Type Detection**: Distinguishes between cartoon and realistic faces
- **Facial Landmark Support**: Can use dlib/MediaPipe for accurate mouth detection on realistic faces
- **Smart Positioning**: 
  - Cartoon faces: Mouth at 78% down from top of head
  - Realistic faces: Mouth at 68% down from top of head
- **Multiple Detection Methods**: Color-based, shape-based, and proportion-based head detection

To enable facial landmark detection for realistic faces:
```bash
pip install dlib mediapipe
# Download shape predictor from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
```

### Manual Mouth Positioning (Standard Style)
If automatic mouth detection isn't perfect, specify exact coordinates:

```bash
python backend/cli_test.py --style standard --image character.png --audio speech.wav --mouth-x 150 --mouth-y 200
```

### Environment Variables
- `SOUTH_PARK_FPS`: Frame rate (default: 24)
- `RHUBARB_PATH`: Custom path to Rhubarb executable

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Run setup check
python check_setup.py

# Run unit tests
python backend/tests/test_viseme_map.py

# Or with pytest
cd backend && python -m pytest tests/ -v
```

## 🎯 Tips for Best Results

### Character Images
- Use high-resolution images (512x512 or larger)
- Ensure character faces camera directly
- Clean, simple backgrounds work best
- PNG with transparency recommended

### Audio Files
- Clear speech with minimal background noise
- 16-44kHz sample rate recommended
- Mono or stereo both supported

### Animation Styles
- **Standard**: Best for main characters, clear speech
- **Canadian**: Best for comedy, exaggerated effects

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **FFmpeg errors**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```

3. **Rhubarb not found (optional)**
   - Download from: https://github.com/DanielSWolf/rhubarb-lip-sync
   - Place in `backend/models/rhubarb`
   - Or use fallback amplitude-based detection

4. **Empty video output**
   - Check input file formats
   - Verify image has content
   - Check audio file duration

### Performance Tips
- Use smaller images for faster processing
- Standard style is more CPU efficient than Canadian
- Consider batch processing for multiple files

## 📊 Output

Generated videos are saved to `backend/output/` with names like:
- `talking_head_12345.mp4`

Videos include:
- Synchronized lip-sync animation
- Original audio track
- H.264 encoding for web compatibility
- 24fps (or custom FPS)

## 🎉 You're Ready!

The South Park animator is now fully functional with both standard sprite-based and Canadian flappy-head animation styles. Enjoy creating your South Park-style talking head animations!