# Agent Guidelines for MEOW

Welcome to the MEOW (Machine Editor for cOnferences Website) repository. This document serves as the primary index and navigation portal for AI agents and human contributors.

---

## Documentation Index

Detailed documentation is organized within the `docs/` directory:

| Document | Description |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | High-level system architecture, webapp & worker components, Redis message flow, task services, and Indico integration. |
| [`docs/TECH_STACK.md`](docs/TECH_STACK.md) | Technology stack details including Python, Starlette, AnyIO, Redis, PyMuPDF, pikepdf, Jinja2, and Supervisor. |
| [`docs/WORKFLOW.md`](docs/WORKFLOW.md) | Development workflow, English language rule, GitHub issue tracking, pull request (PR) template, and testing standards. |
| [`docs/INSTALL.md`](docs/INSTALL.md) | Step-by-step local environment setup, virtualenv initialization, running Redis, webapp, worker, and test suite. |
| [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) | System-level dependencies (C-libraries, Redis) and categorized Python runtime and development package dependencies. |
| [`docs/EXTERNAL_TOOLS.md`](docs/EXTERNAL_TOOLS.md) | External CLI tools and binaries (`bin/`), Java/JRE requirements (`pdftk`), bundled libraries (`lib/`), and subprocess wrappers. |
| [`docs/DOCKER.md`](docs/DOCKER.md) | Containerization guide, Dockerfile base image (`python:3.11`), helper scripts (`docker/*.sh`), and environment variables. |

---

## Key Agent Directives

1. **Language**: Always use **English** for code, documentation, commit messages, PR descriptions, and issue discussions.
2. **Consult Relevant Docs**: When implementing features or investigating bugs, consult the corresponding document (e.g. `docs/ARCHITECTURE.md` for task dispatch, `docs/WORKFLOW.md` for PR formatting).
3. **PR Formatting**: Pull requests must follow the structured format outlined in [`docs/WORKFLOW.md`](docs/WORKFLOW.md).
