# System & Dependency Requirements

This document details the system prerequisites and Python dependencies required to run and develop MEOW.

---

## 1. System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, RHEL/Rocky 8+) or macOS.
- **Python**: Python 3.10 or Python 3.11 (Python 3.11 recommended).
- **Redis**: Redis 6.0+ or Redis 7.0+ (used as message broker and state store).
- **System Libraries**:
  - `libxml2-dev`, `libxslt1-dev` (for `lxml`)
  - `zlib1g-dev`, `libjpeg-dev`, `libfreetype6-dev` (for `pillow` / image processing)
  - Standard C/C++ compiler toolchain (for building C-extensions if wheels are unavailable)

---

## 2. Python Package Requirements

### Core Runtime (`requirements.txt`)
- **Async Web & Networking**:
  - `starlette`: Web framework and routing.
  - `uvicorn`: ASGI server.
  - `websockets`: WebSocket server & client support.
  - `anyio` & `uvloop`: Structured concurrency and fast event loop implementation.
  - `aiohttp`: Asynchronous HTTP client.
  - `redis`: Async Redis client.
- **Document & PDF Processing**:
  - `PyMuPDF` (`fitz`), `PyMuPDFb`, `pymupdf-fonts`: PDF inspection and text/image extraction.
  - `pikepdf`: PDF parsing and modification.
  - `pillow`: Image processing.
  - `odfpy`: OpenDocument (ODT) generation.
- **XML, HTML & Templating**:
  - `lxml`: XML / XSLT transformations.
  - `defusedxml`: Secure XML parsing.
  - `Jinja2`: Templating engine.
  - `minify_html`: HTML minification.
- **Data & Text Serialization**:
  - `orjson`: Fast JSON serialization.
  - `pyarrow` & `numpy`: Tabular and numerical data handling.
  - `rdflib`: RDF metadata manipulation.
  - `nltk` & `Unidecode`: Text normalization.
  - `ulid`: Unique ID generation.
- **Process Management**:
  - `supervisor`: Multi-process management daemon.

### Development & Testing (`requirements-dev.txt`)
- `pytest`: Test runner and testing framework.
- `flake8`: Linting and style enforcement.
- `autopep8`: Automatic code formatting.
- `pylance`: Static analysis support.

---

## 3. External Command-Line Tools & Binaries

MEOW also relies on external tools and bundled binaries located in `bin/` and `lib/` (such as `pdftk`, `qpdf`, `mutool`, `hugo`, `7zzs`, and a Java JRE). For full details and system requirements, see [`docs/EXTERNAL_TOOLS.md`](EXTERNAL_TOOLS.md).
