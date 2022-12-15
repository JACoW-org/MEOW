#!/bin/bash

# https://hub.docker.com/r/minio/minio/

# podman volume create jpsp-minio-vol
# podman volume ls

podman stop it.akera.jpsp.minio
podman rm it.akera.jpsp.minio

# podman pull quay.io/minio/minio

# podman run -p 9000:9000 -p 9001:9001 quay.io/minio/minio server /data --console-address ":9001"

export ARGS="--loglevel notice"  # debug, verbose, notice, warning
export ARGS="$ARGS --save 60 100"  # save
export ARGS="$ARGS --appendonly yes"  # appendonly
export ARGS="$ARGS --appendfsync everysec"  # appendfsync
export ARGS="$ARGS --aof-use-rdb-preamble yes"  # aof-use-rdb-preamble

podman run --name it.akera.jpsp.minio \
	-v jpsp-minio-vol:/data \
    -e REDIS_ARGS="$ARGS" \
    -p 9000:9000 \
    -p 9001:9001 \
    quay.io/minio/minio \
    server /data --console-address ":9001"
