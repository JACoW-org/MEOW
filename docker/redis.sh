#!/bin/bash

# https://hub.docker.com/r/redis/redis-stack
# https://hub.docker.com/r/redis/redis-stack-server

# podman volume create jpsp-redis-vol
# podman volume ls

podman stop it.akera.jpsp.redis
podman rm it.akera.jpsp.redis

# podman pull redis/redis-stack:latest

# podman run -d --name it.akera.jpsp.redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

export ARGS="--loglevel notice"  # debug, verbose, notice, warning
export ARGS="$ARGS --save 60 100"  # save
export ARGS="$ARGS --appendonly yes"  # appendonly
export ARGS="$ARGS --appendfsync everysec"  # appendfsync
export ARGS="$ARGS --aof-use-rdb-preamble yes"  # aof-use-rdb-preamble

podman run --name it.akera.jpsp.redis \
	-v jpsp-redis-vol:/data \
    -e REDIS_ARGS="$ARGS" \
    -p 6379:6379 \
    -p 8001:8001 \
    redis/redis-stack:latest 
