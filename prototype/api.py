from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from parser import parse_netscape_bookmarks
from chrome_parser import parse_chrome_bookmarks
from env_scan_v2 import get_browser_profiles, open_folder

app = Flask(__name__)
CORS(app)

# In-memory "Database" for the prototype verification
# This ensures Stage 4 "Main App Page" can actually show combined data.
BOOKMARKS_DB = [
    {"title": "Documentation Hub", "url": "http://localhost:8080/docs/", "source": "System"}
]

@app.route('/add', methods=['POST'])
def add_bookmark():
    data = request.json
    url = data.get('url')
    title = data.get('title')
    if not url or not title:
        return jsonify({"status": "error", "message": "Missing URL or Title"}), 400
    
    new_bookmark = {"title": title, "url": url, "source": "Bookmarklet"}
    BOOKMARKS_DB.insert(0, new_bookmark)
    print(f"[API] Received Bookmark: {title} ({url})")
    return jsonify({"status": "success", "received": new_bookmark})

@app.route('/bookmarks', methods=['GET'])
def get_bookmarks():
    """Returns the current state of the database."""
    return jsonify({"status": "success", "data": BOOKMARKS_DB})

@app.route('/upload_bulk', methods=['POST'])
def upload_bulk():
    """Parses an uploaded file (HTML or JSON)."""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    
    file = request.files['file']
    filename = file.filename
    content = file.read().decode('utf-8', errors='ignore')
    
    new_data = []
    if filename.endswith('.html'):
        new_data = parse_netscape_bookmarks(content)
    elif filename.endswith('.json') or filename == 'Bookmarks':
        # Temporary save to pass to chrome_parser (logic improvement)
        temp_path = "/tmp/temp_bookmarks"
        with open(temp_path, 'w') as f:
            f.write(content)
        new_data = parse_chrome_bookmarks(temp_path)
    
    for bm in new_data:
        bm['source'] = f"Upload: {filename}"
        BOOKMARKS_DB.append(bm)
        
    return jsonify({"status": "success", "count": len(new_data)})

@app.route('/env', methods=['GET'])
def get_env():
    """Advanced endpoint for environment fingerprinting (Sprint 02)."""
    return jsonify({"status": "success", "env": get_browser_profiles()})

@app.route('/open_folder', methods=['POST'])
def trigger_open_folder():
    """PoC: Triggers local file manager via backend (Sprint 02)."""
    data = request.json
    path = data.get('path')
    if not path:
        return jsonify({"status": "error", "message": "Missing path"}), 400
    
    # Security: Only allow opening detected profile paths
    profiles = get_browser_profiles()['profiles']
    allowed_paths = [p['path'] for p in profiles]
    
    if path in allowed_paths:
        success = open_folder(path)
        return jsonify({"status": "success" if success else "error"})
    return jsonify({"status": "error", "message": "Unauthorized path"}), 403

if __name__ == '__main__':
    app.run(port=5000)
