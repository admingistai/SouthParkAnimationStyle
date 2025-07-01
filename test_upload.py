#!/usr/bin/env python3
"""
Simple test script to debug file uploads
"""
import os
import sys

# Add the backend directory to the path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload Test</title>
    </head>
    <body>
        <h1>South Park Animator - Upload Test</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <p>
                <label>Image: </label>
                <input type="file" name="image" accept="image/*" required>
            </p>
            <p>
                <label>Audio: </label>
                <input type="file" name="audio" accept="audio/*" required>
            </p>
            <p>
                <button type="submit">Test Upload</button>
            </p>
        </form>
        
        <div id="result"></div>
        
        <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('/test-upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = '<pre>Error: ' + error.message + '</pre>';
            }
        });
        </script>
    </body>
    </html>
    '''

@app.route('/test-upload', methods=['POST'])
def test_upload():
    """Test upload endpoint that doesn't process, just reports what it received"""
    
    result = {
        'success': True,
        'files_received': {},
        'form_data': dict(request.form),
        'total_files': len(request.files)
    }
    
    for file_key, file in request.files.items():
        if file.filename:
            result['files_received'][file_key] = {
                'filename': file.filename,
                'content_type': file.content_type,
                'size': len(file.read()) if hasattr(file, 'read') else 'unknown'
            }
            file.seek(0)  # Reset file pointer
    
    return jsonify(result)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Test server running'})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🧪 Upload Test Server")
    print("="*50)
    print("\nOpen: http://localhost:5001")
    print("\nThis tests file uploads without processing")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')