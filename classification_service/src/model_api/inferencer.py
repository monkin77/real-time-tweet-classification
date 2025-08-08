from model_api.common.preprocessor import preprocess
from model_api.common.labels import ClassifLabel, ClassificationResult, net_idx_to_label
from model_api.models.base import BaseModel
from model_api.models.distil_bert.model import DistilBert
from httpx import HTTPStatusError
from numpy import argmax
from logging import Logger

class Inferencer:
    """
    The Inferencer class is responsible for handling the inference process.
    It uses a pre-trained model to classify text inputs and returns the classification results.
    """

    def __init__(self, logger: Logger):
        self.logger = logger
        self.classifier: BaseModel = DistilBert(logger=self.logger)
        self.is_loaded = False

        # Load the model when the Inferencer is initialized
        self.load_model()

    def load_model(self):
        """Load the pre-trained model."""
        if not self.classifier:
            # Define the classifier if it hasn't been defined yet
            self.classifier = DistilBert(logger=self.logger)

        # Load the model
        self.classifier.load()

        # Set the loaded flag to True
        self.is_loaded = True

    def predict(self, text: str) -> ClassificationResult:
        if not self.is_loaded:
            raise ValueError("Model is not loaded. Call load() before predict().")
        
        # Preprocess the input text. Note: Does not include the tokenization step.
        self.logger.debug(f"[Inferencer] Preprocessing text: {text}")
        cleaned = preprocess(text)

        self.logger.debug(f"[Inferencer] Cleaned text: {cleaned}")
        # Make predictions using the classifier
        try:
            # Feed the cleaned text to the classifier
            softmax_preds = self.classifier.predict(cleaned)

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
            self.logger.debug(f"[Inferencer] Prediction result: {classif_result}\n")

            return classif_result
        except Exception as e:
            self.logger.error(f"[Inferencer] Error during prediction: {e}\n")
            raise HTTPStatusError("Prediction failed", request=None, response=None)