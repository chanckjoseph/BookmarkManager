from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import json
from datetime import datetime
from parser import parse_netscape_bookmarks
from chrome_parser import parse_chrome_bookmarks
from env_scan_v2 import get_browser_profiles
from database import db, Bookmark, SyncBatch, PendingChange, Tag, BookmarkHistory

# ... (Previous code)


from config import Config

app = Flask(__name__, template_folder='.')
app.config.from_object(Config)

from database import db
db.init_app(app)

with app.app_context():
    if app.config['FLASK_ENV'] != 'testing':
        db.create_all()

CORS(app)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/onboarding')
def onboarding():
    return render_template('index.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/history')
def history():
    return render_template('history.html')

# ... (Previous code)
BOOKMARKS_DB = [
    {"title": "Documentation Hub", "url": "/docs/", "source": "System"}
]

def save_history(bookmark):
    """Saves a snapshot of the current bookmark state to history."""
    history = BookmarkHistory(
        bookmark_id=bookmark.id,
        version=bookmark.version,
        url=bookmark.url,
        title=bookmark.title,
        folder_path=bookmark.folder_path
    )
    db.session.add(history)

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

@app.route('/sync_chrome', methods=['POST'])
def sync_chrome():
    """
    Smart Sync for Chrome: Reads 'Bookmarks' JSON and stages changes.
    Ref: docs/arch/sync_logic.md
    """
    data = request.json
    profile_path = data.get('path')
    if not profile_path:
        return jsonify({"status": "error", "message": "Missing profile path"}), 400
        
    try:
        from chrome_parser import parse_chrome_bookmarks
        bookmarks_file = os.path.join(profile_path, "Bookmarks")
        if not os.path.exists(bookmarks_file):
             return jsonify({"status": "error", "message": "Bookmarks file not found"}), 404

        # 1. Read Incoming Data
        incoming_bookmarks = parse_chrome_bookmarks(bookmarks_file)
        
        # 2. Fetch Existing State for this Source
        # Compare against 'chrome%' source_browser
        existing_query = Bookmark.query.filter(Bookmark.source_browser.ilike('chrome%'))
        existing_map = {b.url: b for b in existing_query.all()}
        
        # 3. Create Batch
        batch = SyncBatch(source="chrome_manual", status="pending_review")
        db.session.add(batch)
        db.session.commit()
        
        changes = []
        incoming_urls = set()
        
        for bm in incoming_bookmarks:
            url = bm['url']
            
            # De-duplication
            if url in incoming_urls:
                continue
            incoming_urls.add(url)
            
            # Case A: NEW
            if url not in existing_map:
                changes.append(PendingChange(
                    batch_id=batch.id,
                    change_type="new",
                    diff_blob=json.dumps(bm)
                ))
            else:
                # Case B: EXISTING (Update)
                existing = existing_map[url]
                if existing.title != bm['title'] or existing.folder_path != bm['folder']:
                     changes.append(PendingChange(
                        batch_id=batch.id,
                        change_type="update",
                        bookmark_id=existing.id,
                        diff_blob=json.dumps({
                            "old": {"title": existing.title, "folder": existing.folder_path},
                            "new": bm
                        })
                    ))
        
        # Case C: MISSING (Soft Delete)
        for url, existing in existing_map.items():
            if url not in incoming_urls:
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
    """Applies selected or all changes in a batch to the main bookmarks table."""
    try:
        batch = SyncBatch.query.get_or_404(batch_id)
        if batch.status != 'pending_review':
            return jsonify({"status": "error", "message": "Batch already processed"}), 400
            
        # Get specific IDs to commit, or commit all if None
        data_json = request.json if request.is_json else {}
        ids_to_commit = data_json.get('change_ids')
        
        count = 0
        changes_to_process = []
        
        for change in batch.changes:
            if ids_to_commit is None or change.id in ids_to_commit:
                changes_to_process.append(change)

        for change in changes_to_process:
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
                    # Save current state to history before updating
                    save_history(bm)
                    
                    new_data = data.get('new', {})
                    bm.title = new_data.get('title')
                    bm.folder_path = new_data.get('folder')
                    bm.version += 1 # Increment version
                    bm.last_synced_at = datetime.utcnow()
                    count += 1
                    
            elif change.change_type == 'mark_deleted':
                bm = Bookmark.query.get(change.bookmark_id)
                if bm:
                    save_history(bm)
                    db.session.delete(bm)
                    count += 1
            
            # Remove the change from the batch after processing
            db.session.delete(change)
        
        # If all changes are gone, mark batch as committed
        db.session.flush() # Ensure deletes are registered
        if len(batch.changes) == 0:
            batch.status = 'committed'
            batch.completed_at = datetime.utcnow()
            
        db.session.commit()
        return jsonify({"status": "success", "count": count, "remaining": len(batch.changes)})
        
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
    """Returns the current state of the database with eager-loaded tags."""
    from sqlalchemy.orm import joinedload
    query_term = request.args.get('q')
    
    base_query = Bookmark.query.options(joinedload(Bookmark.tags)).order_by(Bookmark.id.desc())

    if query_term:
        search_term = f"%{query_term}%"
        bookmarks = base_query.filter(
            (Bookmark.title.ilike(search_term)) | 
            (Bookmark.url.ilike(search_term))
        ).all()
    else:
        bookmarks = base_query.all()
        
    return jsonify({"status": "success", "bookmarks": [b.to_dict() for b in bookmarks]})

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
        new_bm = Bookmark(
            url=bm.get('url'),
            title=bm.get('title'),
            folder_path=bm.get('folder', ''),
            source_browser=f"Upload: {filename}",
            status='synced'
        )
        db.session.add(new_bm)
        
    db.session.commit()
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

@app.route('/tags', methods=['GET', 'POST'])
def manage_tags():
    """List all tags or create a new one."""
    if request.method == 'GET':
        tags = Tag.query.order_by(Tag.name).all()
        return jsonify({"status": "success", "data": [t.to_dict() for t in tags]})
    
    if request.method == 'POST':
        data = request.json
        name = data.get('name', '').strip()
        if not name:
            return jsonify({"status": "error", "message": "Tag name required"}), 400
            
        existing = Tag.query.filter_by(name=name).first()
        if existing:
            return jsonify({"status": "error", "message": "Tag already exists"}), 409
            
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        return jsonify({"status": "success", "data": tag.to_dict()})

@app.route('/bookmarks/<int:bookmark_id>/tags', methods=['POST'])
def add_tag_to_bookmark(bookmark_id):
    """Attach a tag to a bookmark."""
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    data = request.json
    tag_name = data.get('name', '').strip()
    
    if not tag_name:
        return jsonify({"status": "error", "message": "Tag name required"}), 400
        
    # Find or Create Tag
    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        tag = Tag(name=tag_name)
        db.session.add(tag)
    
    if tag not in bookmark.tags:
        bookmark.tags.append(tag)
        db.session.commit()
        
    return jsonify({"status": "success", "data": bookmark.to_dict()})

@app.route('/bookmarks/<int:bookmark_id>/tags/<int:tag_id>', methods=['DELETE'])
def remove_tag_from_bookmark(bookmark_id, tag_id):
    """Remove a tag from a bookmark."""
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    tag = Tag.query.get_or_404(tag_id)
    
    if tag in bookmark.tags:
        bookmark.tags.remove(tag)
        db.session.commit()
        
    return jsonify({"status": "success", "data": bookmark.to_dict()})

@app.route('/history', methods=['GET'])
def get_all_history():
    """Returns a global feed of recent bookmark changes."""
    history = BookmarkHistory.query.order_by(BookmarkHistory.created_at.desc()).limit(100).all()
    return jsonify({
        "status": "success",
        "history": [h.to_dict() for h in history]
    })

@app.route('/bookmarks/<int:bookmark_id>/history', methods=['GET'])
def get_bookmark_history(bookmark_id):
    """Returns the version history of a bookmark."""
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    history = BookmarkHistory.query.filter_by(bookmark_id=bookmark_id).order_by(BookmarkHistory.version.desc()).all()
    
    # Return both current version and history
    return jsonify({
        "status": "success",
        "current": bookmark.to_dict(),
        "history": [h.to_dict() for h in history]
    })

@app.route('/bookmarks/<int:bookmark_id>/revert/<int:history_id>', methods=['POST'])
def revert_bookmark(bookmark_id, history_id):
    """Reverts a bookmark to a previous version."""
    bookmark = Bookmark.query.get_or_404(bookmark_id)
    history = BookmarkHistory.query.get_or_404(history_id)
    
    if history.bookmark_id != bookmark_id:
        return jsonify({"status": "error", "message": "History record mismatch"}), 400
        
    # Save current state before revert
    save_history(bookmark)
    
    # Apply historical state
    bookmark.title = history.title
    bookmark.url = history.url
    bookmark.folder_path = history.folder_path
    bookmark.version += 1
    bookmark.last_synced_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({"status": "success", "message": f"Reverted to version {history.version}"})

@app.context_processor
def inject_config():
    """Injects config values into all templates."""
    return dict(API_BASE_URL=app.config.get('API_BASE_URL', ''))

if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
