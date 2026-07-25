import os
from rapidfuzz import process, fuzz

def get_installed_apps():
    apps = {}
    
    # Standard paths on Windows
    paths = []
    program_data = os.environ.get("ProgramData", "C:\\ProgramData")
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    
    paths.append(os.path.join(program_data, "Microsoft", "Windows", "Start Menu", "Programs"))
    paths.append(os.path.join(user_profile, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"))
    
    for path in paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith(".lnk"):
                        app_name = file[:-4]  # Remove .lnk
                        lnk_path = os.path.join(root, file)
                        apps[app_name.lower()] = {
                            "name": app_name,
                            "path": lnk_path
                        }
                        
    # Add standard Windows executables
    standard_apps = {
        "notepad": "notepad.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "paint": "mspaint.exe",
        "mspaint": "mspaint.exe",
        "control panel": "control.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "chrome": "chrome.exe",
        "msedge": "msedge.exe",
        "edge": "msedge.exe"
    }
    
    for key, path in standard_apps.items():
        if key not in apps:
            apps[key] = {
                "name": key,
                "path": path
            }
            
    return apps

def match_app(query_text):
    apps = get_installed_apps()
    if not apps:
        return None, None
        
    # Clean the query text by removing common action verbs
    clean_text = query_text.lower()
    for verb in ["mở", "bật", "chạy", "khởi động", "open", "run", "launch", "start", "ứng dụng", "app"]:
        clean_text = clean_text.replace(verb, " ")
    
    # Clean multiple spaces
    clean_text = " ".join(clean_text.split()).strip()
    
    if not clean_text:
        clean_text = query_text.lower().strip()
        
    candidates = list(apps.keys())
    
    # We can perform fuzzy matching
    match = process.extractOne(clean_text, candidates, scorer=fuzz.WRatio)
    if match:
        matched_key, score, _ = match
        if score >= 50:
            return apps[matched_key]["name"], apps[matched_key]["path"]
            
    return None, None
