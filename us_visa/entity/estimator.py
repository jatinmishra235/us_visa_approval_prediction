import sys
from us_visa.exception import VisaException
from us_visa.logger import logging

from pandas import DataFrame
from sklearn.pipeline import Pipeline

class TargetValueMapping:
    def __init__(self):
        self.Certified: int = 0
        self.Denied: int = 1

    def _asdict(self):
        return self.__dict__
    
    def reverse_mapping(self):
        mapping_response = self._asdict()
        return dict(zip(mapping_response.values(),mapping_response.keys()))
    
class USvisaModel:
    def __init__(self,preprocessing_obj:Pipeline,trained_model_obj:object):
        """
        :param preprocessing_obj : input object of preprocessor
        :param trained_model_obj : input object of model
        """
        self.preprocessor_object = preprocessing_obj
        self.model_object = trained_model_obj
    
    def predict(self,dataframe:DataFrame)->DataFrame:
        """
        Function accepts raw inputs and then transformed raw input using preprocessing_object
        which guarantees that the inputs are in the same format as the training data
        At last it performs prediction on transformed features
        """  
        try:
            logging.info("entered predict method of USvisaModel")
            transformed_features = self.preprocessor_object.transform(dataframe)

            return self.model_object.predict(transformed_features)
        except Exception as e:
            raise VisaException(e,sys)

    def __repr__(self):
        return f"{type(self.model_object).__name__}()"
    
    def __str__(self):
        return f"{type(self.model_object).__name__}()"

