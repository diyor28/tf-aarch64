## Running webserver using docker

Run in the root of the project
```shell
docker compose up -d --build
```
and you should have a running webserver on port 80. If you go to your http://your-ip you should see a web interface

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
First build bazel image that your version of tensorflow/tfdv depends on, you can figure this out by looking at your respective Dockerfile
```shell
docker build -t bazel:3.7 -f ./bazel/Dockerfile_bazel37 ./bazel/
```

And then build the actual image (tensorflow in this case)
```shell
docker build -t tensorflow_py37:2.7.3 -f ./tensorflow/Dockerfile_tf27_py37 --build-arg PYTHON_VERSION=3.7 --build-arg MINOR_VERSION=3 ./tensorflow/
```

Copy wheels from the resulting image to host machine using:
```shell
docker run -v /host/machine/path:/builds tensorflow_py37:2.7.3 cp -a /wheels/. /builds
```
