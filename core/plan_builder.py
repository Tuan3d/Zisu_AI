import os
import json
import importlib.util
from router.split_clauses import split_to_clauses
from router.train_router import route_sentence

# Hàm load extractor động của skill
def load_skill_extractor(skill_id):
    skill_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", skill_id)
    extractor_path = os.path.join(skill_dir, "extractor.py")
    schema_path = os.path.join(skill_dir, "schema.json")
    
    if not os.path.exists(extractor_path) or not os.path.exists(schema_path):
        return None, None
        
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
        
    spec = importlib.util.spec_from_file_location(f"{skill_id}.extractor", extractor_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    default_extract = module.extract
    
    # Check if a trained ML model exists for this skill
    model_path = os.path.join(skill_dir, "extractor_model.pkl")
    if os.path.exists(model_path):
        try:
            from core.ml_extractor import MLExtractor
            ml_extractor = MLExtractor(skill_id)
            if ml_extractor.load():
                def hybrid_extract(text):
                    default_res = default_extract(text)
                    ml_res = ml_extractor.extract(text)
                    res = default_res.copy()
                    for k, v in ml_res.items():
                        if v:
                            res[k] = v
                    return res
                return hybrid_extract, schema
        except Exception as e:
            print(f"Lỗi khi load MLExtractor cho {skill_id}, chuyển sang fallback: {e}")
            
    return default_extract, schema

def build_plan(user_instruction):
    """
    Phân tích yêu cầu -> tách mệnh đề -> định tuyến skill -> trích tham số -> trả về Plan tổng.
    """
    clauses = split_to_clauses(user_instruction)
    steps = []
    
    for i, clause in enumerate(clauses):
        skill_id, confidence = route_sentence(clause)
        extract_fn, schema = load_skill_extractor(skill_id)
        
        params = {}
        if extract_fn:
            try:
                params = extract_fn(clause)
            except Exception as e:
                print(f"Lỗi khi trích xuất tham số cho {skill_id}: {e}")
                
        # Schema info
        risk_level = "LOW"
        expected_result = ""
        if schema:
            risk_level = schema.get("risk_level", "LOW")
            expected_result = f"Thực hiện thành công skill {schema.get('name')}"
            
        steps.append({
            "step_id": i + 1,
            "skill_id": skill_id,
            "skill_name": schema.get("name", skill_id) if schema else skill_id,
            "params": params,
            "expected_result": expected_result,
            "risk_level": risk_level,
            "clause": clause
        })
        
    return {
        "user_instruction": user_instruction,
        "steps": steps
    }
