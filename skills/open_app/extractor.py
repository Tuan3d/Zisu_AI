import sys
import os

# Add root folder to sys.path if not present
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from core.app_helper import match_app

def extract(text):
    """
    Trích xuất tham số app_name bằng Fuzzy Matching từ danh sách ứng dụng đã cài đặt.
    """
    app_name, _ = match_app(text)
    if not app_name:
        # Clean verbs from the fallback text
        clean_text = text.lower()
        for verb in ["mở", "bật", "chạy", "khởi động", "open", "run", "launch", "start", "ứng dụng", "app"]:
            clean_text = clean_text.replace(verb, " ")
        app_name = " ".join(clean_text.split()).strip()
        
    return {
        "app_name": app_name or text
    }

