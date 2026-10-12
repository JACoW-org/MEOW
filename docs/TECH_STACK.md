# Tech Stack Overview

This document provides a technical overview of the frameworks, libraries, and tools used in the MEOW project. Package versions are pinned in `requirements.txt`.

## Core Runtime & Language
- **Python**: 3.12 (see [`INSTALL.md`](INSTALL.md)).
- **Asynchronous Framework**: `asyncio`, `anyio`, and `uvloop` for high-throughput asynchronous execution.

## Web & API Layer
- **Starlette**: Asynchronous web framework used to provide HTTP routes and WebSocket endpoints. A Server-Sent Events route exists but is a stub (see [`ARCHITECTURE.md`](ARCHITECTURE.md)).
- **Uvicorn**: ASGI web server running Starlette (`websockets` is its WebSocket implementation).
- **aiohttp**: Asynchronous HTTP client for interacting with remote services (e.g. Indico, DataCite).

## Task Queue, Worker & Concurrency
- **Async Worker (`worker.py`)**: Background worker service running asynchronous tasks.
- **Redis (`redis-py`)**: used for message passing (Pub/Sub) and as the store of API key credentials.
- **Supervisor (`supervisord`)**: Process management daemon. The configurations in `conf/` also manage other processes and are specific to the original deployment (see [`INSTALL.md`](INSTALL.md)).

## Data & Document Processing
- **PDF Manipulation**:
  - `PyMuPDF` (`fitz`) and `PyMuPDFb`: PDF parsing, rendering, text/metadata extraction, and inspection.
  - `pikepdf`: PDF file modification and low-level stream access.
  - `pymupdf-fonts`: Bundled typography and fonts for PDF processing.
  - `Pillow`: Image processing and validation embedded in papers/documents.
  - PDFtk (`bin/pdftk.sh`, requires Java): concatenation of PDFs for the `brief` and `volume` files.
- **ODF & Office Formats**:
  - `odfpy`: Generating OpenDocument format files (ODT) for abstract booklets.
- **XML & HTML Processing**:
  - `lxml`: XML and XSLT transformations for the BibTeX, LaTeX, RIS, EndNote and Word references.
  - `Jinja2`: Templating engine for the proceedings website content.
  - Hugo (`bin/hugo`): static site generator for the final proceedings website.
  - `minify_html`: Minification of HTML output for published conference proceedings.
- **Data & Text Tools**:
  - `orjson`: Fast JSON serialization and deserialization.
  - `rdflib`: RDF metadata handling.
  - `nltk` & `Unidecode`: Natural language utilities, transliteration, and text normalization.
  - `ulid`: Unique Lexicographically Sortable Identifiers for task and resource tracking.
  - `pytz`: Time zone conversion.
- **Archiving**: 7-Zip (`bin/7zzs`) for the `.7z` proceedings archive.

## Containerization & Deployment
- There is currently no maintained `Dockerfile` or Docker Compose file in this repository. Only Redis helper scripts are usable; see [`DOCKER.md`](DOCKER.md).
