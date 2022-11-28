# Note
Docs are not complete at the moment.
Things to include:
How build instructions change from one file to another
Configuration options

## Running webserver using docker

In the root of the project run
```shell
docker compose up -d --build
```
and you should have a webserver running on port 80. 
Now visit http://your-ip you should see the web interface

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
uvicorn main:app --reload --port 8000
```

## Adding and building custom versions
To add a new tensorflow build configuration create a Dockerfile named `Dockerfile_tf27(0,1,2,3,4)` in the `tensorflow/` directory.
Where `tf27` stands for the major release and `(0,1,2,3,4)` represents available patch versions. 
Then copy the contents of an existing build configuration and modify accordingly to your needs.
The webserver will scan the directory and in the UI you should see a new build configuration available.

## Building wheels manually
First build bazel image that your version of tensorflow/tfdv depends on, you can figure this out by looking at your
respective Dockerfile or [here](https://www.tensorflow.org/install/source#tested_build_configurations).
```shell
docker build -t bazel:3.7 -f ./bazel/Dockerfile_bazel37 ./bazel/
```

And then build the actual image (tensorflow in this case)
```shell
docker build -t tensorflow_py37:2.7.3 -f ./tensorflow/Dockerfile_tf27 --build-arg PYTHON_VERSION=3.7 --build-arg MINOR_VERSION=3 ./tensorflow/
```

Copy wheels from the resulting image to host machine using:
```shell
docker run -v /host/machine/path:/builds tensorflow_py37:2.7.3 cp -a /wheels/. /builds
```
