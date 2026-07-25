# CONTRIBUTING.md - Hướng dẫn đóng góp Skill mới cho zisu AI

Chào mừng bạn đóng góp kỹ năng (Skill) mới cho cộng đồng! Quy trình đóng góp và tích hợp một Skill mới gồm 7 bước bắt buộc sau:

## Quy trình 7 bước phát triển và đóng góp Skill mới

1. **Bước 1: Tạo cấu trúc thư mục Skill**
   Tạo thư mục mới trong `/skills/<tên_skill_của_bạn>`.

2. **Bước 2: Định nghĩa Schema (`schema.json`)**
   Khai báo ID, mô tả, các tham số, độ phức tạp (cấp độ 1, 2, hoặc 3), và độ nguy hại `risk_level` (LOW, MEDIUM, HIGH).

3. **Bước 3: Viết Extractor trích xuất tham số (`extractor.py`)**
   * **Cấp độ 1 (Rule thuần):** Dùng `rapidfuzz` để khớp với danh sách tham số cố định.
   * **Cấp độ 2 (Rule + Regex):** Dùng regex để bóc tách thông tin có định dạng.
   * **Cấp độ 3 (Model nhẹ):** Xây dựng bộ training và model trích xuất cụm từ tự do.

4. **Bước 4: Tạo dữ liệu huấn luyện / Test cases**
   * Viết tệp dữ liệu test mẫu `test_cases.jsonl`.
   * Đối với Skill cấp độ 3, chuẩn bị tập tin `training_data.jsonl` phong phú chứa ít nhất 10 ví dụ với các nhóm nhãn rõ ràng.

5. **Bước 5: Huấn luyện & Chạy thử nghiệm**
   * Huấn luyện riêng model extractor cho skill (nếu cấp 3).
   * Huấn luyện lại Router tổng hợp từ giao diện Admin.

6. **Bước 6: Chạy kiểm thử hồi quy (Regression Test)**
   * Chạy kiểm thử hồi quy thông qua script `python -m eval.run_eval` hoặc nhấn nút Train Router trên Admin Dashboard để đảm bảo Router không nhầm lẫn giữa skill mới và các skill cũ.

7. **Bước 7: Gửi Pull Request**
   * Kiểm tra mã nguồn sạch sẽ, không có placeholder hoặc emoji trong giao diện. Gửi Pull Request của bạn lên nhánh chính.
