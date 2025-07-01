from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return 'Server is running!'

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/test', methods=['GET', 'POST', 'OPTIONS'])
def test():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({'message': 'CORS is working!', 'method': request.method})

@app.route('/upload', methods=['POST', 'OPTIONS'])
def upload():
    if request.method == 'OPTIONS':
        return '', 200
    
    print("Upload endpoint hit!")
    print(f"Files: {list(request.files.keys())}")
    print(f"Form: {dict(request.form)}")
    
    return jsonify({
        'success': True,
        'files_received': list(request.files.keys()),
        'form_data': dict(request.form)
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Test server starting...")
    print("Open: http://localhost:5000")
    print("Test CORS in browser console with:")
    print("fetch('http://localhost:5000/test').then(r => r.json()).then(console.log)")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')