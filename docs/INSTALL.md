# Installation & Setup Guide

This guide provides instructions for setting up and running MEOW in a local development environment.

---

## 1. Prerequisites
- **Python**: Python 3.10 or Python 3.11 (Python 3.11 recommended).
- **Redis Server**: Redis 6.0+ or 7.0+ running locally or in Docker.
- **Git**: For version control.

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

# Install dependencies (for development and tests)
pip install -r requirements-dev.txt

# Alternatively, for production runtime dependencies only:
# pip install -r requirements.txt
```

---

## 3. Starting Redis

MEOW relies on Redis for task distribution and state. You can run Redis locally or using the provided helper script:

```bash
# Start Redis in a Docker container for development
./docker/redis.dev.sh
```

Ensure Redis is reachable on `127.0.0.1:6379` (or configure `REDIS_HOST` and `REDIS_PORT` environment variables accordingly).

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

### Option B: Running with Supervisor

You can manage both `webapp` and `worker` processes using Supervisor:

```bash
# Start supervisord in development mode
./venv/bin/supervisord -c conf/supervisord.dev.conf

# Control processes using supervisorctl
./venv/bin/supervisorctl -c conf/supervisord.dev.conf status
./venv/bin/supervisorctl -c conf/supervisord.dev.conf restart all
```

---

## 5. Running Tests

Run the test suite using `pytest`:

```bash
./venv/bin/pytest tests/
```
