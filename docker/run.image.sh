#!/bin/bash

docker build -t cat--meow_image . 

docker stop cat--meow
docker rm cat--meow

docker run --name cat--meow \
    -e REDIS_HOST=192.168.1.120 \
    -e REDIS_PORT=6379 \
    -p 8080:8080 \
    -p 8443:8443 \
    cat--meow_image

