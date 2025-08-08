import keras
from ..base import BaseModel
from logging import Logger

class DistilBert(BaseModel):
    def __init__(self, logger: Logger):
        super().__init__(logger=logger)

    def load(self):
        trained_model_file = "./model_api/models/distil_bert/trained_model.keras"  # "./models/distil_bert/trained_model.keras"    # TODO: Add this to .env file
        
        # Print the WD First
        # import os
        # self.logger.debug(f"[DistilBert] Current working directory: {os.getcwd()}\n\n\n")

        self.classifier: keras.Model = keras.models.load_model(trained_model_file)

        # Print summary of the loaded mode
        self.logger.debug("[DistilBert] Classifier summary:")
        self.classifier.summary()

        # Set the loaded flag to True
        self.is_loaded = True

    def predict(self, text: str) -> list[float]:
        ''''
        Preprocess the input text and make predictions using the classifier.

        :param text: The text to classify.

        :return: The prediction results after applying softmax.
        Returns a list of probabilities of belonging to each class.
        Shape: (num_classes=2)
        '''
        if not self.classifier:
            raise ValueError("Model is not loaded. Call load() before predict().")
        
        # Tokenization and other Preprocessing are handled by the classifier class.

        # Add batch dimension for the input text
        net_input = [text]  # Wrap the text in a list to create a batch of size 1
        self.logger.debug(f"[DistilBert] Inputs for prediction: {net_input}", exc_info=False)

        # Get the logits from the classifier
        predictions = self.classifier.predict(net_input)
        # This method only classifies a single text at a time, so we can assume batch_size=1.
        predictions = predictions[0]
        self.logger.debug("[DistilBert] Raw predictions (logits):", str(predictions.tolist()))

        # Compute the Softmax probabilities
        softmax_pred = keras.activations.softmax(predictions, axis=-1)
        # self.logger.debug("[DistilBert] Softmax predictions:", str(softmax_pred.numpy().tolist()))

        return softmax_pred