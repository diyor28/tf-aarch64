```shell
docker build -t tensorflow:2.7 -f tensorflow/Dockerfile_tf27_py37 .
```

```shell
source venv/bin/active
```

```shell
uvicorn main:app --reload --port 8000
```
