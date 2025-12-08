"""
Sisi Lola Voice API - Production endpoint for voice generation
"""

from flask import Flask, request, jsonify, send_file
from sisi_lola_voice_lock import SisiLolaVoiceLock
from pathlib import Path
import tempfile
import os

app = Flask(__name__)
voice_lock = SisiLolaVoiceLock()

@app.route('/generate', methods=['POST'])
def generate_voice():
    """Generate Sisi Lola voice from text"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        output_path = voice_lock.generate_speech(text, tmp.name)
        return send_file(output_path, mimetype='audio/wav')

@app.route('/batch', methods=['POST'])
def batch_generate():
    """Generate multiple voice samples"""
    data = request.json
    texts = data.get('texts', [])
    
    if not texts:
        return jsonify({'error': 'No texts provided'}), 400
    
    output_dir = Path(tempfile.mkdtemp())
    results = voice_lock.batch_generate(texts, output_dir)
    
    return jsonify({
        'count': len(results),
        'files': [str(f) for f in results]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'model': voice_lock.model_id,
        'voice_seed': voice_lock.voice_seed,
        'device': voice_lock.device
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
