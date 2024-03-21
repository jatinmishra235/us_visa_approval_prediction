from us_visa.cloud_storage.aws_storage import SimpleStorageService
from us_visa.exception import VisaException
from us_visa.entity.estimator import USvisaModel
import sys
from pandas import DataFrame


class USvisaEstimator:
    """
    This class is used to save and retrieve usvisas model in s3_bucket and to to prediction
    """
    def __init__(self,bucket_name,model_path):
        """
        :param : bucket_name : name of the bucket
        :param : model_path : path of the model in s3_bucket
        """
        self.bucket_name = bucket_name
        self.s3 = SimpleStorageService()
        self.model_path = model_path
        self.loaded_model:USvisaModel=None

    def is_model_present(self,model_path):
        try:
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name,s3_key=model_path)
        except VisaException as e:
            print(e)
            return False
    
    def load_model(self)->USvisaModel:
        """
        load the model from model path
        """
        return self.s3.load_model(self.model_path,bucket_name=self.bucket_name)

    def save_model(self,from_file,remove=False):
        """
        save the model to model path
        :param from_file: your loacl system model path
        :param remove: by default it is false, it means you will your model locally available 
        """
        try:
            self.s3.upload_file(from_file,
                                to_filename=self.model_path,
                                bucket_name=self.bucket_name,
                                remove=remove)
    
        except VisaException as e:
            raise VisaException(e,sys)
        
    def predict(self,dataframe):
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe)
        except VisaException as e:
            raise VisaException(e,sys)