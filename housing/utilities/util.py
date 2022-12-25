import shutil
from datetime import datetime
import json

import dill
import numpy as np
import pandas as pd

from housing.exception import CustomException
import sys, os


def get_current_time_stamp():
    return f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"


def get_dictionary_from_json(file_path: str) -> dict:
    try:
        f = open(file_path)
        # returns JSON object as a dictionary
        return json.load(f)
    except Exception as e:
        raise CustomException(e, sys) from e


def get_file_join(*args):
    try:
        return os.path.join(*args)
    except Exception as e:
        raise CustomException(e, sys) from e


def make_directories(dir_name):
    os.makedirs(dir_name, exist_ok=True)


def get_base_file_name(url):
    return os.path.basename(url)


def check_dir_exists(dir_path):
    return os.path.exists(dir_path)


def remove_dir(dir_path):
    pass
    # os.remove(dir_path)


def check_dir_remove_make(dir_path):
    if check_dir_exists(dir_path):
        remove_dir(dir_path)

    make_directories(dir_path)


def get_first_filename_from_directory_list(dir_path):
    return os.listdir(dir_path)[0]


def get_dir(dir_path):
    return os.path.dirname(dir_path)


def load_data(file_path: str, schema_file_path: str) -> pd.DataFrame:
    try:
        datatset_schema = get_dictionary_from_json(schema_file_path)

        schema = datatset_schema["columns"]

        dataframe = pd.read_csv(file_path)

        error_messgae = ""

        for column in dataframe.columns:
            if column in list(schema.keys()):
                dataframe[column].astype(schema[column])
            else:
                error_messgae = f"{error_messgae} \nColumn: [{column}] is not in the schema."
        if len(error_messgae) > 0:
            raise Exception(error_messgae)
        return dataframe

    except Exception as e:
        raise CustomException(e, sys) from e


def get_base_file_replace_filename_with_npz(file_path):
    return get_base_file_name(file_path).replace(".csv", ".npz")


def save_numpy_array_data(file_path: str, array: np.array):
    """
    Save numpy array data to file
    file_path: str location of file to save
    array: np.array data to save
    """
    try:
        dir_path = get_dir(file_path)
        make_directories(dir_path)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise CustomException(e, sys) from e


def save_object(file_path: str, obj):
    """
    file_path: str
    obj: Any sort of object
    """
    try:
        dir_path = get_dir(file_path)
        make_directories(dir_path)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise CustomException(e, sys) from e
