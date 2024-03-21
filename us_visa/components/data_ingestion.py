from us_visa.exception import VisaException
from us_visa.logger import logging
import os,sys
from sklearn.model_selection import train_test_split

from us_visa.entity.config_entity import DataIngestionConfig
from us_visa.entity.artifact_entity import DataIngestionArtifact

from pandas import DataFrame

from us_visa.data_access.usvisadata import UsVisaData

class DataIngestion:
    def __init__(self,data_ingestion_config:DataIngestionConfig=DataIngestionConfig()):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise VisaException(e,sys)
        
    def export_data_into_feature_store(self):
        """
        Method Name : export_data_into_feature_store
        Description : this method export data from mongodb to csv file
        """
        logging.info('exporting data from mongodb')

        us_visa_data = UsVisaData()
        dataframe = us_visa_data.export_data_as_dataframe(collection_name=self.data_ingestion_config.collection_name)
        logging.info(f"shape of data {dataframe.shape}")

        feature_store_filepath = self.data_ingestion_config.feature_store_file_path

        dir_name = os.path.dirname(feature_store_filepath)

        os.makedirs(dir_name,exist_ok=True)

        logging.info(f"saving exported data into feature store filepath {feature_store_filepath}")
        dataframe.to_csv(feature_store_filepath,index=False,header=True)
        return dataframe
    
    def split_data_as_train_test(self,dataframe:DataFrame)->None:
        """
        Method Name : split_data_as_train_test
        Description : this method splits data into train and test based in split ratio
        """
        logging.info('entered into split_data_as_train_test method of data ingestion class')
        try:
            train_set, test_set = train_test_split(dataframe,test_size=self.data_ingestion_config.train_test_split_ratio)
            logging.info("performed train test split on dataset")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)

            logging.info("exporting train and test files")

            train_set.to_csv(self.data_ingestion_config.training_file_path,index=False,header=True)
            test_set.to_csv(self.data_ingestion_config.test_file_path,index=False,header=True)

            logging.info("exported training and test file path")
        except Exception as e:
             raise VisaException(e,sys)
        
    def initiate_data_ingestion(self):
        """
        Method Name : initiate_data_ingestion
        Description : this method intiates data ingestion component of training pipeline
        Output : training set and test set are returned as artifacts of data ingestion component
        On failure : write a exception log and raises exception
        """
        try:
            dataframe = self.export_data_into_feature_store()

            logging.info("got data from mongodb")

            self.split_data_as_train_test(dataframe=dataframe)

            logging.info("performed train test split")

            logging.info("exited initiate_data_ingestion method of data ingestion class")

            data_ingestion_artifact = DataIngestionArtifact(train_file_path = self.data_ingestion_config.training_file_path,
                                                            test_file_path = self.data_ingestion_config.test_file_path)
            
            logging.info(f"data ingestion config : {data_ingestion_artifact}")

            return data_ingestion_artifact
        except Exception as e:
            raise VisaException(e,sys)
        





