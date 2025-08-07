# labels.py
from enum import Enum
from pydantic import BaseModel, Field

class ClassifLabel(str, Enum):
    """Enum for classification labels."""
    DISASTER = "disaster"
    NON_DISASTER = "non-disaster"
    CLASSIFICATION_ERROR = "classification_error"

class ClassificationResult(BaseModel):
    """Represents the response from the ML model API."""
    label: ClassifLabel = Field(..., description="Classification label", )  
    confidence: float
