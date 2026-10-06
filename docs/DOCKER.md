# Docker & Containerization Guide

This document describes what is (and is not) available in this repository for running MEOW and its Redis dependency with Docker.

> **Status:** the repository does **not** currently contain a maintained `Dockerfile` or a Docker Compose file. The `Dockerfile` was removed in commit `5f65d36` (2023-10-02, "refactoring"). The MEOW image scripts in `docker/` are therefore **legacy** and do not work as-is. Only the Redis helper scripts are usable today.

---

## 1. Redis helper scripts (usable)

MEOW needs a Redis server (see [`INSTALL.md`](INSTALL.md)). The `docker/` directory provides three scripts that run Redis in the foreground (`exec docker run --rm`), so the terminal is blocked until the container is stopped:

| Script | Image | Ports | Volume | Notes |
|---|---|---|---|---|
| `docker/redis.dev.sh` | `redis/redis-stack:latest` | `6379`, `8001` (Redis Stack UI) | `jpsp-redis-vol` | Log level `notice`. |
| `docker/redis.test.sh` | `redis:alpine` | `6379`, `8001` | `redis-test-vol` | Log level `notice`. |
| `docker/redis.prod.sh` | `redis/redis-stack-server:latest` | `6379` | `jpsp-redis-vol` | Log level `warning`. |

All three stop and remove any existing container named `cat--meow_redis` first, and enable persistence with `--save 60 100`, `--appendonly yes`, `--appendfsync everysec` and `--aof-use-rdb-preamble yes`. The dev and prod scripts share the same volume (`jpsp-redis-vol`).

---

## 2. MEOW image scripts (legacy, not working)

| Script | What it does | Why it does not work |
|---|---|---|
| `docker/build.image.sh` | `docker pull python:3.11`, then `docker build --no-cache -t cat--meow_image .` | There is no `Dockerfile` in the repository root. |
| `docker/run.image.sh` | Builds `cat--meow_image`, then runs the `cat--meow` container with `-p 8080:8080 -p 8443:8443` and a hardcoded `REDIS_HOST` (a private LAN address). | Same as above. In addition, `8443` is only a port mapping: the application does not serve TLS (uvicorn is started without certificates), so there is no HTTPS endpoint. |

If you need a container image, a new `Dockerfile` has to be written first. It would have to start `webapp.py` and `worker.py` (see [`INSTALL.md`](INSTALL.md)) and provide the external tools listed in [`EXTERNAL_TOOLS.md`](EXTERNAL_TOOLS.md), including a Java runtime.

---

## 3. Environment Variables

Defined in `meow/app/config.py`:

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `127.0.0.1` | Hostname or IP of the Redis server. |
| `REDIS_PORT` | `6379` | Port of the Redis server. |
| `CLIENT_TYPE` | none | Set by `webapp.py` and `worker.py` themselves (`webapp` / `worker`); do not set it manually. |
| `SERVER_PORT` | `8080` | Defined in the configuration but effectively unused: the port is passed to `uvicorn` on the command line. |
| `LOG_LEVEL` | `info` | Defined in the configuration but effectively unused: the code that applied it is commented out in `meow/app/factory.py`. |
