from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from parser import parse_netscape_bookmarks
from env_check import detect_environment

app = Flask(__name__)
CORS(app)

@app.route('/add', methods=['POST'])
def add_bookmark():
    data = request.json
    url = data.get('url')
    title = data.get('title')
    if not url or not title:
        return jsonify({"status": "error", "message": "Missing URL or Title"}), 400
    print(f"[API] Received Bookmark: {title} ({url})")
    return jsonify({"status": "success", "received": {"title": title, "url": url}})

@app.route('/import', methods=['POST'])
def import_bookmarks():
    """Bulk import feasibility test using sample_bookmarks.html."""
    sample_path = "prototype/sample_bookmarks.html"
    if os.path.exists(sample_path):
        with open(sample_path, 'r') as f:
            content = f.read()
        bookmarks = parse_netscape_bookmarks(content)
        return jsonify({"status": "success", "count": len(bookmarks), "data": bookmarks})
    return jsonify({"status": "error", "message": "Sample file not found"}), 404

@app.route('/env', methods=['GET'])
def get_env():
    """Endpoint for environment fingerprinting."""
    return jsonify({"status": "success", "env": detect_environment()})

if __name__ == '__main__':
    app.run(port=5000)
