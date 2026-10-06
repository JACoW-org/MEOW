# Architecture

MEOW (Machine Editor for cOnferences Website) is a service designed to automate the processing and publication pipeline of JACoW conference proceedings from Indico data.

---

## 1. High-Level Overview

MEOW consists of two main execution tiers cooperating through Redis:
1. **Web Application (`webapp.py`)**: An asynchronous HTTP and WebSocket server built on Starlette and Uvicorn. It handles incoming requests from Indico or frontend clients, authenticates via API keys, dispatches tasks to workers, and streams execution progress over WebSocket.
2. **Worker Daemon (`worker.py`)**: A decoupled async worker process running on AnyIO/uvloop. It receives tasks via Redis Pub/Sub, executes computation-heavy tasks (document processing, PDF manipulation, validation, packaging), and reports results and logs back.

```
+-------------------------------------------------------------+
|                      Indico / Clients                       |
+-------------------------------------------------------------+
               | (HTTP REST / WebSocket)
               v
+-------------------------------------------------------------+
|                     MEOW Web Application                    |
|                         (webapp.py)                         |
|   - API Authentication (API keys)                           |
|   - WebSocket Task Dispatch & Status Streaming              |
|   - Static file serving (`var/html`) & REST Endpoints       |
+-------------------------------------------------------------+
               |                             ^
               | (Pub/Sub)                   | (Status & Results)
               v                             |
+-------------------------------------------------------------+
|                         Redis Store                         |
|   - Task topics & counters (`workers:stream:counter`)       |
|   - Worker registration & Pub/Sub channels                  |
|   - API key credentials (`meow:credential:*` hashes)        |
+-------------------------------------------------------------+
               ^                             |
               | (Subscribe & Execute)       |
               v                             v
+-------------------------------------------------------------+
|                     MEOW Worker Daemon                      |
|                         (worker.py)                         |
|   - Abstract Booklet Generation (ODT)                       |
|   - PDF Checking & Compliance Validation                    |
|   - Final Proceedings Generation & Packaging                |
|   - DOI Metadata Registration (DataCite)                    |
+-------------------------------------------------------------+
```

---

## 2. Web Application (`webapp.py`)

The web application exposes several endpoint groups:
- **REST API (`/api`)**:
  - `/api/ping`: Service health check and authentication test.
  - `/api/df`: Disk usage metrics for storage volumes.
  - `/api/info/{event_id}`: Information and metadata about an event.
  - `/api/clear/{event_id}`: Cache and temporary file cleanup for an event.
  - `/api/refs/{event_id}`: References and citations processing.
- **WebSocket Gateway (`/socket`)**:
  - Route: `/socket/{api_key}/{task_id}`. Handles bi-directional task invocation and live streaming of task events.
  - Distributes tasks across the available workers' Pub/Sub channels (round-robin, using the `workers:stream:counter` Redis counter).
  - Supports task cancellation (`task:kill`, forwarded to the worker's Pub/Sub topic).
- **Server-Sent Events (`POST /sse/{key}`)**: currently a stub. The endpoint only returns a single placeholder message; it does not stream task progress (that is done over the WebSocket above).
- **Static files (`/`)**: the `var/html` directory (generated artifacts and reports) is served as static files mounted at the root path.

---

---

## 3. Worker & Task Execution (`worker.py`)

- **Concurrency & Lifecycle**:
  - Runs on `anyio` with `uvloop` for high concurrency.
  - Integrates graceful shutdown hooks on `SIGINT` / `SIGTERM`.
  - Dispatches tasks asynchronously while capturing errors and progress logs.
  - Uses Redis Pub/Sub only. A Redis Streams based consumer exists in `meow/app/workers/stream.py` but is not wired in (`meow/app/instances/services.py` uses `PubsubRedisWorkerLogicComponent`).
- **Communication Protocol**:
  - Uses structured JSON payloads containing task `head` (UUID, timestamp, action code) and `body` (parameters and payload).

---

## 4. Core Task Services

Located in `meow/services/local/event/`:

### Abstract Booklet (`event_abstract_booklet.py`)
- Collects conference sessions, tracks, and contributions from Indico.
- Exports the booklet as an OpenDocument Text (ODT) file built with `odfpy` (`export_abstract_booklet_to_odt`). No PDF is produced by this task.

### PDF Quality & Compliance Check (`event_pdf_check.py`)
- Analyzes PDF papers submitted to the conference using `PyMuPDF` (`fitz`) and `pikepdf`.
- Validates page geometry, fonts, margins, metadata, and structural conformance to JACoW publication requirements.

### Final Proceedings Generation (`event_proceedings.py`)
- Aggregates processed PDF contributions, session metadata, slides, and extra materials.
- Builds HTML tables of contents, authors indices, session indices, and search metadata.
- Generates the INSPIRE HEP and DOI payloads (`build_hep_payloads`, `build_doi_payloads`) and the BibTeX, LaTeX, RIS, EndNote and Word references (XSLT in `xslt/`).
- Renders the proceedings website with Jinja2 templates and Hugo (see [`EXTERNAL_TOOLS.md`](EXTERNAL_TOOLS.md)).
- Compresses proceedings for archive distribution.

### Registered tasks
The tasks the worker can run are registered in `meow/tasks/infra/task_repository.py`: `event_abstract_booklet`, `event_papers_check`, `event_pre_press`, `event_final_proceedings`, `event_compress_proceedings`, `event_doi_draft`, `event_doi_delete`, `event_doi_publish`, `event_doi_hide`, `event_doi_info` and `event_doi_login`.

### DOI Management (`event_doi_*`)
- Interacts with DataCite / JACoW DOI APIs to draft, update, publish, or hide DOIs for conference contributions and proceedings.

---

## 5. Indico Integration

MEOW integrates with Indico through a plugin (PURR) that lives in a separate repository and is not documented or verified here. It is described as follows:
- **Configuration**: Stores MEOW service endpoint URLs and authentication tokens per conference event.
- **Administrative UI Actions**: Extends Indico event management interfaces with action buttons (e.g. generating abstract booklets, triggering paper checks, initiating proceedings builds).
