# [Proposal] Infrastructure Evolution: Systemd Lifecycle, Cgroups v2 Monitoring, Valkey Migration, & Dashboards

> **Status:** Proposal / Draft  
> **Related Issues:** [#19 (Structured Logs & Systemd Service Adoption)](https://github.com/JACoW-org/MEOW/issues/19), [#22 (Resource Monitoring via Cgroups v2 VFS & Multi-Replica Management)](https://github.com/JACoW-org/MEOW/issues/22), [#23 (Application-Level State Backup, Valkey Migration Pipeline & S3 Export)](https://github.com/JACoW-org/MEOW/issues/23)

---

## 1. Executive Summary

This proposal outlines the architectural evolution of MEOW's execution and operations layer. Transitioning from standalone process scripts / Supervisor to a native **Systemd**, **Linux Cgroups v2**, **AnyIO**, **Zstandard**, and **S3** architecture maximizes operational reliability, horizontal scalability, zero-overhead telemetry, and engine-agnostic data protection.

### Core Objectives
1. **Zero-Overhead Subprocess Telemetry:** Direct non-blocking kernel reads via Cgroups v2 Virtual File System (`/sys/fs/cgroup`) to accurately track CPU, RAM (current and peak), and process counts across arbitrary worker subprocess trees (LaTeX, Ghostscript, PyMuPDF, etc.).
2. **Deterministic Multi-Instance Scaling & Failure Isolation:** Native Systemd template units (`meow-worker@.service`, `meow-webapp@.service`) grouped under resource slices (`meow-worker.slice`) and managed atomically via `meow.target`.
3. **Engine-Agnostic Logical Backup & Valkey Migration:** Automated non-blocking JSON/NDJSON state extraction with `tar.zst` compression and Boto3 S3 upload, facilitating seamless migration from Redis to Valkey without binary RDB incompatibilities.
4. **Structured Logging & Centralization:** Standardized JSON stdout logging ingested directly by `systemd-journald`.
5. **Unified Multi-Dashboard Ecosystem:** Real-time metrics streaming to conference editorial tools, operations telemetry dashboards, and backup management consoles.

---

## 2. High-Level Architecture Overview

```
+---------------------------------------------------------------------------------------------------+
|                                       DASHBOARDS & CLIENTS                                        |
+---------------------------------------------------------------------------------------------------+
|  1. PURR / Indico Conference UI   |  2. System & Telemetry Dashboard  |  3. Backup & Ops Console  |
|  - Task Progress (SSE / WS)       |  - CPU / RAM / PID per replica    |  - S3 Snapshot History    |
|  - PDF Quality / Booklet Status   |  - Cgroups v2 Real-time Charts    |  - Timer status & Journal |
+---------------------------------------------------------------------------------------------------+
                               |                              |                             |
                       (REST / WS / SSE)              (REST / SSE)                (Admin REST / S3)
                               |                              |                             |
                               v                              v                             v
+---------------------------------------------------------------------------------------------------+
|                                     MEOW WEBAPP POOL (Systemd)                                    |
|                                    `meow-webapp@<port>.service`                                   |
|  - FastAPI / Starlette Async Engine (Uvicorn / AnyIO)                                             |
|  - Token Authentication & Event Dispatch                                                          |
|  - Metrics Aggregator (`GET /api/system/metrics` & `GET /sse/system`)                             |
+---------------------------------------------------------------------------------------------------+
             |                                                                       ^
      (Task Dispatch)                                                         (VFS Direct Read)
             |                                                                       |
             v                                                                       |
+-----------------------------------------+                 +----------------------------------------+
|          REDIS / VALKEY STORE           |                 |          KERNEL CGROUP V2 VFS          |
|  - Task Queues / PubSub Streams         |                 |  `/sys/fs/cgroup/system.slice/`        |
|  - Ephemeral Status & Channel Mapping   |                 |  - `meow-worker@*.service/cpu.stat`    |
|  - API Keys & Config State              |                 |  - `meow-worker@*.service/memory.*`    |
+-----------------------------------------+                 |  - `meow-worker@*.service/pids.current`|
     |                     ^                                +----------------------------------------+
     |                     | (Logical State Extractor)                           ^
     | (Consume & Exec)    |                                                     | (Native Kernel Tree)
     v                     |                                                     |
+----------------------------------------------------+                           |
|             MEOW WORKER POOL (Systemd)             |                           |
|      `meow-worker@<id>.service` in Slice           |---------------------------+
|  - Isolated worker daemons (AnyIO / uvloop)        |
|  - Heavy tasks: PyMuPDF, Ghostscript, LaTeX, ODT   |
|  - Structured Logging -> `journald` stdout         |
+----------------------------------------------------+
                           ^
                           | (Scheduled by Timer)
+---------------------------------------------------------------------------------------------------+
|                              AUTOMATED BACKUP & MIGRATION SUBSYSTEM                               |
|                     `meow-backup.timer` ---> `meow-backup.service` (Oneshot)                      |
|  - AnyIO Logical Scanner: scan & extract critical state (JSON/NDJSON) from Redis/Valkey          |
|  - Ultra-fast Zstandard Streaming Compression (`tar.zst`)                                         |
|  - Boto3 Secure Upload -> Target S3 Bucket (AWS S3 / MinIO / Ceph / Cloudflare R2)                |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Core Architectural Pillars

### 3.1. Systemd Multi-Instance & Lifecycle Management
- **Template Units**:
  - `meow-worker@.service`: Enables horizontal scaling of independent worker instances (`meow-worker@1.service`, `meow-worker@2.service`, etc.).
  - `meow-webapp@.service`: Allows running multiple balanced web application processes.
- **Hierarchical Slicing (`meow-worker.slice`)**:
  - Organizes all worker processes into a dedicated slice with `CPUAccounting=yes` and `MemoryAccounting=yes` enabled.
  - Allows setting aggregate resource safeguards and limits (e.g. `MemoryMax`, `CPUQuota`) to protect host system stability during heavy conference workloads.
- **Unified Target (`meow.target`)**:
  - Serves as the single synchronization point to start, stop, or restart the entire MEOW application pool atomically (`systemctl restart meow.target`).

### 3.2. Zero-Overhead Cgroups v2 VFS Telemetry
- **Direct Kernel File Access**:
  - WebApp reads metrics directly from `/sys/fs/cgroup/system.slice/meow-worker@*.service/` without spawning polling subprocesses (`ps`, `top`) or depending on heavy external agents.
  - **Memory Usage & Peaks**: `memory.current` (bytes currently allocated) and `memory.peak` (historical max).
  - **CPU Utilization**: `cpu.stat` (microsecond counters `usage_usec`, `user_usec`, `system_usec`).
  - **Subprocess Tracking**: `pids.current` captures all transient child processes spawned by tasks (LaTeX engines, Ghostscript conversions, `pdftk`, PyMuPDF).
- **Streaming Telemetry**:
  - Polling API: `GET /api/system/metrics` for structured point-in-time snapshots.
  - Real-Time Streaming: `GET /sse/system` for low-latency Server-Sent Events pushed to management frontends.

### 3.3. Logical Backup & Valkey Migration Subsystem
- **Application-Level State Extraction**:
  - An asynchronous scanner script using AnyIO and redis-py/valkey drivers scans logical keys (API credentials, active conference configurations, state registries) and serializes them into structured JSON/NDJSON.
  - Avoids binary `dump.rdb` vendor lock-in, enabling frictionless migration between Redis and Valkey.
- **High-Throughput Zstandard Compression**:
  - Logical datasets and local configurations are packed into streaming `tar.zst` archives with minimal CPU overhead and optimal compression ratios.
- **Automated S3 Offloading & Timers**:
  - Managed by a Systemd timer unit (`meow-backup.timer`) triggering a sandboxed oneshot service (`meow-backup.service`).
  - Automatically uploads snapshots to S3-compatible object storage (AWS S3, MinIO, Cloudflare R2, Ceph) with configurable retention lifecycle policies.

### 3.4. Structured Logging with Journald
- Worker and WebApp components output structured JSON logs directly to `stdout`.
- `systemd-journald` captures, timestamps, and indexes log streams automatically, providing instant query filtering (`journalctl -u meow-worker@1 -o json`) and log rotation without blocking application I/O.

---

## 4. Multi-Dashboard Ecosystem

The proposed architecture feeds three specialized operational dashboards:

```
+----------------------------------------------------------------------------------------------------+
|                                      MEOW DASHBOARD ECOSYSTEM                                      |
+-----------------------------------+-----------------------------------+----------------------------+
| 1. CONFERENCE WORKFLOW DASHBOARD  | 2. SYSTEM & TELEMETRY DASHBOARD   | 3. OPS & BACKUP DASHBOARD  |
|    (PURR / Indico Integration)    |    (Real-time Cluster Metrics)    |    (Admin & Disaster Rec.) |
+-----------------------------------+-----------------------------------+----------------------------+
| Purpose:                          | Purpose:                          | Purpose:                   |
| - Conference editorial ops        | - Resource bottleneck detection   | - Platform maintenance     |
| - Paper compliance checks         | - Worker pool right-sizing        | - Disaster recovery audit  |
| - Real-time task feedback         | - Memory leak / OOM prevention    | - Redis -> Valkey migration|
|                                   |                                   |                            |
| Key Components:                   | Key Components:                   | Key Components:            |
| - ODT/PDF booklet build progress  | - Real-time CPU/RAM charts/worker | - Systemd timer status     |
| - PDF check compliance badges     | - Memory peak gauges              | - S3 backup archive list   |
| - Live task log stream (WS/SSE)   | - Active subprocess (PID) count   | - Guided restore/migration |
| - Proceedings preview & download  | - Redis/Valkey queue depth        | - Aggregated journal logs  |
|                                   |                                   |                            |
| Data Channels:                    | Data Channels:                    | Data Channels:             |
| - WebSocket `/socket`             | - SSE `/sse/system`               | - REST `/api/system/admin` |
| - SSE Task Events                 | - REST `/api/system/metrics`      | - S3 ListBucket API        |
+-----------------------------------+-----------------------------------+----------------------------+
```

### Dashboard Roles & Interactions

1. **Conference Workflow Dashboard (PURR / Indico Integration)**:
   - **Audience**: JACoW Conference Editors and Scientific Secretaries.
   - **Functionality**: Live monitoring of PDF quality checks, booklet generation, and proceedings compilation without page reloads.

2. **System & Telemetry Dashboard (WebApp / Admin UI)**:
   - **Audience**: DevOps and Infrastructure Administrators.
   - **Functionality**: Real-time cluster observability via Cgroups v2 data. Allows dynamic scaling decisions and immediate detection of stalled child processes.

3. **Operations & Backup Dashboard (Admin Portal)**:
   - **Audience**: System Operators and Maintainers.
   - **Functionality**: Visibility into automated backup runs, integrity of S3 archives, and single-click validation for Redis-to-Valkey migration.

---

## 5. Architectural Comparison

| Dimension | Previous Architecture | Proposed Evolution | Operational Impact |
|---|---|---|---|
| **Process Management** | Manual scripts / Single Supervisor instance | Systemd templates (`meow-*@.service`) + Slice | Fault isolation, auto-restart, unified `meow.target` |
| **Resource Telemetry** | External forks (`ps`, `top`) or ad-hoc tools | Direct Cgroups v2 VFS (`/sys/fs/cgroup`) | Zero CPU overhead, full subprocess tree accounting |
| **Logging** | Flat local text files | Structured JSON stdout $\to$ Journald | Centralized indexing, rotation, instant filtering |
| **Data Backup** | Redis-dependent binary `dump.rdb` | AnyIO logical extraction + `tar.zst` to S3 | Engine-agnostic (Valkey ready), compact, automated |
| **Telemetry Delivery** | Generic polling endpoints | REST snapshot + streaming SSE (`/sse/system`) | Real-time responsiveness with minimal bandwidth |
