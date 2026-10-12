# Installation & Setup Guide

This guide provides instructions for setting up and running MEOW in a local development environment.

---

## 1. Prerequisites
- **Linux x86_64**: the bundled binaries in `bin/` and `lib/` are x86_64 ELF executables.
- **Python 3.12**: the version used for the maintainers' virtual environment; the pinned `requirements.txt` was installed and the test suite run on 3.12 while reviewing this document. Python 3.11 is the version the legacy Docker scripts target. Other versions, in particular 3.13 or newer, have not been verified (the pinned `numpy`, `PyMuPDF` and `pyarrow` versions may not provide wheels for them).
- **Redis server**: running locally or in Docker (see section 3).
- **Java runtime** (`java` in the `PATH`): required by `bin/pdftk.sh` to build the proceedings PDFs. See [`EXTERNAL_TOOLS.md`](EXTERNAL_TOOLS.md).
- **Git**.

---

## 2. Virtual Environment Setup

Clone the repository and initialize the Python virtual environment:

```bash
# Navigate to the project root
cd /path/to/meow

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source ./venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install the runtime dependencies
pip install -r requirements.txt

# Install the test runner (for development)
pip install pytest
```

> **Do not install `requirements-dev.txt` on its own.** It is an older freeze (February 2024) than `requirements.txt` and pins outdated versions (for example `aiohttp 3.9.3` instead of `3.10.11`, `starlette 0.37.1` instead of `0.40.0`). If you do use it, install `requirements.txt` afterwards so that the current pins win.

All commands below must be run from the **project root**: the code uses relative paths such as `bin/`, `lib/`, `jinja/`, `xslt/`, `assets/` and `var/`.

---

## 3. Starting Redis

MEOW relies on Redis for task distribution and credentials. You can run Redis locally or use one of the helper scripts:

```bash
# Start Redis in a Docker container for development (runs in the foreground, press Ctrl+C to stop)
./docker/redis.dev.sh
```

Ensure Redis is reachable on `127.0.0.1:6379` (or set `REDIS_HOST` and `REDIS_PORT`). See [`DOCKER.md`](DOCKER.md) for the details of the three Redis scripts.

---

## 4. Running the Application

### Option A: Running Services Manually

1. **Start the Web Application (Starlette + Uvicorn)**:
   ```bash
   ./venv/bin/uvicorn webapp:app --host 0.0.0.0 --port 8080 --reload
   ```

2. **Start the Async Worker**:
   ```bash
   ./venv/bin/python3 worker.py
   ```

### Option B: Running with Supervisor (production-style deployments only)

The files in `conf/` (`supervisord.dev.conf`, `supervisord.prod.conf`, `supervisord.conf`) were written for the original deployment. They contain **absolute paths** (`/pj/elettra/...`), start additional processes (for example `maildump`) and log into `var/log`, `var/pid` and `var/tmp`, which are not part of a fresh checkout. They must be adapted (and those directories created) before use, and they contain a hardcoded credential that must be replaced. For local development use Option A.

---

## 5. Creating an API Key

Every call to the API and the WebSocket needs an API key stored in Redis (`meow:credential:*`). With Redis running, from the project root:

```bash
./venv/bin/python3 -m meow auth -login <user>@<host>   # create a key, prints it
./venv/bin/python3 -m meow auth -list                  # list existing keys
./venv/bin/python3 -m meow auth -logout <key>          # delete a key
```

---

## 6. Running Tests

```bash
./venv/bin/pytest tests/
```
