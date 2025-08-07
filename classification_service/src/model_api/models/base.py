from abc import ABC, abstractmethod
import keras
import keras_nlp

class BaseModel(ABC):
    def __init__(self):
        """Initialize the base model."""
        self.preprocessor: keras_nlp.models.Preprocessor = None  # Will be initialized in load method
        self.classifier: keras.Model = None  # Will be initialized in load method
        self.is_loaded = False

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def predict(self, text: str):
        '''
        Preprocess the input text and make predictions using the classifier.
        :param text: The text to classify.

        :return: The prediction results. Shape: (batch_size, num_classes=2)
        Returns a list of probabilities of belonging to each class.
        '''
        pass
