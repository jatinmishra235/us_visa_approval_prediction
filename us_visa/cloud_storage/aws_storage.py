import boto3
from us_visa.configuration.aws_connection import S3Client
import os,sys
from us_visa.logger import logging
from us_visa.exception import VisaException
from mypy_boto3_s3.service_resource import Bucket
from botocore.exceptions import ClientError
from pandas import DataFrame, read_csv
import pickle
from io import StringIO



class SimpleStorageService:

    def __init__(self):
        s3_client=S3Client()
        self.s3_resource = s3_client.s3_resource
        self.s3_client = s3_client.s3_client

    def s3_key_path_available(self,bucket_name,s3_key):
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=s3_key)]
            if len(file_objects) > 0 :
                return True
            else:
                return False
        except Exception as e:
            raise VisaException(e,sys)

    @staticmethod
    def read_object(object_name:str, decode: bool=True, make_readable:bool = False):
        """
        Method_name : read_object
        Description : This method reads object_name object with kwargs
        """
        try:
            func=(
                lambda: object_name.get()['Body'].read().decode()
                if decode is True
                else object_name.get()['Body'].read()
            )
            conv_func = lambda: StringIO(func()) if make_readable is True else func()
            return conv_func()
        except Exception as e:
            raise VisaException(e,sys)

    def get_bucket(self, bucket_name):
        """
        Method_name : get_bucket
        Description : This method gets the bucket object based on bucket name
        Output      : bucket object is returned based on bucket name
        On failure  : writes error log and raises exception
        """
        try:
            bucket = self.s3_resource.Bucket(bucket_name)
            return bucket
        except Exception as e:
            raise VisaException(e,sys)
        
    def get_file_object(self, filename, bucket_name):
        """
        Method_name : get_file_object
        Description : this method gets file object from bucket_name based on filename
        """
        try:
            bucket = self.get_bucket(bucket_name)

            file_objects = [file_object for file_object in bucket.objects.filter(Prefix=filename)]

            func = lambda x: x[0] if len(x) == 1 else x

            file_objs = func(file_objects)

            return file_objs
        except Exception as e:
            raise VisaException(e,sys)
        
    def load_model(self, model_name, bucket_name, model_dir=None):
        """
        Method_name : load_model
        Description : this method loads model_name model from bucket_name with kwargs
        """
        try:
            func=(
                lambda: model_name
                if model_dir is None
                else model_dir + '/' + model_name
            )
            model_file = func()
            file_object = self.get_file_object(model_file,bucket_name)
            model_obj = self.read_object(file_object, decode=False)
            model = pickle.loads(model_obj)
            return model
        except Exception as e:
            raise VisaException(e,sys)
        
    def create_folder(self, foldr_name, bucket_name):
        """
        Method_name : create_folder
        Description : this method creates folder_name folder in bucket_name bucket
        """
        try:
            self.s3_resource.Object(bucket_name, foldr_name).load()
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                folder_obj = foldr_name + '/'
                self.s3_client.put_object(Bucket=bucket_name, Key=folder_obj)
            else:
                pass
    
    def upload_file(self, from_filename, to_filename, bucket_name, remove = True):
        """
        Method_name : upload_file
        Description : this method uploads the from_filename to bucket_name with to_filename as bucket filename
        """
        try:
            logging.info(f"uploading {from_filename} file to {to_filename} file in {bucket_name} bucket")

            self.s3_resource.meta.client.upload_file(from_filename, bucket_name, to_filename)

            logging.info(f"uploaded {from_filename} file to {to_filename} file in {bucket_name} bucket")

            if remove is True:
                os.remove(from_filename)
                logging.info(f"remove is set to {remove}, deleted the file")
            else:
                logging.info(f"remove is set to {remove}, not deleted the file")
        except Exception as e:
            raise VisaException(e,sys)
        
    def upload_df_as_csv(self,dataframe,local_filename,bucket_filename,bucket_name):
        """
        Method_name : upload_df_as_csv
        Description : this method uploads dataframe to bucket_filename csv file in bucket_name bucket
        """
        try:
            dataframe.to_csv(local_filename, index=None, header=True)
            self.upload_file(local_filename, bucket_filename, bucket_name)

        except Exception as e:
            raise VisaException(e,sys)
    
    def get_df_from_object(self,object_):
        """
        Method_name : get_df_from_object
        Description : this method gets dataframe from object_
        """
        try:
            content = self.read_object(object_,make_readable=True)
            df = read_csv(content, na_values='na')
            return df
        except Exception as e:
            raise VisaException(e,sys)
        
    def read_csv(self, filename, bucket_name):
        """
        Method_name : read_csv
        Description : this method reads csv file from bucket_name bucket
        """
        try:
            csv_obj = self.get_file_object(filename,bucket_name)
            df = self.get_df_from_object(csv_obj)
            return df
        except Exception as e:
            raise VisaException(e,sys)