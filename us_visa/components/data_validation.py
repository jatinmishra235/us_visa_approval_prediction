import os,sys,json
from pandas import DataFrame
import pandas as pd

from us_visa.exception import VisaException
from us_visa.logger import logging

from us_visa.utils.main_utils import write_yaml_file,read_yaml_file

from us_visa.entity.config_entity import DataValidationConfig
from us_visa.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact

from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection

from us_visa.constant import SCHEMA_FILE_PATH

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_validation_config:DataValidationConfig):
        """
        :param data_ingestion_artifact output reference of data ingestion stage
        :param data_validation_config configuration for data validation
        """

        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_file = read_yaml_file(filepath=SCHEMA_FILE_PATH)
        except Exception as e:
            raise VisaException(e,sys)
        
    def validate_number_of_columns(self,dataframe : DataFrame)->bool:
        """
        Method Name : validate_number_of_columns
        Description : this methoda validates number of columns of input dataframe
        Output      : returns bool value based on validation result
        On failure  : log the error and raises exception
        """
        try:
            status = len(dataframe.columns)==len(self._schema_file['columns'])
            logging.info(f"is required columns present {status}")
            return status
        except Exception as e:
            raise VisaException(e,sys)
        
    def is_column_exist(self,dataframe:DataFrame)->bool:
        """
        Method Name : is_column_exist
        Description : this method validates existance of categorical and numerical columns
        Output      : returns bool value based on validation result
        On failure  : log error and raises exception
        """
        try:
            dataframe_column = dataframe.columns
            missing_numerical_columns = []
            missing_categorical_columns = []

            for column in self._schema_file['numerical_columns']:
                if column not in dataframe_column:
                    missing_numerical_columns.append(column)

            if len(missing_numerical_columns)>0:
                logging.info(f'missing numerical column {missing_numerical_columns}')

            for column in self._schema_file['categorical_columns']:
                if column not in dataframe_column:
                    missing_categorical_columns.append(column)

            if len(missing_categorical_columns)>0:
                logging.info(f"missing categorical column {missing_categorical_columns}")
            
            return False if len(missing_categorical_columns)>0 or len(missing_numerical_columns)>0 else True
        except Exception as e:
            raise VisaException(e,sys)
        
    @staticmethod
    def read_data(filepath)->DataFrame:
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            raise VisaException(e,sys)
    
    def detect_dataset_drift(self,reference_df:DataFrame,current_df:DataFrame)->bool:
        """
        Method Name : detect_dataset_drift
        Description : this method detects drift in dataset
        Output      : returns bool based on drift result
        On failure  : log error and raises exception
        """
        try:
            data_drift_profile = Profile(sections=[DataDriftProfileSection()])
            data_drift_profile.calculate(reference_df,current_df)

            report = data_drift_profile.json()
            json_report = json.loads(report)

            write_yaml_file(filepath=self.data_validation_config.drift_report_filepath,obj=json_report)

            n_features = json_report['data_drift']['data']['metrics']['n_features']
            n_drifted_features = json_report['data_drift']['data']['metrics']['n_drifted_features']

            logging.info(f"{n_features}/{n_drifted_features} drift detected")

            drift_status = json_report['data_drift']['data']['metrics']['dataset_drift']
            return drift_status
        except Exception as e:
            raise VisaException(e,sys)
        
    def initiate_data_validation(self):
        """
        Method Name : initiate_data_validation
        Description : this method initiates data validation component of pipeline
        Output      : this method returns data_validation_artifact
        On failure  : log error and raises exception
        """
        try:
            validation_error_msg = ""
            logging.info("starting data validation")
            train_df,test_df = (DataValidation.read_data(filepath=self.data_ingestion_artifact.train_file_path),
                                DataValidation.read_data(filepath=self.data_ingestion_artifact.test_file_path))
            
            status = self.validate_number_of_columns(dataframe=train_df)
            logging.info(f"all required columns are present in training dataset {status}")
            if not status:
                validation_error_msg += "columns are missing in training dataset"

            status = self.validate_number_of_columns(dataframe=test_df)
            logging.info(f"all required columns are present in test dataset {status}")
            if not status:
                validation_error_msg += "columns are missing in test dataset"

            status = self.is_column_exist(train_df)
            if not status:
                validation_error_msg += "columns are missing in training dataset"

            status = self.is_column_exist(test_df)
            if not status:
                validation_error_msg += "columns are missing in test dataset"

            validation_status = len(validation_error_msg)==0

            if validation_status:
                drift_status = self.detect_dataset_drift(train_df,test_df)
                
                if drift_status:
                    logging.info('drift detected')
                    validation_error_msg += "drift detected"
                else:
                    validation_error_msg += "drfit not detected"

            else:
                logging.info(f"validation error: {validation_error_msg}")

            data_validation_artifact = DataValidationArtifact(
                validation_status=validation_status,
                message=validation_error_msg,
                drift_report_filepath=self.data_validation_config.drift_report_filepath
            )
            logging.info(f"data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise VisaException(e,sys)
