import json

from flask import Flask, request
from flask import send_file, abort, render_template

from constant import CONFIG_DIR
from entity.housing_predictor import HousingData, HousingPredictor
from housing.logger import logging
from housing.pipeline.pipeline import Pipeline
from housing.utilities.util import get_current_time_stamp, write_yaml_file, read_yaml_file, get_file_join, \
    make_directories, current_working_directory, check_dir_exists, get_dir, get_is_file, \
    get_filename_from_directory_list

ROOT_DIR = current_working_directory()
LOG_FOLDER_NAME = "logs"
PIPELINE_FOLDER_NAME = "housing"
SAVED_MODELS_DIR_NAME = "saved_models"
MODEL_CONFIG_FILE_PATH = get_file_join(ROOT_DIR, CONFIG_DIR, "model.yaml")
LOG_DIR = get_file_join(ROOT_DIR, LOG_FOLDER_NAME)
PIPELINE_DIR = get_file_join(ROOT_DIR, PIPELINE_FOLDER_NAME)
MODEL_DIR = get_file_join(ROOT_DIR, SAVED_MODELS_DIR_NAME)
from housing.config.configuration import Configuration

from housing.logger import get_log_dataframe

HOUSING_DATA_KEY = "housing_data"
MEDIAN_HOUSING_VALUE_KEY = "median_house_value"

app = Flask(__name__)


@app.route('/artifact', defaults={'req_path': 'housing'})
@app.route('/artifact/<path:req_path>')
def render_artifact_dir(req_path):
    make_directories("housing")
    # Joining the base and the requested path
    print(f"req_path: {req_path}")
    abs_path = get_file_join(req_path)
    print(abs_path)
    # Return 404 if path doesn't exist
    if not check_dir_exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if get_is_file(abs_path):
        if ".html" in abs_path:
            with open(abs_path, "r", encoding="utf-8") as file:
                content = ''
                for line in file.readlines():
                    content = f"{content}{line}"
                return content
        return send_file(abs_path)

    # Show directory contents
    files = {get_file_join(abs_path, file_name): file_name for file_name in get_filename_from_directory_list(abs_path)
             if
             "artifact" in get_file_join(abs_path, file_name)}

    result = {
        "files": files,
        "parent_folder": get_dir(abs_path),
        "parent_label": abs_path
    }
    return render_template('files.html', result=result)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e)


@app.route('/view_experiment_hist', methods=['GET', 'POST'])
def view_experiment_history():
    experiment_df = Pipeline.get_experiments_status()
    context = {
        "experiment": experiment_df.to_html(classes='table table-striped col-12')
    }
    return render_template('experiment_history.html', context=context)


@app.route('/train', methods=['GET', 'POST'])
def train():
    message = ""
    pipeline = Pipeline(config=Configuration(current_time_stamp=get_current_time_stamp()))
    if not Pipeline.experiment.running_status:
        message = "Training started."
        pipeline.start()
    else:
        message = "Training is already in progress."
    context = {
        "experiment": pipeline.get_experiments_status().to_html(classes='table table-striped col-12'),
        "message": message
    }
    return render_template('train.html', context=context)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    context = {
        HOUSING_DATA_KEY: None,
        MEDIAN_HOUSING_VALUE_KEY: None
    }

    if request.method == 'POST':
        longitude = float(request.form['longitude'])
        latitude = float(request.form['latitude'])
        housing_median_age = float(request.form['housing_median_age'])
        total_rooms = float(request.form['total_rooms'])
        total_bedrooms = float(request.form['total_bedrooms'])
        population = float(request.form['population'])
        households = float(request.form['households'])
        median_income = float(request.form['median_income'])
        ocean_proximity = request.form['ocean_proximity']

        housing_data = HousingData(longitude=longitude,
                                   latitude=latitude,
                                   housing_median_age=housing_median_age,
                                   total_rooms=total_rooms,
                                   total_bedrooms=total_bedrooms,
                                   population=population,
                                   households=households,
                                   median_income=median_income,
                                   ocean_proximity=ocean_proximity,
                                   )
        housing_df = housing_data.get_housing_input_data_frame()
        housing_predictor = HousingPredictor(model_dir=MODEL_DIR)
        median_housing_value = housing_predictor.predict(X=housing_df)
        context = {
            HOUSING_DATA_KEY: housing_data.get_housing_data_as_dict(),
            MEDIAN_HOUSING_VALUE_KEY: median_housing_value,
        }
        return render_template('predict.html', context=context)
    return render_template("predict.html", context=context)


@app.route('/saved_models', defaults={'req_path': 'saved_models'})
@app.route('/saved_models/<path:req_path>')
def saved_models_dir(req_path):
    make_directories("saved_models")
    # Joining the base and the requested path
    print(f"req_path: {req_path}")
    abs_path = get_file_join(req_path)
    print(abs_path)
    # Return 404 if path doesn't exist
    if not check_dir_exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if get_is_file(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = {get_file_join(abs_path, file): file for file in get_filename_from_directory_list(abs_path)}

    result = {
        "files": files,
        "parent_folder": get_dir(abs_path),
        "parent_label": abs_path
    }
    return render_template('saved_models_files.html', result=result)


@app.route("/update_model_config", methods=['GET', 'POST'])
def update_model_config():
    try:
        if request.method == 'POST':
            model_config = request.form['new_model_config']
            model_config = model_config.replace("'", '"')
            print(model_config)
            model_config = json.loads(model_config)

            write_yaml_file(file_path=MODEL_CONFIG_FILE_PATH, data=model_config)

        model_config = read_yaml_file(file_path=MODEL_CONFIG_FILE_PATH)
        return render_template('update_model.html', result={"model_config": model_config})

    except  Exception as e:
        logging.exception(e)
        return str(e)


@app.route(f'/logs', defaults={'req_path': f'{LOG_FOLDER_NAME}'})
@app.route(f'/{LOG_FOLDER_NAME}/<path:req_path>')
def render_log_dir(req_path):
    make_directories(LOG_FOLDER_NAME)
    # Joining the base and the requested path
    logging.info(f"req_path: {req_path}")
    abs_path = get_file_join(req_path)
    print(abs_path)
    # Return 404 if path doesn't exist
    if not check_dir_exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if get_is_file(abs_path):
        log_df = get_log_dataframe(abs_path)
        context = {"log": log_df.to_html(classes="table-striped", index=False)}
        return render_template('log.html', context=context)

    # Show directory contents
    files = {get_file_join(abs_path, file): file for file in get_filename_from_directory_list(abs_path)}

    result = {
        "files": files,
        "parent_folder": get_dir(abs_path),
        "parent_label": abs_path
    }
    return render_template('log_files.html', result=result)


if __name__ == "__main__":
    app.run()
