import json
import os

def parse_chrome_bookmarks(file_path):
    """
    Parses a native Chrome JSON Bookmarks file.
    """
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        bookmarks = []
        
        def walk_tree(node):
            if isinstance(node, dict):
                if node.get('type') == 'url':
                    bookmarks.append({
                        "title": node.get('name'),
                        "url": node.get('url'),
                        "source": "Chrome JSON"
                    })
                
                # Check children (folders or other sections)
                for key, value in node.items():
                    if key == 'children':
                        for child in value:
                            walk_tree(child)
                    elif isinstance(value, dict):
                        walk_tree(value)

        # Chrome roots: bookmark_bar, other, synced
        roots = data.get('roots', {})
        for root_node in roots.values():
            walk_tree(root_node)
            
        return bookmarks
    except Exception as e:
        print(f"Error parsing Chrome JSON: {e}")
        return []

if __name__ == "__main__":
    # Test path for Linux
    test_path = os.path.expanduser("~/.config/google-chrome/Default/Bookmarks")
    if os.path.exists(test_path):
        results = parse_chrome_bookmarks(test_path)
        print(f"Parsed {len(results)} bookmarks from Chrome.")
        if results:
            print(f"First 2: {results[:2]}")
