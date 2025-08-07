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

        trained_model_file = "./model_api/models/distil_bert/trained_model.keras"    # TODO: Check if this is the correct path
        self.classifier = keras.models.load_model(trained_model_file)

        # Set the loaded flag to True
        self.is_loaded = True

    def predict(self, text: str):
        ''''
        Preprocess the input text and make predictions using the classifier.
        '''
        if not self.preprocessor or not self.classifier:
            raise ValueError("Model is not loaded. Call load() before predict().")
        
        inputs = self.preprocessor(text)
        # inputs = {key: inputs[key][None, :] for key in inputs}  #
        print("Inputs for prediction:", inputs)

        predictions = self.classifier(inputs)
        print("Raw predictions:", predictions)

        return predictions