import re

def extract(text):
    """
    Trích xuất dir_name và target_dir cho kỹ năng tạo thư mục.
    Ví dụ: "tạo thư mục photos ở C:/Users" hoặc "tạo folder project"
    """
    # Trích xuất dir_name
    dir_name_pattern = r"(?:tạo thư mục|tạo folder)\s+([a-zA-Z0-9_\-\.]+)"
    dir_name_match = re.search(dir_name_pattern, text, re.IGNORECASE)
    dir_name = dir_name_match.group(1).strip() if dir_name_match else None
    
    # Trích xuất target_dir
    target_dir_pattern = r"(?:ở thư mục|trong thư mục|tại thư mục|ở|trong|tại)\s+([a-zA-Z0-9_\-\/\\:]+)"
    target_dir_match = re.search(target_dir_pattern, text, re.IGNORECASE)
    target_dir = target_dir_match.group(1).strip() if target_dir_match else None
    
    # Tránh trùng lặp nếu target_dir bắt được chính tên folder
    if target_dir == dir_name:
        target_dir = None
        
    return {
        "dir_name": dir_name,
        "target_dir": target_dir
    }
