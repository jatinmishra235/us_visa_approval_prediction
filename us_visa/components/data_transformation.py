import json 
import sys
import pandas as pd
import numpy as np
from pandas import DataFrame

from us_visa.exception import VisaException
from us_visa.logger import logging

from imblearn.combine import SMOTEENN
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder, PowerTransformer

from us_visa.constant import CURRENT_YEAR, SCHEMA_FILE_PATH, TARGET_COLUMN

from us_visa.entity.config_entity import DataTransformationConfig
from us_visa.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact

from us_visa.entity.estimator import TargetValueMapping

from us_visa.utils.main_utils import save_object,save_numpy_array_data,read_yaml_file,drop_columns


class DataTransformation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_artifact:DataValidationArtifact,
                 data_transformation_config:DataTransformationConfig):
        """
        :param data_ingestion_artifact: Output referenece of data ingestion artifact stage
        :param data_validation_artifact: Output referenece of data validation artifact stage
        :param data_transformation_config: configuration for data transformation 
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
            self._schema_config = read_yaml_file(filepath=SCHEMA_FILE_PATH)
        except Exception as e:
            raise VisaException(e,sys)
    
    @staticmethod
    def read_data(filepath)->DataFrame:
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            raise VisaException(e,sys)
        
    def get_data_transformer_object(self)->Pipeline:
        """
        Method Name : get_data_transformer_object
        Description : this method creates and returns data transformer object for data
        Output      : data transformer object is returned
        On failure  : write error log and raise exception
        """
        logging.info("entered get_data_transformer_object method of DataTransformation class")
        try:
            numeric_transformer = StandardScaler()
            oh_transformer = OneHotEncoder()
            ordinal_encoder = OrdinalEncoder()

            oh_columns = self._schema_config['oh_columns']
            or_columns = self._schema_config['or_columns']
            transform_columns = self._schema_config['transform_columns']
            num_columns = self._schema_config['num_features']

            transform_pipe = Pipeline(steps=[
                ('power_transformer',PowerTransformer('yeo-johnson'))
            ])

            preprocessor = ColumnTransformer([
                ('OneHotencoder',oh_transformer,oh_columns),
                ('OrdinalEncoder',ordinal_encoder,or_columns),
                ('power_transformer',transform_pipe,transform_columns),
                ('StandaredScaler',numeric_transformer,num_columns)
            ])

            logging.info("cretead preprocessor object")

            return preprocessor
    
        except Exception as e:
            raise VisaException(e,sys)


    def initiate_data_transformation(self)->DataTransformationArtifact:
        """
        Method Name : initiate_data_transformation
        Description : this method initiates data transformation component of pipeline
        Output      : Data transformation artifact is returned
        On failure  : writes error log and raises exception
        """
        try:
            if self.data_validation_artifact.validation_status:
                logging.info("starting data transformation")
                preprocessor = self.get_data_transformer_object()
                logging.info("got preprocessor object")

                train_df = DataTransformation.read_data(self.data_ingestion_artifact.train_file_path)
                test_df = DataTransformation.read_data(self.data_ingestion_artifact.test_file_path)

                input_feature_train_df = train_df.drop(TARGET_COLUMN,axis=1)
                target_column_train_df = train_df[TARGET_COLUMN]

                logging.info("got input and target features of input dataframe")

                input_feature_train_df['company_age'] = CURRENT_YEAR - input_feature_train_df['yr_of_estab']

                logging.info("added company age column")

                drop_cols = self._schema_config['drop_columns']

                logging.info("drop columns in drop_cols of Training dataset")

                input_feature_train_df = drop_columns(df=input_feature_train_df,cols=drop_cols)

                target_column_train_df = target_column_train_df.replace(
                    TargetValueMapping()._asdict()
                )

                input_feature_test_df = test_df.drop(TARGET_COLUMN, axis=1)
                target_feature_test_df = test_df[TARGET_COLUMN]

                input_feature_test_df['company_age'] = CURRENT_YEAR - input_feature_test_df['yr_of_estab']

                logging.info("added company_age column to test dataset")

                input_feature_test_df = drop_columns(df=input_feature_test_df,cols=drop_cols)

                logging.info("drop the columns in drop_cols of test dataset")

                target_feature_test_df = target_feature_test_df.replace(
                    TargetValueMapping()._asdict()
                )

                logging.info("applying preprocessing object on training and testing dataset")

                input_features_train_arr = preprocessor.fit_transform(input_feature_train_df)
                input_features_test_arr = preprocessor.transform(input_feature_test_df)

                smt = SMOTEENN(sampling_strategy='minority')

                input_feature_train_final,target_feature_train_final = smt.fit_resample(
                    input_features_train_arr,target_column_train_df
                )

                logging.info("applied SMOTEEN on training dataset")

                input_feature_test_final,target_feature_test_final = smt.fit_resample(
                    input_features_test_arr,target_feature_test_df
                )

                logging.info("applied SMOTEEN on test dataset")

                train_arr = np.c_[input_feature_train_final,np.array(target_feature_train_final)]
                test_arr = np.c_[input_feature_test_final,np.array(target_feature_test_final)]

                logging.info("created train array and test array")

                save_object(self.data_transformation_config.transformed_object_filepath,preprocessor)
                save_numpy_array_data(self.data_transformation_config.transformed_train_filepath,train_arr)
                save_numpy_array_data(self.data_transformation_config.transformed_test_filepath,test_arr)

                logging.info("saved the preprocessor object")

                data_transformation_artifact = DataTransformationArtifact(
                    transformed_object_filepath=self.data_transformation_config.transformed_object_filepath,
                    transformed_train_filepath=self.data_transformation_config.transformed_train_filepath,
                    transformed_test_filepath=self.data_transformation_config.transformed_test_filepath
                )
                logging.info(f"data transformation artifact: {data_transformation_artifact}")
                return data_transformation_artifact
        except Exception as e:
            raise VisaException(e,sys)