import shutil
import sys

from entity.artifact_entity import ModelEvaluationArtifact, ModelPusherArtifact
from entity.model_pusher_entity import ModelPusherEntity
from housing.exception import CustomException
from housing.logger import logging
from housing.utilities.util import get_base_file_name, get_file_join, make_directories


class ModelPusher:

    def __init__(self, model_pusher_config: ModelPusherEntity,
                 model_evaluation_artifact: ModelEvaluationArtifact
                 ):
        try:
            logging.info(f"{'>>' * 30}Model Pusher log started.{'<<' * 30} ")
            self.model_pusher_config = model_pusher_config
            self.model_evaluation_artifact = model_evaluation_artifact

        except Exception as e:
            raise CustomException(e, sys) from e

    def export_model(self) -> ModelPusherArtifact:
        try:
            evaluated_model_file_path = self.model_evaluation_artifact.evaluated_model_path
            export_dir = self.model_pusher_config.export_dir_path
            model_file_name = get_base_file_name(evaluated_model_file_path)
            export_model_file_path = get_file_join(export_dir, model_file_name)
            logging.info(f"Exporting model file: [{export_model_file_path}]")
            make_directories(export_dir)

            shutil.copy(src=evaluated_model_file_path, dst=export_model_file_path)
            # we can call a function to save model to Azure blob storage/ google cloud strorage / s3 bucket
            logging.info(
                f"Trained model: {evaluated_model_file_path} is copied in export dir:[{export_model_file_path}]")

            model_pusher_artifact = ModelPusherArtifact(is_model_pusher=True,
                                                        export_model_file_path=export_model_file_path
                                                        )
            logging.info(f"Model pusher artifact: [{model_pusher_artifact}]")
            return model_pusher_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            return self.export_model()
        except Exception as e:
            raise CustomException(e, sys) from e

    def __del__(self):
        logging.info(f"{'>>' * 20}Model Pusher log completed.{'<<' * 20} ")
