#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
from typing import Optional, Dict, Any

from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from utils.custom_logger import initialize_logging

# Setup logging

logger = initialize_logging(filename='mongo_client', console_level='INFO')


class MongoDBConnection:
    def __init__(self, db_name: str, max_retries: int = 3, retry_delay: int = 1):
        self.uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.db_name = db_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Establish a connection to the MongoDB server."""
        try:
            self.client = MongoClient(self.uri, maxPoolSize=10)
            self.db = self.client[self.db_name]
            logger.info("Connected to MongoDB")
        except errors as error:
            logger.error(f"Connection failed: {error}")
            raise

    def retry_wrapper(self, func, *args, **kwargs):
        """Retry a function with exponential backoff."""
        attempt = 0
        while attempt < self.max_retries:
            try:
                return func(*args, **kwargs)
            except (errors.PyMongoError, Exception) as e:
                logger.warning(f"Operation failed: {e}. Retrying in {self.retry_delay ** attempt} seconds...")
                time.sleep(self.retry_delay ** attempt)
                attempt += 1
        raise RuntimeError(f"Operation failed after {self.max_retries} retries.")

    def get_collection(self, collection_name: str) -> Collection:
        """Get a collection from the database."""
        return self.db[collection_name]

    def create_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert a document into a collection."""
        collection = self.get_collection(collection_name)
        result: InsertOneResult = self.retry_wrapper(collection.insert_one, document)
        return str(result.inserted_id)

    def read_document(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a document in a collection."""
        collection = self.get_collection(collection_name)
        return self.retry_wrapper(collection.find_one, query)

    def update_document(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update documents in a collection."""
        collection = self.get_collection(collection_name)
        result: UpdateResult = self.retry_wrapper(collection.update_many, query, {'$set': update})
        return result.modified_count

    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Delete documents from a collection."""
        collection = self.get_collection(collection_name)
        result: DeleteResult = self.retry_wrapper(collection.delete_many, query)
        return result.deleted_count

    def close(self):
        """Close the connection to the MongoDB server."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.close()
