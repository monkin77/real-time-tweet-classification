import keras
import keras_nlp
from ..base import BaseModel

class DistilBert(BaseModel):
    def __init__(self):
        super().__init__()

    def load(self):
        preset = "distil_bert_base_en_uncased"
        self.preprocessor = keras_nlp.models.DistilBertPreprocessor.from_preset(
            preset,
            sequence_length=160,
            name="preprocessor_4_tweets"
        )

        trained_model_file = "./models/distil_bert/trained_model.keras"# "./model_api/models/distil_bert/trained_model.keras"    # TODO: Check if this is the correct path
        self.classifier: keras.Model = keras.models.load_model(trained_model_file)

        # Print summary of the loaded mode
        print("Classifier summary:")
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
        if not self.preprocessor or not self.classifier:
            raise ValueError("Model is not loaded. Call load() before predict().")
        
        # Tokenization and other Preprocessing are handled by the classifier class.
        # inputs = self.preprocessor(text)
        # inputs = {key: inputs[key][None, :] for key in inputs}  #

        # Add batch dimension for the input text
        net_input = [text]  # Wrap the text in a list to create a batch of size 1
        print("Inputs for prediction:", net_input)

        # Get the logits from the classifier
        predictions = self.classifier.predict(net_input)
        # This method only classifies a single text at a time, so we can assume batch_size=1.
        predictions = predictions[0]
        print("Raw predictions (logits):", predictions)

        # Compute the Softmax probabilities
        softmax_pred = keras.activations.softmax(predictions, axis=-1)
        print("Softmax predictions:", softmax_pred)

        return softmax_pred