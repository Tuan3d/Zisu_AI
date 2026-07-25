import os
import json
import pickle
import re
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

class MLExtractor:
    def __init__(self, skill_id):
        self.skill_id = skill_id
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills", skill_id, "extractor_model.pkl")
        self.vectorizer = None
        self.model = None

    def _tokenize(self, text):
        # Simple tokenization by splitting spaces but preserving word bounds
        return text.split()

    def _align_labels(self, text, expected_params):
        tokens = self._tokenize(text)
        labels = ["O"] * len(tokens)
        
        for param, val in expected_params.items():
            if not val:
                continue
            val_str = str(val)
            val_tokens = self._tokenize(val_str)
            n_val = len(val_tokens)
            
            # Find subsegment in tokens
            for i in range(len(tokens) - n_val + 1):
                # Clean strings for comparison
                subsegment = [t.lower().strip(",.!?\"'") for t in tokens[i:i+n_val]]
                val_clean = [t.lower().strip(",.!?\"'") for t in val_tokens]
                if subsegment == val_clean:
                    labels[i] = f"B-{param}"
                    for j in range(1, n_val):
                        labels[i+j] = f"I-{param}"
                    break
        return tokens, labels

    def _get_features(self, tokens, idx):
        word = tokens[idx]
        features = {
            "word": word.lower(),
            "is_title": word.istitle(),
            "is_digit": word.isdigit(),
            "suffix2": word[-2:] if len(word) > 2 else word,
            "suffix3": word[-3:] if len(word) > 3 else word,
            "prefix2": word[:2] if len(word) > 2 else word,
            "prefix3": word[:3] if len(word) > 3 else word,
        }
        if idx > 0:
            features["prev_word"] = tokens[idx-1].lower()
        else:
            features["prev_word"] = "<START>"
            
        if idx < len(tokens) - 1:
            features["next_word"] = tokens[idx+1].lower()
        else:
            features["next_word"] = "<END>"
        return features

    def train(self, test_cases_path):
        X = []
        y = []
        
        if not os.path.exists(test_cases_path):
            return 0
            
        with open(test_cases_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                case = json.loads(line)
                text = case.get("text", "")
                expected = case.get("expected", {})
                
                tokens, labels = self._align_labels(text, expected)
                for idx in range(len(tokens)):
                    X.append(self._get_features(tokens, idx))
                    y.append(labels[idx])
                    
        if not X:
            return 0
            
        self.vectorizer = DictVectorizer(sparse=True)
        X_vec = self.vectorizer.fit_transform(X)
        
        self.model = LogisticRegression(C=10.0, max_iter=1000)
        self.model.fit(X_vec, y)
        
        with open(self.model_path, "wb") as f:
            pickle.dump((self.vectorizer, self.model), f)
            
        return len(X)

    def load(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                self.vectorizer, self.model = pickle.load(f)
            return True
        return False

    def extract(self, text):
        if not self.load():
            return {}
            
        tokens = self._tokenize(text)
        if not tokens:
            return {}
            
        features = [self._get_features(tokens, idx) for idx in range(len(tokens))]
        X_vec = self.vectorizer.transform(features)
        predictions = self.model.predict(X_vec)
        
        extracted = {}
        current_param = None
        current_val_tokens = []
        
        for token, pred in zip(tokens, predictions):
            if pred.startswith("B-"):
                if current_param:
                    extracted[current_param] = " ".join(current_val_tokens)
                current_param = pred[2:]
                current_val_tokens = [token]
            elif pred.startswith("I-") and current_param == pred[2:]:
                current_val_tokens.append(token)
            else:
                if current_param:
                    extracted[current_param] = " ".join(current_val_tokens)
                    current_param = None
                    current_val_tokens = []
                    
        if current_param:
            extracted[current_param] = " ".join(current_val_tokens)
            
        return extracted
