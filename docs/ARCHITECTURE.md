# Architecture

MEOW (Machine Editor for cOnferences Website) is a service designed to automate the processing and publication pipeline of JACoW conference proceedings from Indico data.

---

## 1. High-Level Overview

MEOW consists of two main execution tiers cooperating through Redis:
1. **Web Application (`webapp.py`)**: An asynchronous HTTP, WebSocket, and SSE server built on Starlette and Uvicorn. It handles incoming requests from Indico or frontend clients, authenticates via API keys, schedules tasks, and streams real-time execution progress.
2. **Worker Daemon (`worker.py`)**: A decoupled async worker process running on AnyIO/uvloop. It receives queued/streamed tasks via Redis Pub/Sub, executes computation-heavy tasks (document processing, PDF manipulation, validation, packaging), and reports results and logs back.

```
+-------------------------------------------------------------+
|                      Indico / Clients                       |
+-------------------------------------------------------------+
               | (HTTP REST / WebSocket / SSE)
               v
+-------------------------------------------------------------+
|                     MEOW Web Application                    |
|                         (webapp.py)                         |
|   - API Authentication (API keys)                           |
|   - WebSocket Task Dispatch & Status Streaming              |
|   - Document Preview & REST Endpoints                       |
+-------------------------------------------------------------+
               |                             ^
               | (Pub/Sub & Streams)         | (Status & Results)
               v                             |
+-------------------------------------------------------------+
|                         Redis Store                         |
|   - Task topics & counters (`workers:stream:counter`)       |
|   - Worker registration & Pub/Sub channels                  |
|   - Credential caching                                      |
+-------------------------------------------------------------+
               ^                             |
               | (Subscribe & Execute)       |
               v                             v
+-------------------------------------------------------------+
|                     MEOW Worker Daemon                      |
|                         (worker.py)                         |
|   - Abstract Booklet Generation (ODT / PDF)                 |
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
  - Handles bi-directional task invocation and live streaming of task events.
  - Manages worker load balancing across available worker channels.
  - Supports task cancellation (`task:kill`).
- **Server-Sent Events (`/sse`)**:
  - Unidirectional real-time event streaming for status monitoring.
- **Document Previews (`/` & `/preview`)**:
  - Endpoints to inspect and preview generated artifacts and reports.

---

## 3. Worker & Task Execution (`worker.py`)

- **Concurrency & Lifecycle**:
  - Runs on `anyio` with `uvloop` for high concurrency.
  - Integrates graceful shutdown hooks on `SIGINT` / `SIGTERM`.
  - Dispatches tasks asynchronously while capturing errors and progress logs.
- **Communication Protocol**:
  - Uses structured JSON payloads containing task `head` (UUID, timestamp, action code) and `body` (parameters and payload).

---

## 4. Core Task Services

Located in `meow/services/local/event/`:

### Abstract Booklet (`event_abstract_booklet.py`)
- Collects conference sessions, tracks, and contributions from Indico.
- Generates OpenDocument Text (ODT) and PDF formats using Jinja2 templates and `odfpy`.

### PDF Quality & Compliance Check (`event_pdf_check.py`)
- Analyzes PDF papers submitted to the conference using `PyMuPDF` (`fitz`) and `pikepdf`.
- Validates page geometry, fonts, margins, metadata, and structural conformance to JACoW publication requirements.

### Final Proceedings Generation (`event_proceedings.py`)
- Aggregates processed PDF contributions, session metadata, slides, and extra materials.
- Builds HTML tables of contents, authors indices, session indices, and search metadata.
- Generates publication-ready payloads for INSPIRE HEP, CrossRef, and JACoW formats.
- Compresses proceedings for archive distribution.

### DOI Management (`event_doi_*`)
- Interacts with DataCite / JACoW DOI APIs to draft, update, publish, or hide DOIs for conference contributions and proceedings.

---

## 5. Indico Integration

MEOW integrates with Indico through dedicated plugins:
- **Configuration**: Stores MEOW service endpoint URLs and authentication tokens per conference event.
- **Administrative UI Actions**: Extends Indico event management interfaces with action buttons (e.g. generating abstract booklets, triggering paper checks, initiating proceedings builds).
