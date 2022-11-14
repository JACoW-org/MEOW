
docker pull python:3.10


docker build --no-cache -t jpsp-ng-image .
docker build -t jpsp-ng-image .

docker stop jpsp-ng-container
docker rm jpsp-ng-container

docker run \
    --name jpsp-ng-container \
    -p 8000:8000 \
    -p 8443:8443 \
    -e REDIS_HOST=192.168.1.120 \
    -e REDIS_PORT=6379 \
    jpsp-ng-image
