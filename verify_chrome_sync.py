import requests
import json
import os
import shutil

API_BASE = "http://localhost:5000"
TEST_CHROME_DIR = "test_chrome_profile"
TEST_BOOKMARKS_FILE = os.path.join(TEST_CHROME_DIR, "Bookmarks")

def setup_test_data():
    if os.path.exists(TEST_CHROME_DIR):
        shutil.rmtree(TEST_CHROME_DIR)
    os.makedirs(TEST_CHROME_DIR)
    
    # Create minimal Chrome Bookmarks JSON
    bookmarks_data = {
        "roots": {
            "bookmark_bar": {
                "children": [
                    {
                        "date_added": "13256000000000000",
                        "id": "1",
                        "name": "Google",
                        "type": "url",
                        "url": "https://www.google.com/"
                    },
                    {
                        "children": [
                            {
                                "date_added": "13256000000000000",
                                "id": "3",
                                "name": "Python Docs",
                                "type": "url",
                                "url": "https://docs.python.org/3/"
                            }
                        ],
                        "date_added": "13256000000000000",
                        "id": "2",
                        "name": "Dev",
                        "type": "folder"
                    }
                ],
                "date_added": "13256000000000000",
                "id": "0",
                "name": "Bookmarks Bar",
                "type": "folder"
            }
        },
        "version": 1
    }
    
    with open(TEST_BOOKMARKS_FILE, 'w') as f:
        json.dump(bookmarks_data, f)
    
    print(f"Created test profile at: {os.path.abspath(TEST_CHROME_DIR)}")
    return os.path.abspath(TEST_CHROME_DIR)

def verify_sync():
    print("--- Verifying Chrome Sync ---")
    path = setup_test_data()
    
    try:
        # 1. Trigger Sync
        print("Triggering /sync_chrome...")
        res = requests.post(f"{API_BASE}/sync_chrome", json={"path": path})
        if res.status_code != 200:
            print(f"Error: {res.text}")
            res.raise_for_status()
            
        data = res.json()
        print(f"Sync response: {data}")
        batch_id = data['batch_id']
        assert data['status'] == 'success'
        assert data['count'] > 0
        
        # 2. Verify Batch Details
        print(f"Verifying Batch #{batch_id}...")
        res = requests.get(f"{API_BASE}/sync/batch/{batch_id}")
        res.raise_for_status()
        batch_data = res.json()['batch']
        
        changes = batch_data['changes']
        print(f"Found {len(changes)} changes.")
        
        # Expecting at least "Google" and "Python Docs"
        urls = [c['diff'].get('url') for c in changes if c['type'] == 'new']
        print(f"New URLs: {urls}")
        
        assert "https://www.google.com/" in urls
        assert "https://docs.python.org/3/" in urls
        
        print("✅ Chrome Sync logic verified.")
        
        # Cleanup
        # requests.post(f"{API_BASE}/sync/reject/{batch_id}") # Optional: keep for manual review
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
    finally:
        # Cleanup file
        if os.path.exists(TEST_CHROME_DIR):
            shutil.rmtree(TEST_CHROME_DIR)

if __name__ == "__main__":
    verify_sync()
