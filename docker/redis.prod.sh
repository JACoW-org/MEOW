#!/bin/bash

# https://hub.docker.com/r/redis/redis-stack
# https://hub.docker.com/r/redis/redis-stack-server

# docker volume create cat--meow_redis-vol
# docker volume ls

# docker volume create jpsp-redis-vol
# docker volume ls

docker stop cat--meow_redis
docker rm cat--meow_redis

# docker pull redis/redis-stack:latest

# docker run -d --name it.akera.jpsp.redis -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

export ARGS="--loglevel warning"  # debug, verbose, notice, warning
export ARGS="$ARGS --save 60 100"  # save
export ARGS="$ARGS --appendonly yes"  # appendonly
export ARGS="$ARGS --appendfsync everysec"  # appendfsync
export ARGS="$ARGS --aof-use-rdb-preamble yes"  # aof-use-rdb-preamble


exec docker run --rm \
    --name cat--meow_redis \
    -v jpsp-redis-vol:/data \
    -e REDIS_ARGS="$ARGS" \
    -p 6379:6379 \
    redis/redis-stack-server:latest