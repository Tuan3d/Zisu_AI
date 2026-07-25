import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from core.plan_builder import build_plan
from core.executor import Executor
from core.feedback_logger import log_feedback
from router.train_router import SkillRouter
from eval.run_eval import run_tests

app = Flask(__name__)
CORS(app)

executors = {}

@app.route("/api/plan", methods=["POST"])
def get_plan():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Nội dung yêu cầu trống"}), 400
    plan = build_plan(text)
    return jsonify(plan)

@app.route("/api/execute", methods=["POST"])
def execute_plan():
    data = request.json
    plan = data.get("plan")
    session_id = data.get("session_id", "default")
    
    if not plan:
        return jsonify({"error": "Không có plan để thực thi"}), 400
        
    executor = Executor(plan)
    executors[session_id] = executor
    
    result = executor.run_next()
    return jsonify(result)

@app.route("/api/execute/next", methods=["POST"])
def execute_next():
    data = request.json
    session_id = data.get("session_id", "default")
    
    executor = executors.get(session_id)
    if not executor:
        return jsonify({"error": "Không tìm thấy phiên thực thi"}), 400
        
    result = executor.run_next()
    return jsonify(result)

@app.route("/api/feedback", methods=["POST"])
def post_feedback():
    data = request.json
    skill_id = data.get("skill_id")
    reaction = data.get("reaction")
    reason = data.get("reason")
    details = data.get("details", {})
    
    log_feedback(skill_id, reaction, reason, details)
    return jsonify({"status": "success"})

@app.route("/api/admin/skills", methods=["GET"])
def get_skills():
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    skills = []
    for skill_id in os.listdir(skills_dir):
        schema_path = os.path.join(skills_dir, skill_id, "schema.json")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                
            skills.append({
                "id": skill_id,
                "name": schema.get("name"),
                "description": schema.get("description"),
                "complexity_level": schema.get("complexity_level"),
                "risk_level": schema.get("risk_level"),
                "trained": True,
                "params": schema.get("params", [])
            })
    return jsonify(skills)

@app.route("/api/admin/skills", methods=["POST"])
def create_skill():
    data = request.json
    skill_id = data.get("id")
    if not skill_id:
        return jsonify({"error": "Thiếu Skill ID"}), 400
        
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    skill_path = os.path.join(skills_dir, skill_id)
    os.makedirs(skill_path, exist_ok=True)
    
    schema = {
        "id": skill_id,
        "name": data.get("name"),
        "description": data.get("description"),
        "complexity_level": int(data.get("complexity_level", 1)),
        "risk_level": data.get("risk_level", "LOW"),
        "params": data.get("params", [])
    }
    
    if schema["complexity_level"] == 1:
        schema["fixed_values"] = data.get("fixed_values", {})
        
    with open(os.path.join(skill_path, "schema.json"), "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
        
    extractor_path = os.path.join(skill_path, "extractor.py")
    if not os.path.exists(extractor_path):
        if schema["complexity_level"] == 1:
            code = """import json, os\nfrom rapidfuzz import process, fuzz\ndef extract(text):\n    return {}\n"""
        elif schema["complexity_level"] == 2:
            code = """import re\ndef extract(text):\n    return {}\n"""
        else:
            code = """def extract(text):\n    return {}\n"""
        with open(extractor_path, "w", encoding="utf-8") as f:
            f.write(code)
            
    tc_path = os.path.join(skill_path, "test_cases.jsonl")
    if not os.path.exists(tc_path):
        with open(tc_path, "w", encoding="utf-8") as f:
            f.write("")
            
    return jsonify({"status": "success"})

@app.route("/api/admin/train/router", methods=["POST"])
def train_router_endpoint():
    router = SkillRouter()
    samples = router.train()
    eval_results = run_tests()
    return jsonify({
        "status": "success",
        "samples": samples,
        "eval": eval_results
    })

@app.route("/api/admin/train/extractor", methods=["POST"])
def train_extractor_endpoint():
    data = request.json
    skill_id = data.get("skill_id")
    if not skill_id:
        return jsonify({"error": "Thiếu Skill ID"}), 400
        
    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    test_cases_path = os.path.join(skills_dir, skill_id, "test_cases.jsonl")
    
    if not os.path.exists(test_cases_path):
        return jsonify({"error": f"Không tìm thấy file test cases cho skill {skill_id}"}), 404
        
    from core.ml_extractor import MLExtractor
    extractor = MLExtractor(skill_id)
    samples = extractor.train(test_cases_path)
    
    return jsonify({
        "status": "success",
        "samples": samples
    })

@app.route("/api/admin/feedback", methods=["GET"])
def get_feedback():
    feedback_file = os.path.join(os.path.dirname(__file__), "feedback_log.jsonl")
    logs = []
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    logs.append(json.loads(line))
    return jsonify(logs)

@app.route("/api/admin/eval", methods=["GET"])
def run_eval_endpoint():
    eval_results = run_tests()
    return jsonify(eval_results)

if __name__ == "__main__":
    try:
        SkillRouter().train()
    except Exception as e:
        print("Lỗi train router ban đầu:", e)
    app.run(host="127.0.0.1", port=5000, debug=True)
