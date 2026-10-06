# System & Dependency Requirements

This document details the system prerequisites and Python dependencies required to run and develop MEOW.

---

## 1. System Requirements

- **Operating System**: Linux x86_64. The bundled binaries in `bin/` and `lib/` are x86_64 ELF executables, so macOS and other architectures are not supported by the bundled tools.
- **Python**: 3.12 (see [`INSTALL.md`](INSTALL.md) for what has and has not been verified).
- **Redis**: a reachable Redis server, used as message broker (Pub/Sub) and store for API keys. The helper scripts use `redis/redis-stack` and `redis:alpine` images; no minimum Redis version has been verified.
- **Java runtime**: required by `bin/pdftk.sh`.
- **Binaries in `bin/`**: `hugo`, `7zzs` and `pdftk.sh` are used by the active code path (see [`EXTERNAL_TOOLS.md`](EXTERNAL_TOOLS.md)).
- **System libraries**: none are documented as required. The pinned Python packages provide binary wheels for Linux x86_64 on Python 3.12; a C/C++ toolchain and `-dev` libraries are only needed if you build from source.

---

## 2. Python Package Requirements

The authoritative list is `requirements.txt` (pinned versions). The groups below describe the packages that MEOW imports directly.

### Core Runtime (`requirements.txt`)
- **Async Web & Networking**:
  - `starlette`: Web framework and routing (HTTP and WebSocket; no FastAPI).
  - `uvicorn`: ASGI server (`websockets` is its WebSocket implementation).
  - `anyio` & `uvloop`: Structured concurrency and fast event loop implementation.
  - `aiohttp`: Asynchronous HTTP client.
  - `redis`: Async Redis client.
- **Document & PDF Processing**:
  - `PyMuPDF` (`fitz`), `PyMuPDFb`, `pymupdf-fonts`: PDF inspection, text/image extraction and stamping.
  - `pikepdf`: PDF parsing and modification.
  - `pillow`: Image processing.
  - `odfpy`: OpenDocument (ODT) generation.
- **XML, HTML & Templating**:
  - `lxml`: XML / XSLT transformations.
  - `Jinja2`: Templating engine.
  - `minify_html`: HTML minification.
- **Data & Text Serialization**:
  - `orjson`: Fast JSON serialization.
  - `rdflib`: RDF metadata manipulation.
  - `nltk` & `Unidecode`: Text normalization.
  - `ulid`: Unique ID generation.
  - `pytz`: Time zone conversion.
- **Process Management**:
  - `supervisor`: Multi-process management daemon.

Other packages in `requirements.txt` (for example `pyarrow`, `numpy`, `defusedxml`, `pylance`) are not imported by MEOW's code; they are pinned as dependencies of other packages or for historical reasons. `pylance` is the Lance data-format library, **not** the Microsoft language server.

### Development & Testing
- `flake8` and `autopep8` are listed in `requirements.txt` as well.
- `pytest` is only listed in `requirements-dev.txt`, which is an older freeze of `requirements.txt`. Install `pytest` separately (see [`INSTALL.md`](INSTALL.md)).

---

## 3. External Command-Line Tools & Binaries

See [`docs/EXTERNAL_TOOLS.md`](EXTERNAL_TOOLS.md) for the tools executed by the code (`pdftk` + Java, `hugo`, `7zzs`), the optional ones (`qpdf`, `mutool`, `pdfunite` from the `PATH`) and the files in `bin/` that nothing references.
