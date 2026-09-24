# Docker & Containerization Guide

This document describes how to build, configure, and run MEOW using Docker containers.

---

## 1. Container Overview

- **Base Image**: `python:3.11`
- **Image Name**: `cat--meow_image`
- **Container Name**: `cat--meow`
- **Default Exposed Ports**:
  - `8080`: HTTP, WebSocket, and SSE endpoints.
  - `8443`: HTTPS / Secure WebSocket endpoint.

---

## 2. Docker Helper Scripts

The `docker/` directory provides pre-configured shell scripts for common operations:

| Script | Description |
|---|---|
| `docker/build.image.sh` | Pulls `python:3.11` and builds `cat--meow_image` without cache. |
| `docker/run.image.sh` | Builds and runs the `cat--meow` container connected to Redis. |
| `docker/redis.dev.sh` | Launches a Redis container for development environments. |
| `docker/redis.test.sh` | Launches a Redis container for test environments. |
| `docker/redis.prod.sh` | Launches a Redis container for production environments. |

---

## 3. Environment Variables

| Variable | Default / Example | Description |
|---|---|---|
| `REDIS_HOST` | `127.0.0.1` or `192.168.1.120` | Hostname or IP of the Redis server. |
| `REDIS_PORT` | `6379` | Port number of the Redis server. |
| `CLIENT_TYPE` | `webapp` or `worker` | Set automatically by entrypoint modules. |

---

## 4. Manual Docker Commands

### Build Image
```bash
docker pull python:3.11
docker build -t cat--meow_image .
```

### Run Container
```bash
docker run -d \
    --name cat--meow \
    -p 8080:8080 \
    -p 8443:8443 \
    -e REDIS_HOST=127.0.0.1 \
    -e REDIS_PORT=6379 \
    cat--meow_image
```

### Stop & Remove Container
```bash
docker stop cat--meow
docker rm cat--meow
```
