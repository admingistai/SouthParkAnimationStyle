# South Park Talking Head Animator - Simple Setup

Create South Park-style talking animations with flappy heads!

## 🚀 Quick Start (One Command)

```bash
./run_simple.sh
```

Then open your browser to: **http://localhost:5000**

## 📋 Requirements

The script will check and install these automatically:

- Python 3
- Flask packages (flask, flask-cors, opencv-python, numpy, Pillow, pydub)
- ffmpeg (for MP3 support)

## 🎯 How to Use

1. **Start the app**: `./run_simple.sh`
2. **Open browser**: http://localhost:5000
3. **Upload files**:
   - Character image (PNG/JPG)
   - Audio file (MP3/WAV)
4. **Click "Create Animation"**
5. **Download your video!**

## 🔧 Manual Setup (if needed)

### Install Python packages:
```bash
pip install flask flask-cors opencv-python numpy Pillow pydub
```

### Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Run manually:
```bash
cd backend
python3 app_simple.py
```

## 🧪 Testing

If uploads aren't working, test with:
```bash
python3 test_upload.py
```
Then go to http://localhost:5001

## 📁 Test Files

Use the provided test files:
- `test_samples/test_character.png`
- `test_samples/test_audio.wav`

## ❓ Troubleshooting

### "ffmpeg not found"
- Install ffmpeg using the commands above
- MP3 files won't work without ffmpeg

### "Port already in use"
- The script will automatically kill processes on port 5000
- Or manually: `lsof -ti:5000 | xargs kill`

### "CORS error"
- This shouldn't happen with the simple setup
- Everything runs on one server (port 5000)

### "File upload fails"
- Try the test mode: `python3 test_upload.py`
- Check file sizes (max 50MB)
- Make sure files are valid image/audio formats

## 🎬 Features

- **Canadian/Flappy style** - Like Terrance & Phillip
- **Automatic lip sync** - Syncs to audio amplitude
- **Multiple formats** - PNG, JPG, MP3, WAV
- **One-click setup** - No complex configuration

## 📝 How It Works

1. Splits character head horizontally (60/40)
2. Analyzes audio for speech patterns
3. Rotates top half of head based on audio
4. Renders video with synchronized audio

Enjoy creating your South Park animations! 🎭