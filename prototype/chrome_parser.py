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
        
        def walk_tree(node, current_path="", is_root=False):
            if isinstance(node, dict):
                node_name = node.get('name')
                
                if node.get('type') == 'url':
                    bookmarks.append({
                        "title": node_name,
                        "url": node.get('url'),
                        "folder": current_path,
                        "source": "Chrome JSON"
                    })
                
                # Check children (folders)
                if 'children' in node:
                    # If this is root, we don't append node_name (it's already the current_path label)
                    if is_root:
                        new_path = current_path
                    else:
                        new_path = f"{current_path} > {node_name}" if current_path else node_name
                        
                    for child in node['children']:
                        walk_tree(child, new_path)

        # Chrome roots: bookmark_bar, other, synced
        roots = data.get('roots', {})
        
        # Mapping technical keys to human labels used in source screenshot
        root_mapping = {
            "bookmark_bar": "Bookmarks Toolbar",
            "other": "Other Bookmarks",
            "synced": "Mobile Bookmarks"
        }

        for root_key, root_node in roots.items():
            label = root_mapping.get(root_key, root_node.get('name', root_key))
            walk_tree(root_node, label, is_root=True)
            
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
