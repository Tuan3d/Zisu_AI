import os
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ROUTER_MODEL_PATH = os.path.join(os.path.dirname(__file__), "router_model.pkl")

DEFAULT_TRAINING_DATA = [
    # open_app
    {"text": "mở trình duyệt chrome lên", "skill_id": "open_app"},
    {"text": "chạy ứng dụng notepad giùm tôi", "skill_id": "open_app"},
    {"text": "mở máy tính calculator", "skill_id": "open_app"},
    {"text": "hãy mở cmd lên đi", "skill_id": "open_app"},
    {"text": "bật explorer", "skill_id": "open_app"},
    {"text": "mở word", "skill_id": "open_app"},
    
    # create_file
    {"text": "tạo file note.txt với nội dung đi mua sữa", "skill_id": "create_file"},
    {"text": "tạo tập tin data.csv chứa hello world", "skill_id": "create_file"},
    {"text": "tạo file readme.md ở thư mục Document", "skill_id": "create_file"},
    {"text": "tạo file mới trong thư mục work", "skill_id": "create_file"},
    {"text": "hãy viết vào file test.txt nội dung test", "skill_id": "create_file"},
    
    # create_directory
    {"text": "tạo thư mục project ở D:/work", "skill_id": "create_directory"},
    {"text": "tạo folder source trong thư mục code", "skill_id": "create_directory"},
    {"text": "tạo thư mục mới tại ổ đĩa C", "skill_id": "create_directory"},
    {"text": "tạo folder build", "skill_id": "create_directory"},
    {"text": "hãy tạo thư mục test", "skill_id": "create_directory"},
    
    # delete_file_or_dir
    {"text": "xóa file old_data.csv", "skill_id": "delete_file_or_dir"},
    {"text": "xóa thư mục build", "skill_id": "delete_file_or_dir"},
    {"text": "xóa folder test ở D:/work", "skill_id": "delete_file_or_dir"},
    {"text": "hãy xóa tập tin report.pdf", "skill_id": "delete_file_or_dir"},
    {"text": "xóa file nháp đi", "skill_id": "delete_file_or_dir"}
]

class SkillRouter:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.skills = ["open_app", "create_file", "create_directory", "delete_file_or_dir"]

    def load_training_data(self):
        training_file = os.path.join(os.path.dirname(__file__), "training_data.jsonl")
        data = []
        if os.path.exists(training_file):
            try:
                with open(training_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data.append(json.loads(line))
            except Exception:
                pass
        if not data:
            data = DEFAULT_TRAINING_DATA
        return data

    def save_training_data(self, data):
        training_file = os.path.join(os.path.dirname(__file__), "training_data.jsonl")
        with open(training_file, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    def train(self):
        data = self.load_training_data()
        texts = [d["text"] for d in data]
        labels = [d["skill_id"] for d in data]
        
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(texts)
        
        self.model = LogisticRegression(C=1.0, max_iter=1000)
        self.model.fit(X, labels)
        
        with open(ROUTER_MODEL_PATH, "wb") as f:
            pickle.dump((self.vectorizer, self.model), f)
            
        return len(data)

    def load(self):
        if os.path.exists(ROUTER_MODEL_PATH):
            with open(ROUTER_MODEL_PATH, "rb") as f:
                self.vectorizer, self.model = pickle.load(f)

    def route(self, text):
        self.load()
        if not self.vectorizer or not self.model:
            t = text.lower()
            if "xóa" in t:
                return "delete_file_or_dir", 0.6
            elif "thư mục" in t or "folder" in t:
                return "create_directory", 0.6
            elif "tạo file" in t or "tập tin" in t:
                return "create_file", 0.6
            else:
                return "open_app", 0.5
                
        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]
        max_idx = probs.argmax()
        skill_id = self.model.classes_[max_idx]
        confidence = float(probs[max_idx])
        return str(skill_id), confidence

def route_sentence(text):
    router = SkillRouter()
    return router.route(text)
