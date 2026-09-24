# Tech Stack Overview

This document provides a technical overview of the frameworks, libraries, and tools used in the MEOW project.

## Core Runtime & Language
- **Python**: Python 3.10+ (Python 3.11 recommended).
- **Asynchronous Framework**: `asyncio`, `anyio`, and `uvloop` for high-throughput asynchronous execution.

## Web & API Layer
- **Starlette**: Asynchronous web framework used to provide HTTP routes, WebSocket endpoints, and Server-Sent Events (SSE).
- **Uvicorn**: ASGI web server running Starlette.
- **WebSockets (`websockets`)**: Real-time communication for task execution, progress streaming, and task management.
- **aiohttp**: Asynchronous HTTP client for interacting with remote services (e.g. Indico, DataCite).

## Task Queue, Worker & Concurrency
- **Async Worker (`worker.py`)**: Background worker service running asynchronous tasks.
- **Redis (`redis-py`)**: In-memory data store used for message passing (Pub/Sub), task streaming, state caching, and credentials lookup.
- **Supervisor (`supervisord`)**: Process management daemon managing `webapp` and `worker` instances in development and production environments.

## Data & Document Processing
- **PDF Manipulation**:
  - `PyMuPDF` (`fitz`) and `PyMuPDFb`: PDF parsing, rendering, text/metadata extraction, and inspection.
  - `pikepdf`: PDF file modification, linearization, encryption/permission handling, and low-level stream access.
  - `pymupdf-fonts`: Bundled typography and fonts for PDF processing.
  - `Pillow`: Image processing and validation embedded in papers/documents.
- **ODF & Office Formats**:
  - `odfpy`: Generating and manipulating OpenDocument format files (ODT) for abstract booklets.
- **XML & HTML Processing**:
  - `lxml`: Fast XML and XSLT transformations for JACoW proceedings formats.
  - `defusedxml`: Secure XML parsing preventing XML vulnerabilities (XXE, entity bombs).
  - `Jinja2`: Templating engine for HTML, XML, and document rendering.
  - `minify_html`: Minification of HTML output for published conference proceedings.
- **Data & Text Tools**:
  - `orjson`: Fast JSON serialization and deserialization.
  - `pyarrow` & `numpy`: Efficient numerical data and tabular structures.
  - `rdflib`: RDF metadata handling and semantic exports.
  - `nltk` & `Unidecode`: Natural language utilities, transliteration, and text normalization.
  - `ulid`: Unique Lexicographically Sortable Identifiers for task and resource tracking.

## Containerization & Deployment
- **Docker**: Containerized deployment based on `python:3.11`.
- **Docker Compose**: Service composition including Redis and MEOW containers.
