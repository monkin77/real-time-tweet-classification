from pydantic import BaseModel, Field
from model_api.common.labels import ClassifLabel


# --- Pydantic Models for Data Validation ---
class RawTweetData(BaseModel):
    """Represents the 'data' field of an incoming raw tweet message."""
    id: str = Field(..., alias="id", description="Unique identifier for the tweet")
    text: str = Field(..., alias="text", description="Text content of the tweet")
    created_at: str = Field(..., alias="created_at", description="Timestamp when the tweet was created")
    author_id: str = Field(..., alias="author_id", description="ID of the user who authored the tweet")
    username: str = Field(..., alias="username", description="Username of the author")


class RawTweet(BaseModel):
    """Represents the full structure of an incoming raw tweet message."""
    data: RawTweetData


class ClassificationResult(BaseModel):
    """Represents the response from the ML model API."""
    label: ClassifLabel = Field(..., description="Classification label", )  
    confidence: float


class ClassifiedTweet(BaseModel):
    """Represents the final, enriched data to be published."""
    id: str
    text: str
    label: str
    confidence: float

class PredictTweet(BaseModel):
    """Represents the input for the tweet prediction endpoint."""
    text: str
    id: str = Field(..., description="Unique identifier for the tweet")
