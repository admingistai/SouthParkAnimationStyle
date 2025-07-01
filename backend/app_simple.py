from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from core.animator import TalkingHeadAnimator

app = Flask(__name__)
CORS(app)  # Simple CORS for all routes

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'temp')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'output')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'mp3', 'mp4', 'm4a', 'ogg', 'aac'}

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

animator = TalkingHeadAnimator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Read the frontend HTML file
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
    with open(frontend_path, 'r') as f:
        html_content = f.read()
    
    # Replace the API_URL in the HTML to use relative paths
    html_content = html_content.replace('const API_URL = \'http://localhost:5000\';', 'const API_URL = \'\';')
    
    return html_content

@app.route('/<path:filename>')
def serve_static(filename):
    # Serve CSS and JS files from frontend directory
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    if os.path.exists(os.path.join(frontend_dir, filename)):
        with open(os.path.join(frontend_dir, filename), 'r') as f:
            content = f.read()
        
        # Modify JS files to use correct API URL
        if filename.endswith('.js'):
            content = content.replace("const API_URL = 'http://localhost:5000';", "const API_URL = '';")
            return content, 200, {'Content-Type': 'application/javascript'}
        elif filename.endswith('.css'):
            return content, 200, {'Content-Type': 'text/css'}
    
    return "Not Found", 404

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'South Park Animator is running!'})

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Simple test endpoint"""
    if request.method == 'POST':
        return jsonify({
            'method': 'POST',
            'files': list(request.files.keys()),
            'form': dict(request.form)
        })
    return jsonify({'message': 'Test endpoint working!'})

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload_files():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("\n=== Processing Upload ===")
        
        # Check for required files
        if 'image' not in request.files or 'audio' not in request.files:
            missing = []
            if 'image' not in request.files:
                missing.append('image')
            if 'audio' not in request.files:
                missing.append('audio')
            return jsonify({
                'error': f'Missing required files: {", ".join(missing)}',
                'received_files': list(request.files.keys())
            }), 400
        
        image = request.files['image']
        audio = request.files['audio']
        
        # Validate files
        if image.filename == '' or audio.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(image.filename):
            return jsonify({'error': f'Invalid image file type: {image.filename}'}), 400
            
        if not allowed_file(audio.filename):
            return jsonify({'error': f'Invalid audio file type: {audio.filename}'}), 400
        
        # Create directories
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Save files
        image_filename = secure_filename(image.filename)
        audio_filename = secure_filename(audio.filename)
        
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        
        image.save(image_path)
        audio.save(audio_path)
        
        print(f"Files saved: {image_filename}, {audio_filename}")
        
        # Process animation
        try:
            style = request.form.get('style', 'canadian')
            output_path = animator.create_animation(image_path, audio_path, style)
            
            return jsonify({
                'success': True,
                'video_url': f'/download/{os.path.basename(output_path)}'
            })
        except Exception as e:
            print(f"Animation processing error: {e}")
            import traceback
            traceback.print_exc()
            
            # Check for common issues
            error_msg = str(e)
            if 'ffmpeg' in error_msg.lower():
                error_msg = "ffmpeg not found. Please install it: brew install ffmpeg"
            
            return jsonify({'error': f'Processing failed: {error_msg}'}), 500
            
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_video(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = 5001  # Changed from 5000 to avoid macOS AirPlay conflict
    
    print("\n" + "="*60)
    print("🎬 South Park Animator Starting...")
    print("="*60)
    print(f"\n✅ Server running at: http://localhost:{port}")
    print(f"✅ Health check: http://localhost:{port}/health")
    print("\n📝 Instructions:")
    print(f"1. Open your browser to http://localhost:{port}")
    print("2. Upload a character image (PNG/JPG)")
    print("3. Upload audio (MP3/WAV)")
    print("4. Click 'Create Animation'")
    print("\n⚠️  Make sure ffmpeg is installed: brew install ffmpeg")
    print("="*60 + "\n")
    
    app.run(debug=True, port=port, host='0.0.0.0')