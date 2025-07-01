from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS, cross_origin
import os
import tempfile
from werkzeug.utils import secure_filename
from core.animator import TalkingHeadAnimator

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Configure CORS to allow all origins during development
CORS(app, origins="*", allow_headers="*", methods="*")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'temp')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'output')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'mp3', 'mp4', 'm4a', 'ogg', 'aac'}

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

animator = TalkingHeadAnimator()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Don't serve API routes as static files
    if path.startswith(('upload', 'download', 'health', 'test-upload')):
        return "Not Found", 404
    return app.send_static_file(path)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/test-upload', methods=['POST'])
def test_upload():
    """Test endpoint to debug file uploads"""
    print("\n=== TEST UPLOAD DEBUG ===")
    print(f"Content-Type: {request.content_type}")
    print(f"Files in request: {list(request.files.keys())}")
    print(f"Form data: {list(request.form.keys())}")
    
    result = {
        'files_received': {},
        'form_data': dict(request.form)
    }
    
    for file_key in request.files:
        file = request.files[file_key]
        result['files_received'][file_key] = {
            'filename': file.filename,
            'content_type': file.content_type,
            'size': len(file.read())
        }
        file.seek(0)  # Reset file pointer
    
    print(f"Result: {result}")
    return jsonify(result)

@app.route('/upload', methods=['POST', 'OPTIONS'])
@cross_origin()
def upload_files():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        return '', 200
    try:
        print("\n=== UPLOAD REQUEST DEBUG ===")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Files keys: {list(request.files.keys())}")
        print(f"Form keys: {list(request.form.keys())}")
        
        # Check for files
        if 'image' not in request.files:
            print("ERROR: 'image' not in request.files")
            return jsonify({'error': 'Missing image file', 'files_received': list(request.files.keys())}), 400
            
        if 'audio' not in request.files:
            print("ERROR: 'audio' not in request.files")
            return jsonify({'error': 'Missing audio file', 'files_received': list(request.files.keys())}), 400
        
        image = request.files['image']
        audio = request.files['audio']
        
        print(f"Image: {image.filename} ({image.content_type})")
        print(f"Audio: {audio.filename} ({audio.content_type})")
        
        if not allowed_file(image.filename) or not allowed_file(audio.filename):
            return jsonify({'error': f'Invalid file type. Image: {image.filename}, Audio: {audio.filename}'}), 400
        
        # Create upload folder if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save uploaded files
        image_path = os.path.join(UPLOAD_FOLDER, secure_filename(image.filename))
        audio_path = os.path.join(UPLOAD_FOLDER, secure_filename(audio.filename))
        
        image.save(image_path)
        audio.save(audio_path)
        print(f"Files saved: {image_path}, {audio_path}")
        
        # Process animation
        style = request.form.get('style', 'canadian')
        
        # Handle manual mouth positioning for standard style
        mouth_anchor = None
        if style == 'standard':
            mouth_x = request.form.get('mouth_x')
            mouth_y = request.form.get('mouth_y')
            if mouth_x and mouth_y:
                try:
                    mouth_anchor = (int(mouth_x), int(mouth_y))
                    print(f"Using manual mouth anchor: {mouth_anchor}")
                except ValueError:
                    print("Invalid mouth coordinates, using auto-detection")
        
        output_path = animator.create_animation(image_path, audio_path, style, mouth_anchor)
        
        return jsonify({
            'success': True,
            'video_url': f'/download/{os.path.basename(output_path)}'
        })
        
    except Exception as e:
        print(f"Error processing upload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_video(filename):
    try:
        return send_file(
            os.path.join(OUTPUT_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print("\n" + "="*50)
    print("South Park Animator is starting...")
    print("Open your browser to: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host='localhost')