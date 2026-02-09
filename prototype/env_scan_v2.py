import os
import platform
import subprocess
import glob

def get_browser_profiles():
    """
    Advanced scanner to find real browser profile directories.
    """
    system = platform.system()
    profiles = []

    # Linux-specific scan
    if system == "Linux":
        # Chrome/Chromium variants
        chrome_roots = [
            os.path.expanduser("~/.config/google-chrome"),
            os.path.expanduser("~/.config/chromium")
        ]
        for root in chrome_roots:
            if os.path.exists(root):
                # Profiles are either 'Default' or 'Profile X'
                matches = glob.glob(os.path.join(root, "Default")) + glob.glob(os.path.join(root, "Profile *"))
                for p in matches:
                    if os.path.exists(os.path.join(p, "Bookmarks")):
                        profiles.append({
                            "browser": "Chrome/Chromium",
                            "name": os.path.basename(p),
                            "path": p,
                            "file": os.path.join(p, "Bookmarks")
                        })
        
        # Firefox
        ff_root = os.path.expanduser("~/.mozilla/firefox")
        if os.path.exists(ff_root):
            # Firefox profiles are in folders ending with .default or .default-release
            matches = glob.glob(os.path.join(ff_root, "*.default*"))
            for p in matches:
                # FF uses bookmarks.html (exported) or places.sqlite (live)
                # For Sprint 02 feasibility, we look for 'places.sqlite' as a proxy for the live profile
                if os.path.exists(os.path.join(p, "places.sqlite")):
                    profiles.append({
                        "browser": "Firefox",
                        "name": os.path.basename(p),
                        "path": p,
                        "file": "places.sqlite (Live Data)"
                    })

    return {
        "os": system,
        "profiles": profiles
    }

def open_folder(path):
    """PoC: Opens the system file manager at the given path."""
    if not os.path.exists(path):
        return False
    
    try:
        system = platform.system()
        if system == "Linux":
            subprocess.Popen(["xdg-open", path])
        elif system == "Darwin": # macOS
            subprocess.Popen(["open", path])
        elif system == "Windows":
            subprocess.Popen(["explorer", path])
        return True
    except Exception as e:
        print(f"Error opening folder: {e}")
        return False

if __name__ == "__main__":
    print("--- Advanced Environment Scanner v2 ---")
    data = get_browser_profiles()
    print(f"OS Detected: {data['os']}")
    
    if not data['profiles']:
        print("No active browser profiles with bookmarks found.")
    else:
        for p in data['profiles']:
            print(f"\n[{p['browser']}] {p['name']}")
            print(f"  Path: {p['path']}")
            print(f"  Status: Bookmark-ready")
        
        # Test Open Folder on the first one found
        first_path = data['profiles'][0]['path']
        print(f"\n[Test] Attempting to open: {first_path}")
        # open_folder(first_path) # Disabled for CLI run, will be used in API
