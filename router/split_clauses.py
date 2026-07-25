import os
import json
import re

def split_to_clauses(text):
    """
    Tách các câu phức ghép thành các mệnh đề đơn dựa trên các từ nối tiếng Việt.
    Ví dụ: "Mở chrome rồi sau đó tạo file note.txt" 
    -> ["Mở chrome", "tạo file note.txt"]
    """
    # Các từ khóa liên kết hoặc chỉ thị thứ tự hành động
    delimiters = [
        r"\sau đó và\b",
        r"\brồi sau đó\b",
        r"\bsau đó\b",
        r"\brồi\b",
        r"\bvà\b",
        r"\bthì\b",
        r"\bkế tiếp\b",
        r"\ttiếp theo\b",
        r",\s*"
    ]
    
    # Kết hợp các delimiter thành một pattern duy nhất
    pattern = "|".join(delimiters)
    
    # Thay thế các từ nối bằng một dấu phân cách đặc biệt
    temp_text = re.sub(pattern, "|||", text, flags=re.IGNORECASE)
    
    # Chia nhỏ câu và lọc bỏ các khoảng trắng thừa hoặc mệnh đề rỗng
    clauses = [c.strip() for c in temp_text.split("|||") if c.strip()]
    
    # Loại bỏ các từ đệm ở đầu mệnh đề như "sau đó", "tiếp theo", "hãy"
    cleaned_clauses = []
    for clause in clauses:
        c = re.sub(r"^(sau đó|tiếp theo|hãy|rồi|và|thì)\s+", "", clause, flags=re.IGNORECASE).strip()
        if c:
            cleaned_clauses.append(c)
            
    return cleaned_clauses
