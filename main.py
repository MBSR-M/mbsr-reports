#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

from mongo_client import MongoDBConnection
from utils.custom_logger import initialize_logging

load_dotenv()

# Setup logging

logger = initialize_logging(filename='main', console_level='DEBUG')

if __name__ == "__main__":
    db_name = "project_management"

    with MongoDBConnection(os.getenv('MONGO_PROJECT_DB')) as db_connection:
        try:
            doc_id = db_connection.create_document('test', {'name': 'John', 'age': 30})
            logger.info(f"Document created with ID: {doc_id}")

            doc = db_connection.read_document('test', {'name': 'John'})
            logger.info(f"Document found: {doc}")

            modified_count = db_connection.update_document('test', {'name': 'John'}, {'age': 31})
            logger.info(f"Documents updated: {modified_count}")

            deleted_count = db_connection.delete_document('test', {'name': 'John'})
            logger.error(f"Documents deleted: {deleted_count}")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
