import sys

from us_visa.cloud_storage.aws_storage import SimpleStorageService
from us_visa.exception import VisaException
from us_visa.logger import logging
from us_visa.entity.artifact_entity import ModelPusherArtifact,ModelEvaluationArtifact
from us_visa.entity.config_entity import ModelPusherConfig
from us_visa.entity.s3_estimator import USvisaEstimator


class ModelPusher:
    def __init__ (self, model_evaluation_artifact:ModelEvaluationArtifact,
                  model_pusher_config:ModelPusherConfig):
        """
        :param model_evaluation_artifact: output reference of model evaluation artifact stage
        :param model_pusher_config: configuration for model pusher
        """
        try:
            self.s3 = SimpleStorageService()
            self.model_evaluation_artifact = model_evaluation_artifact
            self.model_pusher_config = model_pusher_config
            self.usvisa_estimator = USvisaEstimator(bucket_name=model_pusher_config.bucket_name,
                                                    model_path=model_pusher_config.s3_model_key_path)
        except Exception as e:
            raise VisaException(e,sys)
        
    def initiate_model_pusher(self)->ModelPusherArtifact:
        """
        Method_name: initiate_model_pusher
        Description: this method initiates model_pusher steos
        output: retunrs model pusher artifact
        On failure: writes exception log and raises exception
        """
        try:
            logging.info("uploading artifact folder to s3 bucket")

            self.usvisa_estimator.save_model(from_file=self.model_evaluation_artifact.trained_model_path)

            model_pusher_artifact = ModelPusherArtifact(bucket_name=self.model_pusher_config.bucket_name,
                                                        s3_model_path=self.model_pusher_config.s3_model_key_path)
            
            logging.info("uploaded artifacts folder to s3 bucket")
            logging.info(f"model pusher artifacts : {model_pusher_artifact}")

            return model_pusher_artifact
        except Exception as e:
            raise VisaException(e,sys)
        