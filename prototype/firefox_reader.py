import sqlite3
import os

def get_firefox_bookmarks(sqlite_path):
    """
    Reads bookmarks from a Firefox places.sqlite database.
    Returns a list of dicts: {'title': str, 'url': str, 'folder': str, 'source': 'Firefox'}
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
        def get_full_path(item_id):
            path = []
            curr_id = item_map[item_id]["parent"]
            
            # Traverse up to root (parent=0 or missing)
            while curr_id in item_map:
                # 0 is the root, 1 is 'Menu', 2 is 'Toolbar', 3 is 'Tags', 5 is 'Unsorted'
                # We can skip the root(0)
                if curr_id == 0:
                    break
                    
                parent_data = item_map[curr_id]
                title = parent_data["title"]
                
                # Normalize root folder names for better UX
                if curr_id == 1: title = "Menu"
                elif curr_id == 2: title = "Toolbar"
                elif curr_id == 3: title = "Tags"
                elif curr_id == 5: title = "Other"
                
                if title:
                    path.insert(0, title)
                
                curr_id = parent_data["parent"]
            
            return " > ".join(path)

        bookmarks = []
        for item_id, data in item_map.items():
            if data["type"] == 1: # Bookmark
                url = url_map.get(data["fk"])
                if url:
                    full_path = get_full_path(item_id)
                    bookmarks.append({
                        "title": data["title"] or "No Title",
                        "url": url,
                        "folder": full_path,
                        "source": "Firefox"
                    })
                    
        return bookmarks

    finally:
        conn.close()
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
