from common.preprocessor import preprocess
from common.labels import ClassifLabel, ClassificationResult
from models.base import BaseModel
from models.distil_bert.model import DistilBert
from httpx import HTTPStatusError

# Define the Used Classifier -- inside the models/ folder
classifier: BaseModel = DistilBert()
# Load the model
classifier.load()

def predict(text: str) -> ClassificationResult:
    if not classifier.is_loaded:
        raise ValueError("Model is not loaded. Call load() before predict().")
     
    # Preprocess the input text. Note: Does not include the tokenization step.
    print(f"[Inferencer] Preprocessing text: {text}")
    cleaned = preprocess(text)
    
    print(f"[Inferencer] Cleaned text: {cleaned}")
    # Make predictions using the classifier
    try:
        result = classifier.predict(cleaned)
    except Exception as e:
        print(f"[Inferencer] Error during prediction: {e}")
        raise HTTPStatusError("Prediction failed", request=None, response=None)


    print(f"[Inferencer] Prediction result: {result}")

    if isinstance(result, list):
        best = max(result[0], key=lambda x: x['score'])
        label = best["label"]
        confidence = float(best["score"])
        return {"label": label, "confidence": confidence}
    else:
        print(f"[Inferencer] Unexpected result type: {type(result)} |  Result: {result}")
        return result