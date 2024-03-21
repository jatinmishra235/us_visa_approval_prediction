from datetime import date
import os

DATABASE_NAME = 'US_VISA'
COLLECTION_NAME = 'visa_data'
MONGODB_URL_KEY = 'MONGODB_URL'

ARTIFACT_DIR = 'artifact'

MODEL_FILE_NAME = 'model.pkl'

PIPELINE_NAME = 'usvisa'

TARGET_COLUMN = 'case_status'
CURRENT_YEAR = date.today().year
PREPROCESSING_OBJECT_FILE_NAME = 'preprocessor.pkl'
FILENAME = 'usvisa.csv'
TRAIN_FILE_NAME = 'train.csv'
TEST_FILE_NAME = 'test.csv'

SCHEMA_FILE_PATH = os.path.join('config','schema.yaml')

AWS_ACCESS_KEY_ID_ENV_KEY = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY_ENV_KEY = "AWS_SECRET_ACCESS_KEY"
REGION_NAME = "us-east-1"


"""
Data ingestion constants name starts with DATA_INGESTION VAR name
"""
DATA_INGESTION_COLLECTION_NAME = 'visa_data'
DATA_INGESTION_DIR_NAME = 'data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIR = 'feature_store'
DATA_INGESTION_INGESTED_DIR = 'ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 0.2

"""
Data validation constants name starts with DATA_VALIDATION VAR name
"""

DATA_VALIDATION_DIR = 'data_validation'
DATA_VALIDATION_DRIFT_REPORT_DIR = 'drift_report'
DATA_VALIDATION_DRIFT_REPORT_FILENAME = 'drift.yaml'

"""
Data transformation constants name starts with DATA_TRANSFORMATION VAR name
"""

DATA_TRANSFORMATION_DIR_NAME = 'data_transformation'
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR = 'transformed'
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR = 'transformed_object'

"""
Model trainer constants name starts with MODEL_TRAINER VAR name
"""

MODEL_TAINER_DIR_NAME = 'model_trainer'
MODEL_TRAINER_TRAINED_MODEL_DIR = 'trained_model'
MODEL_TRAINER_TRAINED_MODEL_NAME = 'model.pkl'
MODEL_TRAINER_EXPECTED_SCORE = 0.6
MODEL_TRAINER_MODEL_CONFIG_FILE_PATH = os.path.join('config','model.yaml')

MODEL_EVALUATION_CHANGED_THRESHOLD_SCORE : float = 0.02
MODEL_BUCKET_NAME = "usvisa-model-jatin"
MODEL_PUSHER_S3_KEY = "model-registry"


APP_HOST = "0.0.0.0"
APP_PORT = 8080