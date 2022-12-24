import json
import sys

import pandas as pd
import numpy as np

from entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from entity.data_validation_entity import DataValidationEntity
from housing.exception import CustomException
from housing.logger import logging
from housing.utilities.util import check_dir_exists, make_directories, get_dir, get_dictionary_from_json
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab


class DataValidation:

    def __init__(self, data_validation_config: DataValidationEntity,
                 data_ingestion_artifact: DataIngestionArtifact):
        try:
            logging.info(f"{'>> ' * 30}Data Valdaition log started.{'<< ' * 30} \n\n")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_train_and_test_df(self):
        try:
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df, test_df
        except Exception as e:
            raise CustomException(e, sys) from e

    def is_train_test_file_exists(self) -> bool:

        try:
            logging.info("Checking if training and test file is available")
            is_train_file_exist = False
            is_test_file_exist = False

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            is_train_file_exist = check_dir_exists(train_file_path)
            is_test_file_exist = check_dir_exists(test_file_path)

            is_available = is_train_file_exist and is_test_file_exist

            logging.info(f"Is train and test file exists?-> {is_available}")

            if not is_available:
                training_file = self.data_ingestion_artifact.train_file_path
                testing_file = self.data_ingestion_artifact.test_file_path
                message = f"Training file: {training_file} or Testing file: {testing_file}" \
                          "is not present"
                raise Exception(message)

            return is_available
        except Exception as e:
            raise CustomException(e, sys) from e

    def validate_dataset_schema(self) -> bool:

        try:
            schema_file_path = self.data_validation_config.schema_file_path
            schema_json = get_dictionary_from_json(schema_file_path)
            train_df, test_df = self.get_train_and_test_df()
            print(type(np.array(train_df.columns)), train_df.columns)
            columns_from_df = np.array(train_df.columns)
            is_size_same = len(columns_from_df) == len(schema_json["columns"].keys())
            all_column_name_present = True
            for i in columns_from_df:
                if i in schema_json["columns"]:
                    print(i, "True")
                else:
                    all_column_name_present = False
                    print(i, "False")
            print(type(train_df.dtypes), train_df.dtypes)

            numCols = list(set(train_df.select_dtypes("number").columns))
            catCols = list(set(train_df.select_dtypes("object").columns))
            is_numeric_column_size = len(numCols) == len(schema_json["numerical_columns"])
            is_categorical_column_size = len(catCols) == len(schema_json["categorical_columns"])
            print(f"numerical is {is_numeric_column_size} and categorical {is_categorical_column_size}")
            is_categorical_value_equal = len(np.array(train_df["ocean_proximity"].unique())) == len(
                schema_json["domain_value"]["ocean_proximity"])
            print(is_categorical_value_equal)

            validation_status = is_size_same and all_column_name_present and is_numeric_column_size and is_categorical_column_size and is_categorical_value_equal
            return validation_status
        except Exception as e:
            raise CustomException(e, sys) from e

    def get_and_save_data_drift_report(self):
        try:
            profile = Profile(sections=[DataDriftProfileSection()])

            train_df, test_df = self.get_train_and_test_df()

            profile.calculate(train_df, test_df)

            report = json.loads(profile.json())

            report_file_path = self.data_validation_config.report_file_path
            report_dir = get_dir(report_file_path)
            make_directories(report_dir)

            with open(report_file_path, "w") as report_file:
                json.dump(report, report_file, indent=6)
            return report
        except Exception as e:
            raise CustomException(e, sys) from e

    def save_data_drift_report_page(self):
        try:
            dashboard = Dashboard(tabs=[DataDriftTab()])
            train_df, test_df = self.get_train_and_test_df()
            dashboard.calculate(train_df, test_df)

            report_page_file_path = self.data_validation_config.report_page_file_path
            report_page_dir = get_dir(report_page_file_path)
            make_directories(report_page_dir)

            dashboard.save(report_page_file_path)
        except Exception as e:
            raise CustomException(e, sys) from e

    def is_data_drift_found(self) -> bool:

        try:
            report = self.get_and_save_data_drift_report()
            schema_file_path = self.data_validation_config.schema_file_path
            schema_json = get_dictionary_from_json(schema_file_path)
            is_data_drift = True
            for feature in schema_json["columns"].keys():
                data_drift_feature = report["data_drift"]["data"]["metrics"][feature]["drift_detected"]
                if not data_drift_feature:
                    print(feature, data_drift_feature)
                else:
                    is_data_drift = False
            self.save_data_drift_report_page()
            return is_data_drift
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:

        try:

            if self.is_train_test_file_exists() and self.validate_dataset_schema() and self.is_data_drift_found():
                data_validation_artifact = DataValidationArtifact(
                    schema_file_path=self.data_validation_config.schema_file_path,
                    report_file_path=self.data_validation_config.report_file_path,
                    report_page_file_path=self.data_validation_config.report_page_file_path,
                    is_validated=True,
                    message="Data Validation performed successfully."
                )
                logging.info(f"Data validation artifact: {data_validation_artifact}")
                return data_validation_artifact
            else:
                message = f"Data Validation Error, something wrong with schema or data drift or file foe not exist " \
                          f"for test and train dataset "
                raise Exception(message)
        except Exception as e:
            raise CustomException(e, sys) from e

    def __del__(self):
        logging.info(f"{'>> ' * 30}Data Validation log completed.{'<< ' * 30} \n\n")
