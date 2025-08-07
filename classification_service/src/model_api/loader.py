# loader.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Optional
import threading

class ModelLoader:
    '''
    Singleton class to load and cache the model and tokenizer.
    This ensures that the model is loaded only once and reused across requests.
    '''
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_path: str, tokenizer_path: Optional[str] = None):
        '''
        Create a new instance of ModelLoader.
        '''
        if not cls._instance:
            # Use a lock to ensure thread safety during singleton instantiation
            # This prevents multiple threads from creating multiple instances
            # of the ModelLoader at the same time.
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._init(model_path, tokenizer_path)
        return cls._instance

    def _init(self, model_path, tokenizer_path=None):
        '''
        Initialize the model and tokenizer.
        :param model_path: Path to the model directory.
        :param tokenizer_path: Optional path to the tokenizer directory.
        If not provided, defaults to model_path.
        '''
        from transformers import pipeline
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path or model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.pipeline = pipeline(
            "text-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            return_all_scores=True # Ensures softmax scores are returned
        )
    
    def get_pipeline(self):
        '''
        Return the classification pipeline.
        '''
        return self.pipeline
