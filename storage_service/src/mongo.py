# storage_service/src/mongo.py - MongoDB Connection and Operations
from pymongo import MongoClient
from pymongo.collection import Collection

def create_mongo_client(mongo_uri: str, database_name: str, collection: str):
    """
    Creates a MongoDB client and connects to the specified database.
    
    :param mongo_uri: The MongoDB URI to connect to.
    :param database_name: The name of the database to access.
    :param collection: The name of the collection to access.

    :return: A tuple containing the MongoClient, database object, and collection object.
    """
    # Connect to MongoDB
    db_client = MongoClient(mongo_uri)
    db = db_client[database_name]  # Access the specified database
    collection = db[collection]  # Access the specified collection

    return db_client, db, collection

def close_mongo_client(db_client: MongoClient):
    """
    Closes the MongoDB client connection.
    """
    if db_client:
        db_client.close()
        print("MongoDB connection closed.")
    else:
        print("No MongoDB client to close.")


# Class for Classified Tweet Document
class ClassifiedTweet:
    '''
    Represents a classified tweet document.
    '''
    def __init__(self, tweet_id: str, text: str, label: str, confidence: float):
        self.tweet_id = tweet_id
        self.text = text
        self.label = label
        self.confidence = confidence

    def to_dict(self):
        """
        Converts the ClassifiedTweet instance to a dictionary.
        """
        return {
            "tweet_id": self.tweet_id,
            "text": self.text,
            "label": self.label,
            "confidence": self.confidence
        }

    @staticmethod
    def from_dict(data: dict):
        """
        Creates a ClassifiedTweet instance from a dictionary.
        """
        # Check if required fields are present
        if not all(key in data for key in ("id", "text", "label", "confidence")):
            raise ValueError("Missing required fields in data dictionary.")

        return ClassifiedTweet(
            tweet_id=data.get("id"),
            text=data.get("text"),
            label=data.get("label"),
            confidence=data.get("confidence")
        )
    
def insert_document(collection: Collection, document: ClassifiedTweet):
    """
    Inserts a ClassifiedTweet document into the specified collection.
    
    :param collection: The MongoDB collection to insert the document into.
    :param document: The ClassifiedTweet instance to insert.
    
    :return: The inserted document's ID.
    """
    result = collection.insert_one(document.to_dict())
    return result.inserted_id
