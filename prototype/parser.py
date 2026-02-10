import re
import json

def parse_netscape_bookmarks(html_content):
    """
    Parses Netscape-format HTML bookmarks with folder hierarchy support.
    Uses a stack-based approach to track parent folders.
    """
    bookmarks = []
    folder_stack = []
    
    # Simple line-by-line parsing as Netscape HTML is often malformed
    # We look for <DL>, </DL>, <H3> (folder name), and <A> (bookmark)
    lines = html_content.splitlines()
    
    # Regex patterns
    folder_pattern = re.compile(r'<H3[^>]*>([^<]+)</H3>', re.IGNORECASE)
    link_pattern = re.compile(r'<A\s+HREF="([^"]+)"[^>]*>([^<]+)</A>', re.IGNORECASE)
    dl_pattern = re.compile(r'<DL>', re.IGNORECASE)
    dl_end_pattern = re.compile(r'</DL>', re.IGNORECASE)

    for line in lines:
        line = line.strip()
        
        # Folder Start/Label
        folder_match = folder_pattern.search(line)
        if folder_match:
            # Note: We find H3 before entering the next DL
            # The next <DL> will belong to this H3
            label = folder_match.group(1).strip()
            # If we see an H3, we assume we're about to enter its DL
            # But the stack management happens in DL patterns
            pending_folder = label
        
        if dl_pattern.search(line):
            # If we have a pending folder name, push it to stack
            if 'pending_folder' in locals():
                folder_stack.append(pending_folder)
                del pending_folder
            else:
                # Top level or unlabelled DL
                # Check for specific source roots if applicable
                pass
        
        if dl_end_pattern.search(line):
            if folder_stack:
                folder_stack.pop()

        # Bookmark Link
        link_match = link_pattern.search(line)
        if link_match:
            url = link_match.group(1).strip()
            title = link_match.group(2).strip()
            current_folder = " > ".join(folder_stack)
            
            bookmarks.append({
                "title": title,
                "url": url,
                "folder": current_folder or "Root"
            })
    
    return bookmarks

if __name__ == "__main__":
    # Test execution
    test_file = "prototype/sample_bookmarks.html"
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        results = parse_netscape_bookmarks(content)
        print(f"[Parser] Successfully extracted {len(results)} bookmarks.")
        print(json.dumps(results[:2], indent=2))
    else:
        print(f"[Parser] Error: {test_file} not found.")
