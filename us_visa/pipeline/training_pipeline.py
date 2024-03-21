import sys

from us_visa.exception import VisaException
from us_visa.logger import logging

from us_visa.components.data_ingestion import DataIngestion
from us_visa.components.data_validation import DataValidation
from us_visa.components.data_transformation import DataTransformation
from us_visa.components.model_trainer import ModelTrainer
from us_visa.components.model_evaluation import ModelEvaluation
from us_visa.components.model_pusher import ModelPusher

from us_visa.entity.config_entity import (DataIngestionConfig,
                                          DataValidationConfig,
                                          DataTransformationConfig,
                                          ModelTrainerConfig,
                                          ModelEvaluationConfig,
                                          ModelPusherConfig)

from us_visa.entity.artifact_entity import (DataIngestionArtifact,
                                            DataValidationArtifact,
                                            DataTransformationArtifact,
                                            ModelTrainerArtifact,
                                            ModelEvaluationArtifact,
                                            ModelPusherArtifact)


class TrainingPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.data_validation_config = DataValidationConfig()
        self.data_transformation_config = DataTransformationConfig()
        self.model_trainer_config = ModelTrainerConfig()
        self.model_evaluation_config = ModelEvaluationConfig()
        self.model_pusher_config = ModelPusherConfig()

    def start_data_ingestion(self)->DataIngestionArtifact:
        """
        This method is initiating data ingestion component of pipeline
        """
        try:
            logging.info('getting data from mongodb')
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info('saved data into train set and test set')
            return data_ingestion_artifact
        except Exception as e:
            raise VisaException(e,sys)
    
    def start_data_validation(self,data_ingestion_artifact:DataIngestionArtifact)->DataValidationArtifact:
        """
        This method is initiating data validation component of pipeline
        """
        try:
            logging.info("starting data validation")
            data_validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact,
                                             data_validation_config=self.data_validation_config)
            data_validation_artifact = data_validation.initiate_data_validation()
            logging.info("performed data validation")
            return data_validation_artifact
        except Exception as e:
            raise VisaException(e,sys)
        
    def start_data_transformation(self,data_ingestion_artifact:DataIngestionArtifact,
                                  data_validation_artifact:DataValidationArtifact)->DataTransformationArtifact:
        """
        This method is initiating data transformation component of pipeline
        """
        try:
            logging.info("starting data transformation")
            data_transformation = DataTransformation(data_ingestion_artifact=data_ingestion_artifact,
                                                     data_validation_artifact=data_validation_artifact,
                                                     data_transformation_config=self.data_transformation_config)
            data_transformation_artifact = data_transformation.initiate_data_transformation()
            logging.info("performed data transformation")
            return data_transformation_artifact
        except Exception as e:
            raise VisaException(e,sys)
        
    def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:
        """
        This method is initiating model trainer component of pipeline
        """
        try:
            logging.info("starting model training")
            model_trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact,
                                         model_trainer_config=self.model_trainer_config)
            model_trainer_artifact = model_trainer.initiate_model_trainer()

            logging.info("performed model training")

            return model_trainer_artifact
        except Exception as e:
            raise VisaException(e,sys)
    
    def start_model_evaluation(self,model_trainer_artifact:ModelTrainerArtifact,
                               data_ingestion_artifact:DataIngestionArtifact)->ModelEvaluationArtifact:
        """
        This method is initiating model evaluation component of pipeline
        """
        try:
            logging.info("starting model evaluation")
            model_evaluation = ModelEvaluation(model_trainer_artifact=model_trainer_artifact,
                                                data_ingestion_artifact=data_ingestion_artifact,
                                                model_eval_config=self.model_evaluation_config)
            model_evaluation_artifact = model_evaluation.initiate_model_evaluation()

            logging.info("performed model evaluation")

            return model_evaluation_artifact
        except Exception as e:
            raise VisaException(e,sys)
        
    def start_model_pusher(self,model_evaluation_artifact:ModelEvaluationArtifact)->ModelPusherArtifact:
        """
        this method is intiating model pusher component of pipeline
        """
        try:
            model_pusher = ModelPusher(model_evaluation_artifact=model_evaluation_artifact,
                                       model_pusher_config=self.model_pusher_config)
            model_pusher_artifact = model_pusher.initiate_model_pusher()
            return model_pusher_artifact
        except Exception as e:
            raise VisaException(e,sys)
        
    def run_pipeline(self):
        """
        this method of TrainingPipeline class is responsible for running complete pipeline
        """
        try:
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact)
            data_transformation_artifact = self.start_data_transformation(data_ingestion_artifact,data_validation_artifact)
            model_trainer_artifact = self.start_model_trainer(data_transformation_artifact)
            model_evaluation_artifact = self.start_model_evaluation(model_trainer_artifact,data_ingestion_artifact)

            if not model_evaluation_artifact.is_model_excepted:
                logging.info("model not accepted")
                return None
            model_pusher_artifact = self.start_model_pusher(model_evaluation_artifact)

        except Exception as e:
            raise VisaException(e,sys)
                
if __name__=='__main__':
    obj = TrainingPipeline()
    obj.run_pipeline()