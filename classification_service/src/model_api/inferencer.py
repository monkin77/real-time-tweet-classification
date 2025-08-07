# inferencer.py

from .loader import ModelLoader
from .preprocessor import preprocess
from .labels import ClassifLabel

import os

MODEL_PATH = os.getenv("MODEL_PATH", "model/")

loader = ModelLoader(model_path=MODEL_PATH)  # singleton
classifier_pipeline = loader.get_pipeline()

def predict(text: str):
    cleaned = preprocess(text)
    result = classifier_pipeline(cleaned)
    # result: [{"label": "...", "score": ...}, ...]
    # Or multiple for return_all_scores
    if isinstance(result, list):
        # If return_all_scores, pick the label with max score
        best = max(result[0], key=lambda x: x['score'])
        label = id2label.get(best["label"], best["label"])
        confidence = float(best["score"])
        return {"label": label, "confidence": confidence}
    else:
        # fallback, single result
        return result
