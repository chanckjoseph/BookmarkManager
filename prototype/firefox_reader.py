import sqlite3
import os

def get_firefox_bookmarks(sqlite_path):
    """
    Reads bookmarks from a Firefox places.sqlite database.
    Returns a dict with bookmarks and count metadata for verification.
    """
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"Database not found: {sqlite_path}")

    # Copy to /tmp to avoid "database is locked" errors if Firefox is running
    import shutil
    import tempfile
    
    # Create temp file that auto-deletes? No, sqlite needs path.
    # Manual temp path
    tmp_path = f"/tmp/places_copy_{os.getpid()}.sqlite"
    shutil.copy2(sqlite_path, tmp_path)

    # Connect to the COPY
    conn = sqlite3.connect(f"file:{tmp_path}?mode=ro", uri=True)
    cursor = conn.cursor()
    
    try:
        # Count total bookmarks in source DB for verification
        cursor.execute("SELECT COUNT(*) FROM moz_bookmarks WHERE type=1")
        source_total = cursor.fetchone()[0]
        
        # 1. Fetch all bookmark items (folders and bookmarks)
        # type: 1=bookmark, 2=folder
        query = """
        SELECT id, type, parent, title, fk
        FROM moz_bookmarks
        WHERE type IN (1, 2)
        """
        cursor.execute(query)
        all_items = cursor.fetchall()
        
        # 2. Build a map for O(1) parent lookup
        # item_map = {id: {parent, title, type}}
        item_map = {
            row[0]: {
                "type": row[1],
                "parent": row[2],
                "title": row[3],
                "fk": row[4]
            } for row in all_items
        }
        
        # 3. Fetch URLs
        cursor.execute("SELECT id, url FROM moz_places")
        url_map = dict(cursor.fetchall())
        
        # 4. Helper to build folder path
        def get_full_path(item_id, parent_id):
            path = []
            curr_id = parent_id
            
            # Traverse up to root (parent=0 or missing)
            while curr_id in item_map:
                if curr_id <= 1: # ID 1 is 'Places Root' (virtual), skip it and stop
                    break
                    
                parent_data = item_map[curr_id]
                title = parent_data["title"]
                
                # Normalize root pillar names
                # ID 2 = Menu, ID 3 = Toolbar, ID 5 = Other
                if curr_id == 2: title = "Bookmarks Menu"
                elif curr_id == 3: title = "Bookmarks Toolbar"
                elif curr_id == 5: title = "Other Bookmarks"
                
                if title:
                    path.insert(0, title)
                
                curr_id = parent_data["parent"]
            
            return " > ".join(path)

        bookmarks = []
        tags_filtered = 0
        invalid_urls = 0
        
        for item_id, data in item_map.items():
            if data["type"] == 1: # Bookmark
                # NOTE: Removed Tags folder (ID 3) filtering per user feedback
                # Firefox may not always have a Tags folder, and filtering by ID 3
                # was incorrectly excluding legitimate bookmarks
                
                url = url_map.get(data["fk"])
                if url:
                    full_path = get_full_path(item_id, data["parent"])
                    bookmarks.append({
                        "title": data["title"] or "No Title",
                        "url": url,
                        "folder": full_path,
                        "source": "Firefox"
                    })
                else:
                    invalid_urls += 1
        
        # Return both bookmarks and metadata for count verification
        return {
            "bookmarks": bookmarks,
            "metadata": {
                "source_total": source_total,
                "tags_filtered": tags_filtered,
                "invalid_urls": invalid_urls,
                "processed": len(bookmarks)
            }
        }

    finally:
        conn.close()
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
