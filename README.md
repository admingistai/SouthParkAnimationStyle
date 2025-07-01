# South Park Talking Head Animator

Create South Park-style talking animations with flappy heads like Terrance & Phillip!

## Quick Start

1. **Setup**
   ```bash
   ./setup.sh
   ```

2. **Install ffmpeg** (if not already installed)
   ```bash
   brew install ffmpeg  # macOS
   # or
   sudo apt-get install ffmpeg  # Ubuntu
   ```

3. **Run the app**
   ```bash
   # Terminal 1: Start backend
   cd backend
   python app.py
   
   # Terminal 2: Open frontend
   open frontend/index.html  # macOS
   # or just open frontend/index.html in your browser
   ```

## Usage

1. Upload a character image (PNG/JPG)
2. Upload audio file (WAV/MP3)
3. Select animation style (Canadian/Standard)
4. Click "Create Animation"
5. Download your video!

## Features

- Automatic head splitting
- Phoneme-based lip sync
- Canadian-style flappy head animation
- Simple web interface

## Tips

- Use images with clear head/body separation
- Front-facing characters work best
- Keep audio under 30 seconds for best results

## Optional: Better Lip Sync

Download Rhubarb Lip Sync from [here](https://github.com/DanielSWolf/rhubarb-lip-sync/releases) and place the `rhubarb` executable in the `models` directory for improved phoneme detection.