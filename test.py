import os
from datetime import datetime

from housing.components.data_ingestion import DataIngestion
from housing.components.data_transformation import DataTransformation
from housing.components.data_validation import DataValidation
from housing.config.configuration import Configuration
from housing.components.model_trainer import ModelTrainer
from housing.utilities.util import get_file_join

print(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
print(datetime.now())

# os.makedirs("LOG_DIR", exist_ok=True)
LOG_FILE_PATH = os.path.join("LOG_DIR", "LOG_FILE_NAME")
print(LOG_FILE_PATH)
print(os.getcwd())
# print(get_file_join())
c = Configuration()
# print(c.config_info_dict)
# print(c.get_training_pipeline_config())
# print(c.get_model_pusher_config())
# print(c.get_model_trainer_config())
# print(c.get_data_ingestion_config())
# print(c.get_data_validation_config())
# print(c.get_model_evaluation_config())
print(os.listdir("/"))
print(os.listdir("/")[0])
di = DataIngestion(c.get_data_ingestion_config())
dv = DataValidation(c.get_data_validation_config(), di.initiate_data_ingestion())
# dv.validate_dataset_schema()
dv.is_data_drift_found()
dt = DataTransformation(c.get_data_transformation_config(), di.initiate_data_ingestion(), dv.initiate_data_validation())

dt.initiate_data_transformation()
mt = ModelTrainer(c.get_model_trainer_config(), dt.initiate_data_transformation())

mt.initiate_model_trainer()
