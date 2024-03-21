import sys
from us_visa.exception import VisaException
from us_visa.logger import logging
from dotenv import load_dotenv
load_dotenv()

import os
from us_visa.constant import DATABASE_NAME, MONGODB_URL_KEY
import pymongo

class MongodbClient:
    client = None

    def __init__(self,database_name= DATABASE_NAME):
        try:
            if MongodbClient.client is None:
                mongo_db_url = os.getenv(MONGODB_URL_KEY)
                if mongo_db_url is None:
                    raise Exception(f"environment key {MONGODB_URL_KEY} is not set")
                MongodbClient.client = pymongo.MongoClient(mongo_db_url)
                self.client = MongodbClient.client
                self.database = self.client[database_name]
                self.database_name = database_name
                logging.info("mongodb connection succesfull")
        except Exception as e:
            raise VisaException(e,sys)