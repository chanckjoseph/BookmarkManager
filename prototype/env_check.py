import os
import platform

def detect_environment():
    """Identifies the OS and searches for common browser profile paths."""
    system = platform.system()
    profile_paths = {
        "Linux": {
            "Chrome": os.path.expanduser("~/.config/google-chrome/Default"),
            "Firefox": os.path.expanduser("~/.mozilla/firefox")
        },
        "Darwin": {  # macOS
            "Chrome": os.path.expanduser("~/Library/Application Support/Google/Chrome/Default"),
            "Firefox": os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
        },
        "Windows": {
            "Chrome": os.path.expandvars("%LOCALAPPDATA%\\Google\\Chrome\\User Data\\Default"),
            "Firefox": os.path.expandvars("%APPDATA%\\Mozilla\\Firefox\\Profiles")
        }
    }
    
    results = {
        "os": system,
        "browsers_detected": []
    }
    
    system_paths = profile_paths.get(system, {})
    for browser, path in system_paths.items():
        if os.path.exists(path):
            results["browsers_detected"].append({
                "name": browser,
                "path": path,
                "status": "Found"
            })
        else:
            results["browsers_detected"].append({
                "name": browser,
                "status": "Not Found"
            })
            
    return results

if __name__ == "__main__":
    env = detect_environment()
    print(f"[EnvCheck] OS: {env['os']}")
    for b in env['browsers_detected']:
        print(f" - {b['name']}: {b['status']}")
