echo "FROM python:3.10" > Dockerfile
echo "RUN pip install tensorflow==2.9.2 -f https://diyor28.github.io/wheels" >> Dockerfile
echo "RUN python -c \"import tensorflow as tf; print(tf.__version__)\"" >> Dockerfile
echo "CMD [\"python\"]" >> Dockerfile
docker build -t diyor28/tensorflow:2.9.2-py310 .

echo "FROM python:3.10" > Dockerfile
echo "RUN pip install tensorflow==2.9.3 -f https://diyor28.github.io/wheels" >> Dockerfile
echo "RUN python -c \"import tensorflow as tf; print(tf.__version__)\"" >> Dockerfile
echo "CMD [\"python\"]" >> Dockerfile
docker build -t diyor28/tensorflow:2.9.3-py310 .

echo "FROM python:3.10" > Dockerfile
echo "RUN pip install tensorflow==2.10.0 -f https://diyor28.github.io/wheels" >> Dockerfile
echo "RUN python -c \"import tensorflow as tf; print(tf.__version__)\"" >> Dockerfile
echo "CMD [\"python\"]" >> Dockerfile
docker build -t diyor28/tensorflow:2.10.0-py310 .

echo "FROM python:3.10" > Dockerfile
echo "RUN pip install tensorflow==2.10.1 -f https://diyor28.github.io/wheels" >> Dockerfile
echo "RUN python -c \"import tensorflow as tf; print(tf.__version__)\"" >> Dockerfile
echo "CMD [\"python\"]" >> Dockerfile
docker build -t diyor28/tensorflow:2.10.1-py310 .
