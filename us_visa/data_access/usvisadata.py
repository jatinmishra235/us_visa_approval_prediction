from us_visa.configuration.mongo_db_connection import MongodbClient
from us_visa.exception import VisaException
from us_visa.constant import DATABASE_NAME
import sys
import pandas as pd
import numpy as np



class UsVisaData:
    """
    this class helps to export entire mongo db data into dataframe
    """
    def __init__(self):
        try:
            self.client = MongodbClient(DATABASE_NAME)
        except Exception as e:
            raise VisaException(e,sys)
        
    def export_data_as_dataframe(self,collection_name:str,database_name = None)->pd.DataFrame:
        """
        export entire data as dataframe
        """
        try:
            if database_name is None:
                collection = self.client.database[collection_name]
            else:
                collection = self.client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))

            if '_id' in df.columns.to_list():
                df = df.drop('_id',axis=1)
            df.replace({'na':np.nan},inplace=True)
            return df
        except Exception as e:
            raise VisaException(e,sys)

