import os
import json
from datetime import datetime

FEEDBACK_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "feedback_log.jsonl")

def log_feedback(skill_id, reaction, reason=None, details=None):
    """
    reaction: 'like' hoặc 'dislike'
    reason: lý do nếu dislike (sai skill, sai tham số, thiếu bước, thừa bước)
    details: chi tiết phản hồi (câu nhập của user, tham số AI trích xuất...)
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "skill_id": skill_id,
        "reaction": reaction,
        "reason": reason,
        "details": details
    }
    
    with open(FEEDBACK_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
    # Nếu dislike và có câu mẫu mới kèm label đúng, tự động chuẩn bị để đưa vào training_data của skill hoặc router
    if reaction == "dislike" and details and "user_text" in details:
        text = details["user_text"]
        if reason == "sai skill" and "correct_skill_id" in details:
            # Lưu ý: Thêm vào training_data của Router
            router_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "router")
            training_file = os.path.join(router_dir, "training_data.jsonl")
            with open(training_file, "a", encoding="utf-8") as f_route:
                new_item = {"text": text, "skill_id": details["correct_skill_id"]}
                f_route.write(json.dumps(new_item, ensure_ascii=False) + "\n")
                
        elif reason == "sai tham số" and "correct_params" in details:
            # Lưu ý: Thêm vào training_data của Skill tương ứng (nếu skill đó là cấp độ 3 như search_file)
            skill_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", skill_id)
            training_file = os.path.join(skill_dir, "training_data.jsonl")
            if os.path.exists(training_file):
                with open(training_file, "a", encoding="utf-8") as f_skill:
                    new_item = {
                        "text": text,
                        "label": "câu sửa lỗi",
                        "expected": details["correct_params"]
                    }
                    f_skill.write(json.dumps(new_item, ensure_ascii=False) + "\n")
                    
    return True
