
docker pull python:3.10


docker build --no-cache -t meow-image .
docker build -t meow-image .

docker stop meow-container
docker rm meow-container

docker run \
    --name meow-container \
    -p 8000:8000 \
    -p 8443:8443 \
    -e REDIS_HOST=192.168.1.120 \
    -e REDIS_PORT=6379 \
    meow-image
