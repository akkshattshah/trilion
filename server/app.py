from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['*'])

@app.route('/')
def home():
    return jsonify({
        "message": "Video Clipper API - Free Tier", 
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat()
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        yt_link = data.get('ytLink')
        num_clips = data.get('numClips', 3)
        clip_duration = data.get('clipDuration', 30)
        
        if not yt_link:
            return jsonify({"error": "No YouTube link provided"}), 400
        
        # Simulate enhanced analysis
        clips = []
        for i in range(num_clips):
            start_time = 30 + (i * 120)
            clips.append({
                "id": i + 1,
                "startTime": start_time,
                "duration": clip_duration,
                "viralScore": 8.5 - (i * 0.2),
                "title": f"Amazing moment #{i+1} from your video!",
                "downloadUrl": f"#clip-{i+1}",
                "analysis_method": "Next-Generation AI Enhanced Intelligence",
                "analysis_success": True
            })
        
        return jsonify({
            "success": True,
            "clips": clips,
            "message": "Enhanced viral analysis completed (Free Tier Demo)"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        yt_link = data.get('ytLink')
        num_clips = data.get('numClips', 3)
        clip_duration = data.get('clipDuration', 30)
        
        if not yt_link:
            return jsonify({"error": "No YouTube link provided"}), 400
        
        clips = []
        for i in range(num_clips):
            start_time = 20 + (i * 90)
            clips.append({
                "id": i + 1,
                "startTime": start_time,
                "duration": clip_duration,
                "title": f"Clip {i+1} from your video",
                "downloadUrl": f"#basic-clip-{i+1}"
            })
        
        return jsonify({
            "success": True,
            "clips": clips,
            "message": "Basic analysis completed (Free Tier)"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
