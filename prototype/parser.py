import re
import json

def parse_netscape_bookmarks(html_content):
    """
    Parses Netscape-format HTML bookmarks.
    Specifically looks for <DT><A HREF="...">Title</A> pattern.
    Handles unclosed <DT> tags common in browser exports.
    """
    bookmarks = []
    # Regex to find links: <A HREF="url"...>Title</A>
    # Note: Using regex for feasibility as Netscape format is often too malformed for standard XML parsers.
    pattern = re.compile(r'<A\s+HREF="([^"]+)"[^>]*>([^<]+)</A>', re.IGNORECASE)
    
    matches = pattern.findall(html_content)
    for url, title in matches:
        bookmarks.append({
            "title": title.strip(),
            "url": url.strip()
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
