from us_visa.exception import VisaException
import yaml
import sys
import os
import pickle
import numpy as np
from pandas import DataFrame

def write_yaml_file(filepath:str,obj:object,replace=False):
    try:
        if replace==True:
            if os.path.exists(filepath):
                os.remove(filepath)
        os.makedirs(os.path.dirname(filepath),exist_ok=True)

        with open(filepath,'w') as file_obj:
            yaml.dump(obj,file_obj)
    except Exception as e:
        raise VisaException(e,sys)

def read_yaml_file(filepath:str):
    try:
        with open(filepath,'r') as file_obj:
            return yaml.safe_load(file_obj)
    except Exception as e: 
        raise VisaException(e,sys)
    
def save_object(filepath,object):
    try:
        os.makedirs(os.path.dirname(filepath),exist_ok=True)
        with open(filepath,'wb') as file_obj:
            return pickle.dump(object,file_obj)
    except Exception as e :
        raise VisaException(e,sys)
    
def load_object(filepath):
    try:
        with open(filepath, 'rb') as file_obj:
            return pickle.load(file_obj)
    except Exception as e:
        raise VisaException(e,sys)
    
def save_numpy_array_data(filepath:str,array:np.array):
    try:
        dir_path = os.path.dirname(filepath)
        os.makedirs(dir_path,exist_ok=True)
        with open(filepath,'wb') as file_obj:
            np.save(file_obj,array)
    except Exception as e:
        raise VisaException(e,sys)
    
def load_numpy_array_data(filepath:str):
    try:
        with open(filepath,'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise VisaException(e,sys)
def drop_columns(df:DataFrame,cols:list)->DataFrame:
    try:
        df = df.drop(columns=cols,axis=1)
        return df
    except Exception as e:
        raise VisaException(e,sys)


