from datetime import datetime
import json
from housing.exception import CustomException
import sys,os


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
        raise CustomException(e,sys) from e
