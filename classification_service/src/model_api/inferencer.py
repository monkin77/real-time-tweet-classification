from model_api.common.preprocessor import preprocess
from model_api.common.labels import ClassifLabel, ClassificationResult, net_idx_to_label
from model_api.models.base import BaseModel
from model_api.models.distil_bert.model import DistilBert
from httpx import HTTPStatusError
from numpy import argmax

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
        # Feed the cleaned text to the classifier
        softmax_preds = classifier.predict(cleaned)

        # Find the predicted class with the highest probability
        predicted_class_idx = argmax(softmax_preds, axis=-1)

        # Map the index to the corresponding label
        label = net_idx_to_label.get(predicted_class_idx, ClassifLabel.CLASSIFICATION_ERROR)

        # Get the confidence score
        confidence = float(softmax_preds[predicted_class_idx])

        # Create the ClassificationResult object
        classif_result = ClassificationResult(
            label=label,
            confidence=confidence
        )
        print(f"[Inferencer] Prediction result: {classif_result}\n")

        return classif_result
    except Exception as e:
        print(f"[Inferencer] Error during prediction: {e}\n")
        raise HTTPStatusError("Prediction failed", request=None, response=None)