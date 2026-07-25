import os
import json
from core.plan_builder import build_plan

def run_tests():
    suite_path = os.path.join(os.path.dirname(__file__), "regression_test_suite.jsonl")
    if not os.path.exists(suite_path):
        return {"status": "error", "message": "Test suite file not found."}
        
    results = []
    passed = 0
    total = 0
    
    with open(suite_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            case = json.loads(line)
            total += 1
            text = case["text"]
            expected = case["expected_steps"]
            
            # Predict
            plan = build_plan(text)
            predicted_steps = plan["steps"]
            
            # Compare
            match = True
            if len(predicted_steps) != len(expected):
                match = False
            else:
                for p, e in zip(predicted_steps, expected):
                    if p["skill_id"] != e["skill_id"]:
                        match = False
                        break
                    # So khớp các tham số không null
                    for k, v in e["params"].items():
                        if p["params"].get(k) != v:
                            match = False
                            break
                            
            if match:
                passed += 1
            results.append({
                "text": text,
                "expected": expected,
                "got": [{"skill_id": s["skill_id"], "params": s["params"]} for s in predicted_steps],
                "passed": match
            })
            
    return {
        "total": total,
        "passed": passed,
        "accuracy": passed / total if total > 0 else 0,
        "details": results
    }

if __name__ == "__main__":
    res = run_tests()
    print(f"Regression Test Results: {res['passed']}/{res['total']} passed ({res['accuracy'] * 100:.1f}%)")
