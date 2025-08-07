# labels.py
from enum import Enum

class ClassifLabel(str, Enum):
    """Enum for classification labels."""
    DISASTER = "disaster"
    NON_DISASTER = "non-disaster"
    CLASSIFICATION_ERROR = "classification_error"
