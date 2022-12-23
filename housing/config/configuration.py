from constant import *
from entity.data_ingestion_entity import DataIngestionEntity
from entity.data_transformation_entity import DataTransformationEntity
from entity.data_validation_entity import DataValidationEntity
from entity.model_evaluation_entity import ModelEvaluationEntity
from entity.model_pusher_entity import ModelPusherEntity
from entity.model_trainer_entity import ModelTrainerEntity
from entity.training_pipeline_entity import TrainingPipelineEntity
from housing.utilities.util import get_dictionary_from_json, get_file_join
from housing.exception import CustomException
import sys
from housing.logger import logging
from datetime import datetime


class Configuration:
    def __init__(self, config_file_path: str = CONFIG_FILE_PATH, current_time_stamp: str = CURRENT_TIME_STAMP) -> None:
        try:
            self.config_info_dict = get_dictionary_from_json(config_file_path)
            self.current_time_stamp = current_time_stamp
            self.training_pipeline_config = self.get_training_pipeline_config()
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_training_pipeline_config(self) -> TrainingPipelineEntity:
        """
        :return:TrainingPipelineConfig
        """
        try:
            training_pipeline_config = self.config_info_dict[TRAINING_PIPELINE_CONFIG]
            artifact_dir = get_file_join(ROOT_DIR,
                                         training_pipeline_config[PIPELINE_NAME],
                                         training_pipeline_config[ARTIFACT_DIR])
            training_pipeline_config = TrainingPipelineEntity(artifact_dir=artifact_dir)
            logging.info(f"Training pipeline config: {training_pipeline_config}")
            return training_pipeline_config
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_data_ingestion_config(self) -> DataIngestionEntity:
        try:
            # artifact directory from training pipeline config
            artifact_dir = self.training_pipeline_config.artifact_dir
            data_ingestion_artifact_dir = get_file_join(
                artifact_dir,
                DATA_INGESTION_ARTIFACT_DIR,
                self.time_stamp
            )
            data_ingestion_info = self.config_info_dict[DATA_INGESTION_CONFIG]
            dataset_download_url = data_ingestion_info[DATASET_DOWNLOAD_URL]
            tgz_download_dir = get_file_join(
                data_ingestion_artifact_dir,
                data_ingestion_info[TGZ_DOWNLOAD_DIR]
            )
            raw_data_dir = get_file_join(data_ingestion_artifact_dir,
                                         data_ingestion_info[DATA_INGESTION_RAW_DATA_DIR_KEY]
                                         )

            ingested_data_dir = get_file_join(
                data_ingestion_artifact_dir,
                data_ingestion_info[DATA_INGESTION_INGESTED_DIR_NAME_KEY]
            )
            ingested_train_dir = get_file_join(
                ingested_data_dir,
                data_ingestion_info[DATA_INGESTION_TRAIN_DIR_KEY]
            )
            ingested_test_dir = get_file_join(
                ingested_data_dir,
                data_ingestion_info[DATA_INGESTION_TEST_DIR_KEY]
            )
            data_ingestion_config = DataIngestionEntity(
                dataset_download_url=dataset_download_url,
                tgz_download_dir=tgz_download_dir,
                raw_data_dir=raw_data_dir,
                ingested_train_dir=ingested_train_dir,
                ingested_test_dir=ingested_test_dir
            )
            logging.info(f"Data Ingestion config: {data_ingestion_config}")
            return data_ingestion_config

        except Exception as e:
            raise CustomException(e, sys) from e

    def get_data_validation_config(self) -> DataValidationEntity:
        try:
            artifact_dir = self.training_pipeline_config.artifact_dir
            data_validation_artifact_dir = get_file_join(artifact_dir, DATA_VALIDATION_ARTIFACT_DIR_NAME,
                                                         self.current_time_stamp)
            data_validation_config = self.config_info[DATA_VALIDATION_CONFIG_KEY]

            schema_file_path = get_file_join(ROOT_DIR,
                                             data_validation_config[DATA_VALIDATION_SCHEMA_DIR_KEY],
                                             data_validation_config[DATA_VALIDATION_SCHEMA_FILE_NAME_KEY]
                                             )

            report_file_path = get_file_join(data_validation_artifact_dir,
                                             data_validation_config[DATA_VALIDATION_REPORT_FILE_NAME_KEY]
                                             )

            report_page_file_path = get_file_join(data_validation_artifact_dir,
                                                  data_validation_config[DATA_VALIDATION_REPORT_PAGE_FILE_NAME_KEY]

                                                  )

            data_validation_config = DataValidationEntity(
                schema_file_path=schema_file_path,
                report_file_path=report_file_path,
                report_page_file_path=report_page_file_path,
            )
            return data_validation_config

        except Exception as e:
            raise CustomException(e, sys) from e

    def get_data_transformation_config(self) -> DataTransformationEntity:
        try:
            artifact_dir = self.training_pipeline_config.artifact_dir

            data_transformation_artifact_dir = get_file_join(
                artifact_dir,
                DATA_TRANSFORMATION_ARTIFACT_DIR,
                self.time_stamp
            )

            data_transformation_config_info = self.config_info[DATA_TRANSFORMATION_CONFIG_KEY]

            add_bedroom_per_room = data_transformation_config_info[DATA_TRANSFORMATION_ADD_BEDROOM_PER_ROOM_KEY]

            preprocessed_object_file_path = get_file_join(
                data_transformation_artifact_dir,
                data_transformation_config_info[DATA_TRANSFORMATION_PREPROCESSING_DIR_KEY],
                data_transformation_config_info[DATA_TRANSFORMATION_PREPROCESSED_FILE_NAME_KEY]
            )

            transformed_train_dir = get_file_join(
                data_transformation_artifact_dir,
                data_transformation_config_info[DATA_TRANSFORMATION_DIR_NAME_KEY],
                data_transformation_config_info[DATA_TRANSFORMATION_TRAIN_DIR_NAME_KEY]
            )

            transformed_test_dir = get_file_join(
                data_transformation_artifact_dir,
                data_transformation_config_info[DATA_TRANSFORMATION_DIR_NAME_KEY],
                data_transformation_config_info[DATA_TRANSFORMATION_TEST_DIR_NAME_KEY]

            )

            data_transformation_config = DataTransformationEntity(
                add_bedroom_per_room=add_bedroom_per_room,
                preprocessed_object_file_path=preprocessed_object_file_path,
                transformed_train_dir=transformed_train_dir,
                transformed_test_dir=transformed_test_dir
            )

            logging.info(f"Data transformation config: {data_transformation_config}")
            return data_transformation_config
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_model_trainer_config(self) -> ModelTrainerEntity:
        try:
            artifact_dir = self.training_pipeline_config.artifact_dir

            model_trainer_artifact_dir = get_file_join(
                artifact_dir,
                MODEL_TRAINER_ARTIFACT_DIR,
                self.time_stamp
            )
            model_trainer_config_info = self.config_info[MODEL_TRAINER_CONFIG_KEY]
            trained_model_file_path = get_file_join(model_trainer_artifact_dir,
                                                    model_trainer_config_info[MODEL_TRAINER_TRAINED_MODEL_DIR_KEY],
                                                    model_trainer_config_info[MODEL_TRAINER_TRAINED_MODEL_FILE_NAME_KEY]
                                                    )

            model_config_file_path = get_file_join(model_trainer_config_info[MODEL_TRAINER_MODEL_CONFIG_DIR_KEY],
                                                   model_trainer_config_info[MODEL_TRAINER_MODEL_CONFIG_FILE_NAME_KEY]
                                                   )

            base_accuracy = model_trainer_config_info[MODEL_TRAINER_BASE_ACCURACY_KEY]

            model_trainer_config = ModelTrainerEntity(
                trained_model_file_path=trained_model_file_path,
                base_accuracy=base_accuracy,
                model_config_file_path=model_config_file_path
            )
            logging.info(f"Model trainer config: {model_trainer_config}")
            return model_trainer_config
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_model_evaluation_config(self) -> ModelEvaluationEntity:
        try:
            artifact_dir = get_file_join(self.training_pipeline_config.artifact_dir,
                                         MODEL_EVALUATION_ARTIFACT_DIR, )

            model_evaluation_config = self.config_info[MODEL_EVALUATION_CONFIG_KEY]

            model_evaluation_file_path = get_file_join(artifact_dir,
                                                       model_evaluation_config[MODEL_EVALUATION_FILE_NAME_KEY])
            response = ModelEvaluationEntity(model_evaluation_file_path=model_evaluation_file_path,
                                             time_stamp=self.time_stamp)

            logging.info(f"Model Evaluation Config: {response}.")
            return response
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_model_pusher_config(self) -> ModelPusherEntity:
        try:
            time_stamp = f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
            model_pusher_config_info = self.config_info[MODEL_PUSHER_CONFIG_KEY]
            export_dir_path = get_file_join(ROOT_DIR, model_pusher_config_info[MODEL_PUSHER_MODEL_EXPORT_DIR_KEY],
                                            time_stamp)

            model_pusher_config = ModelPusherEntity(export_dir_path=export_dir_path)
            logging.info(f"Model pusher config {model_pusher_config}")
            return model_pusher_config

        except Exception as e:
            raise CustomException(e, sys) from e
