import json
from chrome_parser import parse_chrome_bookmarks
from parser import parse_netscape_bookmarks

def test_chrome():
    print("\n--- Testing Chrome Parser ---")
    # Using a mock structure for testing
    mock_data = {
        "roots": {
            "bookmark_bar": {
                "name": "Bookmarks bar",
                "children": [
                    {
                        "name": "Folder A",
                        "children": [{"type": "url", "name": "Link A", "url": "https://a.com"}]
                    }
                ]
            }
        }
    }
    with open("mock_chrome.json", "w") as f:
        json.dump(mock_data, f)
    
    results = parse_chrome_bookmarks("mock_chrome.json")
    for r in results:
        print(f"[{r['folder']}] {r['title']}")

def test_netscape():
    print("\n--- Testing Netscape Parser ---")
    results = parse_netscape_bookmarks(open("sample_bookmarks.html").read())
    for r in results:
        print(f"[{r['folder']}] {r['title']}")

if __name__ == "__main__":
    test_chrome()
    test_netscape()
