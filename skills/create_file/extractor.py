import re

def extract(text):
    """
    Trích xuất file_name, target_dir, và content từ câu yêu cầu.
    Ví dụ: "tạo file abc.txt ở thư mục Document với nội dung xin chào"
    """
    # Trích xuất file_name
    file_pattern = r"(?:tạo file|tạo tập tin)\s+([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+|[a-zA-Z0-9_\-]+)"
    file_match = re.search(file_pattern, text, re.IGNORECASE)
    file_name = file_match.group(1).strip() if file_match else None
    
    # Trích xuất target_dir
    dir_pattern = r"(?:ở thư mục|trong thư mục|tại thư mục|ở|trong)\s+([a-zA-Z0-9_\-\/\\:]+)"
    dir_match = re.search(dir_pattern, text, re.IGNORECASE)
    target_dir = dir_match.group(1).strip() if dir_match else None
    
    # Loại trừ trường hợp target_dir nhận nhầm tên file hoặc từ khóa nội dung
    if target_dir and (target_dir.endswith(".") or target_dir.lower() in ["nội", "nội dung", "với"]):
        target_dir = None
        
    # Trích xuất content
    content_pattern = r"(?:nội dung là|với nội dung|chứa|ghi)\s+(.*?)$"
    content_match = re.search(content_pattern, text, re.IGNORECASE)
    content = content_match.group(1).strip() if content_match else None
    
    # Loại bỏ tiền tố "nội dung" nếu bị trùng trong bóc tách
    if content and content.lower().startswith("nội dung "):
        content = content[9:].strip()
        
    return {
        "file_name": file_name,
        "target_dir": target_dir,
        "content": content
    }
