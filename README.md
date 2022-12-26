Application url:
[HousingPredictor](https://ml-regression-app.herokuapp.com/)

## Start Machine Learning project.


Creating conda environment
```
conda create -p venv python==3.7 -y
```
```
conda activate venv/
```
OR 
```
conda activate venv
```

```
pip install -r requirements.txt
```


To setup CI/CD pipeline in heroku we need 3 information
1. HEROKU_EMAIL = abc@gmail.com
2. HEROKU_API_KEY = <>
3. HEROKU_APP_NAME = ml-regression-app

BUILD DOCKER IMAGE
```
docker build -t <image_name>:<tagname> .
```
> Note: Image name for docker must be lowercase


To list docker image
```
docker images
```

Run docker image
```
docker run -p 5000:5000 -e PORT=5000 f8c749e73678
```

To check running container in docker
```
docker ps
```

Tos stop docker conatiner
```
docker stop <container_id>
```



```
python setup.py install
```


Install ipykernel

```
pip install ipykernel
```


Data Drift:
When your datset stats gets change we call it as data drift



