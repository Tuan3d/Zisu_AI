import re

def extract(text):
    """
    Trích xuất target_path và loại đối tượng (file hay thư mục) để thực hiện hành động xóa.
    Ví dụ: "xóa file note.txt" hoặc "xóa thư mục project"
    """
    # Xác định loại cần xóa
    is_dir = "thư mục" in text.lower() or "folder" in text.lower()
    delete_type = "directory" if is_dir else "file"
    
    # Trích xuất target_path
    path_pattern = r"(?:xóa file|xóa thư mục|xóa folder|xóa tập tin|xóa)\s+([a-zA-Z0-9_\-\.\/\\:]+)"
    path_match = re.search(path_pattern, text, re.IGNORECASE)
    target_path = path_match.group(1).strip() if path_match else None
    
    return {
        "target_path": target_path,
        "type": delete_type
    }
