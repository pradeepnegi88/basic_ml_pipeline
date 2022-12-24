import logging

from entity.artifact_entity import DataIngestionArtifact
from entity.data_ingestion_entity import DataIngestionEntity
from housing.exception import CustomException
import sys
from housing.utilities.util import make_directories, get_base_file_name, get_file_join, check_dir_remove_make, \
    get_first_filename_from_directory_list
from six.moves import urllib
import tarfile
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionEntity) -> None:
        try:
            logging.info(f"{'>>' * 20} Data Ingestion log started.{'<<' * 20}")
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise CustomException(e, sys) from e

    def download_housing_data(self) -> str:
        try:
            download_url = self.data_ingestion_config.dataset_download_url

            tgz_download_dir = self.data_ingestion_config.tgz_download_dir

            make_directories(tgz_download_dir)
            file_name = get_base_file_name(download_url)
            tgz_file_path = get_file_join(tgz_download_dir, file_name)
            logging.info(f"Downloading file from :[{download_url}] into :[{tgz_file_path}]")
            urllib.request.urlretrieve(download_url, tgz_file_path)
            logging.info(f"File :[{tgz_file_path}] has been downloaded successfully.")
            return tgz_file_path

        except Exception as e:
            raise CustomException(e, sys) from e

    def extract_tgz_file(self, tgz_file_path):
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            check_dir_remove_make(raw_data_dir)
            logging.info(f"Extracting tgz file: [{tgz_file_path}] into dir: [{raw_data_dir}]")
            with tarfile.open(tgz_file_path) as tgz_file_obj:
                tgz_file_obj.extractall(path=raw_data_dir)
            logging.info(f"Extraction completed")

        except Exception as e:
            raise CustomException(e, sys) from e

    def split_data_as_train_test(self) -> DataIngestionArtifact:
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir
            file_name = get_first_filename_from_directory_list(raw_data_dir)
            file_path = get_file_join(raw_data_dir, file_name)
            logging.info(f"Reading csv file: [{file_path}]")
            housing_data_frame = pd.read_csv(file_path)

            housing_data_frame["income_cat"] = pd.cut(
                housing_data_frame["median_income"],
                bins=[0.0, 1.5, 3.0, 4.5, 6.0, np.inf],
                labels=[1, 2, 3, 4, 5]
            )

            logging.info(f"Splitting data into train and test")
            strat_train_set = None
            strat_test_set = None

            split = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

            for train_index, test_index in split.split(housing_data_frame, housing_data_frame["income_cat"]):
                strat_train_set = housing_data_frame.loc[train_index].drop(["income_cat"], axis=1)
                strat_test_set = housing_data_frame.loc[test_index].drop(["income_cat"], axis=1)

            train_file_path = get_file_join(self.data_ingestion_config.ingested_train_dir,
                                            file_name)

            test_file_path = get_file_join(self.data_ingestion_config.ingested_test_dir,
                                           file_name)

            if strat_train_set is not None:
                make_directories(self.data_ingestion_config.ingested_train_dir)
                logging.info(f"Exporting training datset to file: [{train_file_path}]")
                strat_train_set.to_csv(train_file_path, index=False)

            if strat_test_set is not None:
                make_directories(self.data_ingestion_config.ingested_test_dir)
                logging.info(f"Exporting test dataset to file: [{test_file_path}]")
                strat_test_set.to_csv(test_file_path, index=False)

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                                            test_file_path=test_file_path,
                                                            is_ingested=True,
                                                            message=f"Data ingestion completed successfully."
                                                            )
            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            tgz_file_path = self.download_housing_data()
            self.extract_tgz_file(tgz_file_path)
            return self.split_data_as_train_test()
        except Exception as e:
            raise CustomException(e, sys) from e
