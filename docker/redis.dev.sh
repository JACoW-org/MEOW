#!/bin/bash

# https://hub.docker.com/r/redis/redis-stack
# https://hub.docker.com/r/redis/redis-stack-server

# podman volume create jpsp-redis-vol
# podman volume ls

podman stop cat--meow_redis
podman rm cat--meow_redis

# podman pull redis/redis-stack:latest

# podman run -d --name cat--meow_redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

export ARGS="--loglevel notice"  # debug, verbose, notice, warning
export ARGS="$ARGS --save 60 100"  # save
export ARGS="$ARGS --appendonly yes"  # appendonly
export ARGS="$ARGS --appendfsync everysec"  # appendfsync
export ARGS="$ARGS --aof-use-rdb-preamble yes"  # aof-use-rdb-preamble

exec podman run --rm \
    --name cat--meow_redis \
    -v jpsp-redis-vol:/data \
    -e REDIS_ARGS="$ARGS" \
    -p 6379:6379 \
    -p 8001:8001 \
    redis/redis-stack:latest 

