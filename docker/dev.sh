#!/bin/bash

docker build -t it.akera.jpsp.image . 

docker stop it.akera.jpsp.node 
docker rm it.akera.jpsp.node ; 

docker run --name it.akera.jpsp.node \
    -e REDIS_HOST=192.168.1.120 \
    -e REDIS_PORT=6379 \
    -p 8080:8080 \
    -p 8443:8443 \
    it.akera.jpsp.image

