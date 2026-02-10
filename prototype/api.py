from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import json
from datetime import datetime
from parser import parse_netscape_bookmarks
from chrome_parser import parse_chrome_bookmarks
from env_scan_v2 import get_browser_profiles
from database import db, Bookmark, SyncBatch, PendingChange

app = Flask(__name__, template_folder='.')
# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'timeout': 30}}

from database import db
db.init_app(app)

with app.app_context():
    db.create_all()

CORS(app)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/onboarding')
def onboarding():
    return render_template('index.html')

# In-memory "Database" for the prototype verification
# This ensures Stage 4 "Main App Page" can actually show combined data.
BOOKMARKS_DB = [
    {"title": "Documentation Hub", "url": "http://localhost:8080/docs/", "source": "System"}
]

@app.route('/sync_firefox', methods=['POST'])
def sync_firefox():
    """
    Smart Sync: Reads Firefox SQLite and stages changes based on Diff Logic.
    Ref: docs/arch/sync_logic.md
    """
    data = request.json
    profile_path = data.get('path')
    if not profile_path:
        return jsonify({"status": "error", "message": "Missing profile path"}), 400
        
    try:
        from firefox_reader import get_firefox_bookmarks
        # 1. Read Incoming Data (The Feed)
        incoming_bookmarks = get_firefox_bookmarks(os.path.join(profile_path, "places.sqlite"))
        
        # 2. Fetch Existing State for this Source
        # We only compare against bookmarks from 'firefox' to ensure safety
        existing_query = Bookmark.query.filter(Bookmark.source_browser.ilike('firefox%'))
        existing_map = {b.url: b for b in existing_query.all()}
        
        # 3. Create Batch
        batch = SyncBatch(source="firefox_manual", status="pending_review")
        db.session.add(batch)
        db.session.commit()
        
        changes = []
        incoming_urls = set()
        
        for bm in incoming_bookmarks:
            url = bm['url']
            
            # De-duplication: Only process the first occurrence of a URL from the source
            if url in incoming_urls:
                continue
            incoming_urls.add(url)
            
            # Case A: NEW (URL not found)
            if url not in existing_map:
                changes.append(PendingChange(
                    batch_id=batch.id,
                    change_type="new",
                    diff_blob=json.dumps(bm)
                ))
            else:
                # Case B: EXISTING (Check for Updates)
                existing = existing_map[url]
                # Check for metadata drift (Title or Folder)
                if existing.title != bm['title'] or existing.folder_path != bm['folder']:
                    print(f"DEBUG MISMATCH: ID={existing.id} | Title: '{existing.title}' vs '{bm['title']}' | Folder: '{existing.folder_path}' vs '{bm['folder']}'")
                    changes.append(PendingChange(
                        batch_id=batch.id,
                        change_type="update",
                        bookmark_id=existing.id,
                        diff_blob=json.dumps({
                            "old": {"title": existing.title, "folder": existing.folder_path},
                            "new": bm
                        })
                    ))
                # Else: Match -> Ignore
                
        # Case C: MISSING (Soft Delete)
        # Verify source matches to avoid deleting Chrome items
        for url, existing in existing_map.items():
            if url not in incoming_urls:
                # Only flag if it's currently marked as 'synced'
                if existing.status != 'absent_on_source':
                    changes.append(PendingChange(
                        batch_id=batch.id,
                        change_type="mark_deleted",
                        bookmark_id=existing.id,
                        diff_blob=json.dumps({"title": existing.title, "url": existing.url})
                    ))

        if changes:
            db.session.bulk_save_objects(changes)
            db.session.commit()
        else:
            # If no changes, maybe auto-approve empty batch or just leave empty?
            # Let's leave it empty to show "Sync Checked - No Changes"
            pass
        
        return jsonify({"status": "success", "batch_id": batch.id, "count": len(changes)})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sync/batches', methods=['GET'])
def get_pending_batches():
    """Returns any batches waiting for review."""
    batches = SyncBatch.query.filter_by(status='pending_review').all()
    return jsonify({
        "status": "success",
        "batches": [{
            "id": b.id,
            "source": b.source,
            "created_at": b.created_at,
            "count": len(b.changes)
        } for b in batches]
    })

@app.route('/sync/batch/<int:batch_id>', methods=['GET'])
def get_batch_details(batch_id):
    """Returns full details and changes for a specific batch."""
    batch = SyncBatch.query.get_or_404(batch_id)
    return jsonify({
        "status": "success",
        "batch": {
            "id": batch.id,
            "source": batch.source,
            "created_at": batch.created_at,
            "changes": [{
                "id": c.id,
                "type": c.change_type,
                "diff": c.get_diff()
            } for c in batch.changes]
        }
    })

@app.route('/sync/commit/<int:batch_id>', methods=['POST'])
def commit_batch(batch_id):
    """Applies all changes in a batch to the main bookmarks table."""
    try:
        batch = SyncBatch.query.get_or_404(batch_id)
        if batch.status != 'pending_review':
            return jsonify({"status": "error", "message": "Batch already processed"}), 400
            
        count = 0
        for change in batch.changes:
            data = change.get_diff()
            
            if change.change_type == 'new':
                bm = Bookmark(
                    url=data.get('url'),
                    title=data.get('title'),
                    folder_path=data.get('folder'),
                    source_browser=data.get('source'),
                    status='synced'
                )
                db.session.add(bm)
                count += 1
                
            elif change.change_type == 'update':
                bm = Bookmark.query.get(change.bookmark_id)
                if bm:
                    new_data = data.get('new', {})
                    bm.title = new_data.get('title')
                    bm.folder_path = new_data.get('folder')
                    bm.last_synced_at = datetime.utcnow()
                    count += 1
                    
            elif change.change_type == 'mark_deleted':
                bm = Bookmark.query.get(change.bookmark_id)
                if bm:
                    bm.status = 'absent_on_source'
                    count += 1
            
        batch.status = 'approved'
        db.session.commit()
        return jsonify({"status": "success", "message": f"Committed {count} bookmarks."})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sync/reject/<int:batch_id>', methods=['POST'])
def reject_batch(batch_id):
    """Discards a batch."""
    try:
        batch = SyncBatch.query.get_or_404(batch_id)
        batch.status = 'rejected'
        db.session.commit()
        return jsonify({"status": "success", "message": "Batch rejected."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/bookmarks', methods=['GET'])
def get_bookmarks():
    """Returns the current state of the database."""
    bookmarks = Bookmark.query.order_by(Bookmark.id.desc()).all()
    return jsonify({"status": "success", "data": [b.to_dict() for b in bookmarks]})

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
