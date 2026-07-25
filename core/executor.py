import time
import os

def execute_step(step):
    """
    Giả lập thực thi kỹ năng thực tế trên máy tính dựa trên Skill ID và Params.
    """
    skill_id = step["skill_id"]
    params = step["params"]
    
    print(f"Bắt đầu thực thi: {skill_id} với tham số {params}")
    time.sleep(1) # Giả lập độ trễ
    
    if skill_id == "open_app":
        app_name = params.get("app_name")
        if not app_name:
            return False, "Thiếu tham số 'app_name' để mở ứng dụng."
        
        from core.app_helper import match_app
        matched_name, app_path = match_app(app_name)
        if not app_path:
            try:
                os.startfile(app_name)
                return True, f"Đã mở ứng dụng {app_name} thành công."
            except Exception as e:
                return False, f"Không tìm thấy ứng dụng '{app_name}' trên hệ thống và không thể khởi chạy: {e}"
        
        try:
            os.startfile(app_path)
            return True, f"Đã mở ứng dụng {matched_name or app_name} thành công."
        except Exception as e:
            return False, f"Lỗi khi mở ứng dụng {matched_name or app_name}: {e}"
        
    elif skill_id == "create_file":
        file_name = params.get("file_name")
        target_dir = params.get("target_dir") or "Workspace"
        content = params.get("content") or ""
        if not file_name:
            return False, "Thiếu tham số 'file_name' để tạo file."
        try:
            if not os.path.isabs(target_dir):
                target_dir = os.path.abspath(target_dir)
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, f"Đã tạo file {file_name} ở thư mục {target_dir} với nội dung '{content}' thành công."
        except Exception as e:
            return False, f"Lỗi khi tạo file thực tế: {e}"
        
    elif skill_id == "create_directory":
        dir_name = params.get("dir_name")
        target_dir = params.get("target_dir") or "Workspace"
        if not dir_name:
            return False, "Thiếu tham số 'dir_name' để tạo thư mục."
        try:
            if not os.path.isabs(target_dir):
                target_dir = os.path.abspath(target_dir)
            full_path = os.path.join(target_dir, dir_name)
            os.makedirs(full_path, exist_ok=True)
            return True, f"Đã tạo thư mục {dir_name} ở thư mục {target_dir} thành công."
        except Exception as e:
            return False, f"Lỗi khi tạo thư mục thực tế: {e}"
        
    elif skill_id == "delete_file_or_dir":
        target_path = params.get("target_path")
        delete_type = params.get("type") or "file"
        if not target_path:
            return False, "Thiếu tham số 'target_path' để xóa."
        try:
            if not os.path.isabs(target_path):
                target_path = os.path.abspath(target_path)
            if not os.path.exists(target_path):
                return False, f"Không tồn tại đường dẫn '{target_path}' để xóa."
            if os.path.isdir(target_path):
                import shutil
                shutil.rmtree(target_path)
            else:
                os.remove(target_path)
            return True, f"Đã xóa {delete_type} {target_path} thành công."
        except Exception as e:
            return False, f"Lỗi khi thực hiện xóa thực tế: {e}"
        
    return False, f"Không nhận diện được kỹ năng {skill_id}."

class Executor:
    def __init__(self, plan):
        self.plan = plan
        self.current_step_idx = 0
        self.history = []

    def run_next(self):
        """
        Chạy bước tiếp theo. Gặp lỗi thì dừng và trả về thông tin lỗi để hỏi người dùng.
        """
        if self.current_step_idx >= len(self.plan["steps"]):
            return {"status": "FINISHED", "message": "Hoàn thành toàn bộ Plan."}
            
        step = self.plan["steps"][self.current_step_idx]
        success, message = execute_step(step)
        
        result = {
            "step_id": step["step_id"],
            "skill_id": step["skill_id"],
            "success": success,
            "message": message
        }
        self.history.append(result)
        
        if success:
            self.current_step_idx += 1
            return {
                "status": "STEP_SUCCESS",
                "result": result,
                "message": message,
                "next_step": self.current_step_idx < len(self.plan["steps"])
            }
        else:
            return {
                "status": "STEP_FAILED",
                "result": result,
                "message": f"Lỗi ở bước {step['step_id']} ({step['skill_name']}): {message}. Bạn có muốn thử lại từ bước này không?"
            }

    def resume_from_error(self):
        """
        Thực hiện chạy lại từ bước bị lỗi hiện tại.
        """
        return self.run_next()
