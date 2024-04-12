# Installation Guide

## Quick Installation

Install TensorFlow using our custom wheels for optimized performance on various architectures:

```shell
pip install tensorflow==2.8.3 -f https://diyor28.github.io/wheels
```

## Supported Versions

Ensure compatibility with these supported versions before installation:

- **Python:** 3.7, 3.8, 3.9, 3.10, 3.11
- **TensorFlow:** 2.7, 2.8, 2.9, 2.10
- **TensorFlow Data Validation (TFDV):** 1.4 to 1.14

**Note:**
- TensorFlow versions 2.11 and above provide prebuilt wheels for aarch64.
- TFDV 1.14 can be manually built, but a prebuilt wheel is currently not available.
- Custom builds for other versions can be requested.

## Docker Images

Use our prebuilt Docker images available on [Docker Hub](https://hub.docker.com/r/diyor28/tensorflow):

```dockerfile
FROM diyor28/tensorflow:2.7.3-py37
RUN python -c "import tensorflow; print(tensorflow.__version__)"
```

All images are based on the official [Python Docker images](https://hub.docker.com/_/python).

TFDV Docker images will be available soon.

## Web Server Setup with Docker

### Basic Authentication

Create a directory and password for basic authentication:

```bash
mkdir basic_auth
htpasswd -c basic_auth/.htpasswd admin
```

### Workbench Directory

Set up a directory to serve as a workbench:

```bash
mkdir /tmp/tf_aarch64
```

### Configuration

Configure environment settings such as build concurrency and caching:

1. Edit the environment settings:

   ```shell
   vim .env
   ```

2. Update or add the following configurations:

   ```dotenv
   BUILDER_THREADS=1  # Max of 2 for systems with <32GB RAM
   USE_CACHE=True     # Disable if using BuildKit or if caching is not desired
   ```

3. Start the Docker container:

   ```shell
   docker compose up -d --build
   ```

Visit `http://localhost` to access the web interface, which includes version selection tools for TensorFlow and TFX.

## Development Setup

### Python Backend Server

```shell
cd back/
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### UI Server

```shell
cd front/
npm install
npm run serve
```

## Manual Wheel Building

### Generate Dockerfile

Create a Dockerfile for building a specific TensorFlow version:

```shell
python gen.py tensorflow -v 2.7.3 -py 3.7 ./Dockerfile_tf
```

### Build Docker Image

Build the Docker image based on the generated Dockerfile:

```shell
docker build -t tensorflow:2.7.3-py3.7 -f ./Dockerfile_tf ./build_templates/context/
```

### Extract Wheels

Copy the built TensorFlow wheels from the Docker container to your host machine:

```shell
docker run -v /host/machine/path:/builds tensorflow:2.7.3-py3.7 cp -a /wheels/. /builds
```

## Future Updates

Details on adding and building custom versions will be provided soon.
