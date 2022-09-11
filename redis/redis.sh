#!/bin/bash

# https://hub.docker.com/r/redis/redis-stack
# https://hub.docker.com/r/redis/redis-stack-server

podman stop it.akera.jpsp.redis
podman rm it.akera.jpsp.redis

podman pull redis/redis-stack:latest

podman run -d --name it.akera.jpsp.redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
