# Note
Docs are not complete at the moment. Things to include:

    How build instructions change from one file to another
    Configuration options

## Installation
```shell
pip install tensorflow==2.8.3 -f https://diyor28.github.io/wheels
```

## Setup

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


## Running webserver using docker

In the root of the project run:
```shell
docker compose up -d --build
```
Now visit http://localhost you should see the web interface

In the web UI there are two tabs: Tensorflow and TFX. 
Each page has a version dropdown at the bottom of the page for selecting
python version, the library version. 
A version number that looks like `2.7.x` means that it will build the latest changes in the 2.7 branch.

## Development
```shell
cd back/
source venv/bin/active
```
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
Coming soon

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

## Supported versions

Python: 3.7, 3.8, 3.9, 3.10, 3.11  
Tensorflow: 2.7, 2.8, 2.9, 2.10  
Tensorflow data validation: 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.12

NOTE: Other versions can be built and uploaded upon request.