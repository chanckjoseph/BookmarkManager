import json
import urllib.request
import urllib.error

import os

API_BASE = os.environ.get('API_BASE_URL', 'http://localhost:5000')
PROFILE_PATH = os.environ.get('FIREFOX_PROFILE_PATH', './empty_chrome_profile') # Fallback for safety

def print_step(title):
    print(f"\n>> {title}")

def post_json(endpoint, data):
    url = f"{API_BASE}{endpoint}"
    req = urllib.request.Request(url, method="POST")
    req.add_header('Content-Type', 'application/json')
    json_data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req, data=json_data) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        return None

def get_json(endpoint):
    url = f"{API_BASE}{endpoint}"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        return None

def check_sync():
    print("Triggering check...")
    data = post_json("/sync_firefox", {"path": PROFILE_PATH})
    if data:
        print(f"Batch #{data['batch_id']}: {data['count']} changes found.")
        return data['batch_id']
    return None

def get_batch(batch_id):
    res = get_json(f"/sync/batch/{batch_id}")
    return res['batch']

def commit(batch_id):
    print(f"Committing Batch #{batch_id}...")
    res = post_json(f"/sync/commit/{batch_id}", {})
    print(res['message'])
    
# 1. First Sync (Should find items, depending on what's in DB)
print_step("Step 1: Baseline Sync")
batch_id = check_sync()

if batch_id:
    details = get_batch(batch_id)
    print(f"Changes: {len(details['changes'])}")
    for c in details['changes'][:3]:
        print(f" - [{c['type']}]")
    
    # Approve it to establish baseline
    commit(batch_id)

# 2. Idempotency Check (Run again immediately)
print_step("Step 2: Idempotency Check (Should be 0 changes)")
batch_id_2 = check_sync()
if batch_id_2:
    details_2 = get_batch(batch_id_2)
    change_count = len(details_2['changes'])
    
    if change_count == 0:
        print("SUCCESS: 0 changes found (Smart Sync works!)")
    else:
        print(f"FAILURE: {change_count} changes found.")
        for c in details_2['changes'][:3]:
            # Print diff snippet
            diff = c['diff']
            if c['type'] == 'update':
                old = diff.get('old', {})
                new = diff.get('new', {})
                print(f" - [update] MISMATCH FOUND:")
                print(f"   OLD: Title='{old.get('title')}', Folder='{old.get('folder')}'")
                print(f"   NEW: Title='{new.get('title')}', Folder='{new.get('folder')}'")
            else:
                url = diff.get('url', diff.get('new', {}).get('url', 'Unknown'))
                print(f" - [{c['type']}] {url}")
