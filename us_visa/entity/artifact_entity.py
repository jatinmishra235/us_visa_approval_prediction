from dataclasses import dataclass
@dataclass
class DataIngestionArtifact:
    train_file_path : str
    test_file_path : str

@dataclass
class DataValidationArtifact:
    validation_status : bool
    message : str
    drift_report_filepath : str

@dataclass
class DataTransformationArtifact:
    transformed_train_filepath : str
    transformed_test_filepath : str
    transformed_object_filepath : str

@dataclass
class ClassificationMetric:
    f1_score : float
    precision_score : float
    recall_score : float

@dataclass
class ModelTrainerArtifact:
    model_file_path : str
    metric_artifact : ClassificationMetric

@dataclass
class ModelEvaluationArtifact:
    is_model_excepted : bool
    changed_accuracy : float
    s3_model_path : str
    trained_model_path : str

@dataclass
class ModelPusherArtifact:
    bucket_name : str
    s3_model_path : str