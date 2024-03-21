import sys
import numpy as np

from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
from neuro_mf import ModelFactory

from us_visa.exception import VisaException
from us_visa.logger import logging

from us_visa.utils.main_utils import load_numpy_array_data,load_object,save_object
from us_visa.entity.config_entity import ModelTrainerConfig
from us_visa.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact,ClassificationMetric
from us_visa.entity.estimator import USvisaModel

class ModelTrainer:
    def __init__(self, data_transformation_artifact:DataTransformationArtifact,model_trainer_config:ModelTrainerConfig):
        """
        :Param data_transformation_artifact : Output component of data transformation stage
        :Param model_trainer_config : Configuration for ModelTrainer
        """
        self.data_transformation_artifact = data_transformation_artifact
        self.model_trainer_config = model_trainer_config

    def get_model_object_and_report(self,train_arr:np.array,test_arr:np.array):
        """
        Method name : get_model_object_and_report
        Description : this method uses neuro_mt to get best model and report
        Output      : returns metric artifact and best model object
        On failure  : writes error log and raises exception
        """
        try:
            logging.info("Using neuro_mf to get best model object and report")
            model_factory = ModelFactory(model_config_path=self.model_trainer_config.model_config_file_path)

            x_train,y_train,x_test,y_test = (train_arr[:,:-1],train_arr[:,-1],test_arr[:,:-1],test_arr[:,-1])

            best_model_detail = model_factory.get_best_model(
                X=x_train,y=y_train,base_accuracy=self.model_trainer_config.expected_accuracy
            )
            model_object = best_model_detail.best_model

            y_pred = model_object.predict(x_test)

            accuracy = accuracy_score(y_test,y_pred)
            f1 = f1_score(y_test,y_pred)
            precision = precision_score(y_test,y_pred)
            recall = recall_score(y_test,y_pred)

            metric_artifact = ClassificationMetric(f1_score=f1,precision_score=precision,recall_score=recall)

            return best_model_detail, metric_artifact
        
        except Exception as e:
            raise VisaException(e,sys)
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        """
        Method name : initiate_model_trainer
        Description : this method intiating model_trainer component of pipeline
        Output      : returns model_trainer_artifact
        On failure  : writes exception log and raises exception
        """
        try:
            logging.info("entered initiate_model_trainer component of ModelTrainer class")
            train_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_train_filepath)
            test_arr = load_numpy_array_data(self.data_transformation_artifact.transformed_test_filepath)

            best_model_detail,metric_artifact = self.get_model_object_and_report(train_arr=train_arr,test_arr=test_arr)

            preprocessing_obj = load_object(self.data_transformation_artifact.transformed_object_filepath)

            if best_model_detail.best_score < self.model_trainer_config.expected_accuracy:
                logging.info("No best model found with score more than best score")
                raise Exception("No best model found with score more than best score")
            
            usvisa_model = USvisaModel(preprocessing_obj=preprocessing_obj,trained_model_obj=best_model_detail.best_model)

            logging.info("created usvisa model object with preprocessor and model")

            save_object(filepath=self.model_trainer_config.trained_model_filepath,object=usvisa_model)

            model_trainer_artifact = ModelTrainerArtifact(model_file_path=self.model_trainer_config.trained_model_filepath,metric_artifact=metric_artifact)

            logging.info(f"model trainer artifact {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e :
            raise VisaException(e,sys)
