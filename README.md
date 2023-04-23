## Installation

```shell
pip install tensorflow==2.8.3 -f https://diyor28.github.io/wheels
```
### Supported versions:
Python: 3.7, 3.8, 3.9, 3.10, 3.11  
Tensorflow: 2.7, 2.8, 2.9, 2.10, 2.11, 2.12
Tensorflow data validation: 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.12, 1.13

NOTE: Other versions can be built and uploaded upon request.

You can also use prebuilt images from [dockerhub](https://hub.docker.com/repository/docker/diyor28/tensorflow)
```dockerfile
FROM diyor28/tensorflow:2.7.3-py37
RUN python -c "import tensorflow; print(tensorflow.__version__)"
```
All the images are based on official [python](https://hub.docker.com/_/python) docker images.

TFDV images are coming soon

## Running webserver using docker
### Make htpasswd for basic auth

```bash
$ mkdir basic_auth
$ htpasswd -c basic_auth/.htpasswd admin
```

### Make directory for workbench

We use `/tmp/tf_aarch64/` for workbench for this build tool.

```bash
$ mkdir /tmp/tf_aarch64
```

### Configuration
If you would like to disable caching or do more than one build at a time
```shell
vim .env
```

```dotenv
# do not set this higher than 2 if you have less then 32GB of RAM. Espeically for building tensorflow
BUILDER_THREADS=1
# disable if you are using buildkit or do not want caching in your builds
USE_CACHE=True
```


Now in the root of the project run:
```shell
docker compose up -d --build
```
Now visit http://localhost you should see the web interface

In the web UI there are two tabs: Tensorflow and TFX. 
Each page has a version dropdown at the bottom of the page for selecting
python version, the library version. 
A version number that looks like `2.7.x` means that it will build the latest changes in the 2.7 branch.

## Development setup

Running python server
```shell
cd back/
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Running ui server
```shell
cd front/
npm i
npm run serve
```

## Adding and building custom versions
Coming soon...

## Building wheels manually

Generate the dockerfile with build instructions (tensorflow in this case)
```shell
python gen.py tensorflow -v 2.7.3 -py 3.7 ./Dockerfile_tf
```

Now build the actual image
```shell
docker build -t tensorflow:2.7.3-py3.7 -f ./Dockerfile_tf ./build_templates/context/
```

Copy wheels from the resulting image to host machine using:
```shell
docker run -v /host/machine/path:/builds tensorflow:2.7.3-py3.7 cp -a /wheels/. /builds
```
