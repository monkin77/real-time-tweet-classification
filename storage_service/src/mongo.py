# storage_service/src/mongo.py - MongoDB Connection and Operations
from pymongo import MongoClient
from pymongo.collection import Collection
from pydantic import BaseModel, Field
from logging import Logger

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
class ClassifiedTweet(BaseModel):
    tweet_id: str = Field(..., alias="id", description="Unique identifier for the tweet")
    text: str = Field(..., alias="text", description="Text content of the tweet")
    label: str = Field(..., alias="label", description="Classification label for the tweet")
    confidence: float = Field(..., alias="confidence", description="Confidence score for the classification")
    created_at: str = Field(..., alias="created_at", description="Timestamp when the tweet was created")    

    
def insert_document(collection: Collection, document: ClassifiedTweet, logger: Logger) -> str:
    """
    Inserts a ClassifiedTweet document into the specified collection.
    
    :param collection: The MongoDB collection to insert the document into.
    :param document: The ClassifiedTweet instance to insert.
    
    :return: The inserted document's ID.
    """
    # Check if the tweet was already stored before
    existing_tweet = collection.find_one({"tweet_id": document.tweet_id})
    if existing_tweet:
        logger.info(f"Tweet with ID {document.tweet_id} already exists in the collection. Skipping insertion.")
        return existing_tweet["_id"]


    result = collection.insert_one(document.model_dump())
    logger.info(f"Inserted document with ID {result.inserted_id}.")
    return result.inserted_id
