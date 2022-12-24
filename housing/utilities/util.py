from datetime import datetime
import json
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
    os.remove(dir_path)


def check_dir_remove_make(dir_path):
    if check_dir_exists(dir_path):
        remove_dir(dir_path)

    make_directories(dir_path)


def get_first_filename_from_directory_list(dir_path):
    return os.listdir(dir_path)[0]


def get_dir(dir_path):
    return os.path.dirname(dir_path)
