# MEOW - README

MEOW (Machine Editor for cOnferences Website) is a collection of tools and scripts to generate
the proceedings from data managed in Indico and stored on PSI or JLab file servers to be
published on JACoW at CERN and KEK.

MEOW can be used pre-conference to generate abstract booklets, during conference
to check on errors in the processed PDFs, and post-conference to generate the proceedings.

The Joint Accelerator Conferences Website (JACoW) is an international collaboration that publishes the proceedings of accelerator conferences held around the world.

[Joint Accelerator Conferences Website](https://www.jacow.org/)

## Contents

- [How it works](#how-it-works)
- [Tasks](#tasks)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running MEOW](#running-meow)
- [Configuration](#configuration)
- [Docker](#docker)
- [Testing](#testing)
- [Generating proceedings offline](#generating-proceedings-offline)
- [Repository layout](#repository-layout)
- [Further documentation](#further-documentation)

## How it works

MEOW is a compute service. It does not store conference data: the Indico plugin
(PURR) sends a *task request* for an event, the service runs it and streams back
progress, logs and the result.

```
 Indico + PURR plugin ──(task request, API key)──▶ MEOW webapp ──(queue)──▶ Redis
        ▲                                                                      │
        │                                                                      ▼
        └────(HTTP: PURR JSON endpoints, attachments, papers)────────────  MEOW worker
```

- **webapp** (`webapp.py`, Starlette app served by uvicorn on port 8080) exposes the
  `/api` (REST), `/socket` (WebSocket) and `/sse` (server-sent events) routes, plus a
  preview of the generated sites. It authenticates callers with an API key and queues
  the tasks.
- **worker** (`worker.py`) takes the queued tasks and runs them. Tasks are async Python;
  work that is CPU bound or relies on external tools runs in separate processes.
- **Redis** carries the task queue, the events between worker and webapp, and the
  per-event locks (a given event is processed by one task at a time).
- **Indico** is only read over HTTP: the PURR endpoints (`settings-and-event-data`,
  `final-proceedings-*`, `abstract-booklet-*`) and the files they point to
  (`external_download_url`), authenticated with the Indico session cookie the plugin
  forwards in the request.

Each task receives all it needs as input (`event`, `settings`, `cookies`), so a run is
fully described by the data Indico serves, which is what makes it reproducible offline
(see [Testing](#testing)).

## Tasks

Tasks are registered by code in `meow/tasks/infra/task_repository.py`:

| Code | What it does |
|---|---|
| `event_abstract_booklet` | Builds the abstract booklet of the event (ODT) |
| `event_papers_check` | Checks the PDFs of the papers and reports the errors found |
| `event_pre_press` | Generates the pre-press proceedings site (volume, brief, per-paper PDFs) |
| `event_final_proceedings` | Generates the final proceedings site, with the DOI and INSPIRE data |
| `event_compress_proceedings` | Compresses the generated proceedings into a `.7z` archive |
| `event_doi_draft`, `event_doi_publish`, `event_doi_hide`, `event_doi_delete`, `event_doi_info`, `event_doi_login` | DOI management on the DOI provider |

Generated files live under `var/` (see [Repository layout](#repository-layout)):
the proceedings site of an event is written to `var/html/<event_id>/`, its working
files to `var/run/`.

## Requirements

- Python 3.12
- Redis (to run the webapp and the worker; not needed for tests)
- External tools, bundled in `bin/` (`hugo`, `qpdf`, `mutool`, `gs`, `pdfcpu`,
  `pdfunite`, `7zzs`, `zlib-flate`, `fix-qdf`, and the `pdftk.sh` wrapper)
- Java, needed by `pdftk` (`bin/pdftk.sh`)
- `supervisor` to run the services the way the Docker image does

The Python dependencies are pinned in `requirements.txt` (runtime) and
`requirements-dev.txt` (adds pytest, fakeredis, ...).

## Installation

```
python3 -m venv venv
./venv/bin/pip install --upgrade pip setuptools wheel
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install -r requirements-dev.txt   # to run the tests
```

`requirements-dev.txt` is a full, standalone freeze (runtime + test dependencies) and
conflicts with `requirements.txt` on some pins (e.g. `yarl`). To run the tests and the
offline tools in a fresh virtualenv install **only** the dev file, e.g. with uv:

```
uv pip install --python venv/bin/python -r requirements-dev.txt
```

MEOW resolves `bin/`, `jinja/`, `assets/`, `xslt/`, `var/` and `venv/bin/python3`
relative to the current directory: run everything **from the repository root**.

## Running MEOW

Start Redis (a development container is provided in `docker/redis.dev.sh`), then
the two processes:

```
./docker/redis.dev.sh                                    # Redis on :6379

./venv/bin/uvicorn webapp:app --host 0.0.0.0 --port 8080 # webapp
./venv/bin/python3 worker.py                             # worker
```

In production the Docker image runs both under supervisor
(`supervisord -n -c ./conf/supervisord.conf`, program group `meow_programs`).
Logs go to `var/log/`.

## Configuration

Settings come from environment variables (`meow/app/config.py`):

| Variable | Default | Meaning |
|---|---|---|
| `SERVER_PORT` | `8080` | Port of the webapp |
| `LOG_LEVEL` | `info` | Log level |
| `REDIS_HOST` | `127.0.0.1` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |

Other values (HTTP timeout of 360 s, event lock timeout of 1 h) are constants in the
same file. Per-event settings (paper license, editors, DOI, ...) are not configured
in MEOW: they come from the PURR settings of the event, in the task request.

One of them tunes the optimization of the `brief` and `volume` PDFs (last step of the
generation: garbage collection and metadata with PyMuPDF, then linearization with qpdf,
each in an external process):

| Setting | Default | Meaning |
|---|---|---|
| `pdf_optimize_garbage` | `4` | Garbage collection level, 0-4. `4` merges duplicate objects and streams (the best reduction, e.g. -44% on the IPAC'26 brief, -17% on the volume, but slow on big volumes). If the optimization fails, set `2` (or lower) and generate again: on error the original file is kept. |

## Docker

`Dockerfile` (in the parent directory of this repository) builds on `base-meow`
(`python:3.12-slim` with supervisor, qpdf, pdftk, mupdf, p7zip), copies the sources to
`/opt/cat/meow`, creates the virtualenv and starts supervisor. In the Docker Compose
environment the service is `meow`:

```
docker compose build meow
docker compose up -d meow
docker compose logs -f meow
```

See `docs/DOCKER.md` for details.

## Testing

```
./venv/bin/pytest ./tests
```

The tests run fully offline: no Indico, PostgreSQL or Redis. A small **Indico mock**
(`tests/mock_indico`, a Starlette app served by uvicorn on a random local port)
emulates the PURR endpoints and the file downloads from a directory of fixture
files, and Redis is replaced by [fakeredis](https://github.com/cunla/fakeredis-py).

| Test | Covers |
|---|---|
| `test_abstract_booklet.py` | Abstract booklet on a small synthetic fixture (`tests/fixtures/indico/minimal`) |
| `test_abstract_booklet_snapshot.py` | Abstract booklet of a real event, mock serving the snapshot files with the right md5 |
| `test_proceedings_snapshot.py` | Pre-press and final proceedings, end to end, on a real event snapshot |
| `test_doi_models.py`, `test_generate_conference_doi.py` | DOI models and generation |

The `*_snapshot` tests need a snapshot of a real event and are skipped unless
`MEOW_INDICO_SNAPSHOT` points to it:

```
MEOW_INDICO_SNAPSHOT=$PWD/var/snapshots/fel2024 ./venv/bin/pytest ./tests
```

### Snapshots of a real event

`tools/snapshot_indico.py` crawls a running Indico and saves what MEOW consumes (the
PURR JSON endpoints and the files it downloads, verified against the md5 Indico
reports):

```
export INDICO_SESSION=<value of the indico_session_http cookie of an admin>
./venv/bin/python tools/snapshot_indico.py \
    --event-url http://indico:8000/event/1/ --out var/snapshots/fel2024

# a small, consistent subset
./venv/bin/python tools/snapshot_indico.py ... --sessions MOB TUP --max-contributions 3
```

Options: `--no-files` (JSON only), `--sessions`, `--max-contributions`, `--quiet`.
Re-running resumes the download.

> A snapshot contains personal data (author emails) and unpublished papers. Keep it
> outside version control (`var/` is git-ignored) and do not commit it.

More details on the mock, the fixture layout and how to write a test:
[docs/TESTING.md](docs/TESTING.md).

## Generating proceedings offline

To produce the pre-press or the final proceedings of an event without Indico, Redis
or the web interface, and keep the result to inspect it:

```
./venv/bin/python tools/run_proceedings.py \
    --snapshot var/snapshots/fel2024 --kind final --workdir var/work/fel2024
```

`--kind prepress` generates the pre-press instead (`final` is the default). The tool
runs the same task the plugin triggers, against the mock serving the snapshot, and
prints the progress and the path of the result:

```
var/work/fel2024/var/html/1/index.html     the static site
var/work/fel2024/var/html/1/pdf/           volume, brief and papers
var/work/fel2024/var/run/1_tmp/            downloaded PDFs (reused by re-runs)
```

To browse the site with working links, serve the directory:

```
cd var/work/fel2024/var/html/1 && python3 -m http.server 8081
```

This is the way to repeat alpha tests on a test event: the same snapshot always yields
the same inputs. The `.7z` archive is produced by the separate
`event_compress_proceedings` task and is not part of this run.

### Testing a branch or a PR (alpha test)

To check the effect of a change on a real event, generate the same proceedings from the
same snapshot with `develop` and with the branch, in two separate work directories, and
compare the sites:

```
git worktree add var/wt/dev develop
git worktree add var/wt/pr  <branch>      # rebased on develop

for t in dev pr; do
  (cd var/wt/$t && ../../../venv/bin/python tools/run_proceedings.py \
      --snapshot ../../snapshots/fel2024 --kind final --workdir ../../work/$t)
done
diff -rq var/work/dev/var/html/1 var/work/pr/var/html/1
```

Notes:

- Some output is not deterministic (e.g. the order of the affiliations in the institute
  pages), so also compare two runs that should be identical to know the noise, and
  compare the pages by content, not byte by byte. PDFs always differ (timestamps).
- To simulate data Indico does not have in the snapshot (e.g. a contribution custom field
  such as `CAT_preprint_marking`, or a PURR setting), copy the snapshot **with hard
  links** (`cp -al`) and rewrite only the JSON files to change: the mock refuses symlinks
  that point outside the snapshot directory.
- The preprint stamp is the text of the `pre_print` PURR setting: to see which papers
  are stamped, look for it in the first page of `var/html/<id>/pdf/<CODE>.pdf`
  (`bin/mutool draw -F txt`).
- Remote services (DOI registration, INSPIRE) are not reached: only the data sent to them
  can be checked, by calling the generating function directly.

## Repository layout

```
webapp.py, worker.py      entry points of the two processes
meow/
  app/                    application factory, config, Redis, queue, workers
  routes/                 /api, /socket, /sse and preview routes
  controllers/, callbacks/, repositories/, models/
  tasks/
    infra/                task base class, repository (task codes), runner, status
    local/                the tasks listed above
  services/local/         the logic behind the tasks
    event/                abstract booklet, final proceedings, PDF checks, ...
  utils/                  HTTP client, logging, helpers
  fonts/
bin/                      external tools (hugo, qpdf, mutool, gs, pdftk wrapper, ...)
jinja/, assets/, xslt/    templates, static assets and stylesheets of the generated sites
conf/                     supervisor configuration
docker/                   helper scripts (build, run, Redis)
tests/                    test suite, Indico mock (tests/mock_indico), fixtures
tools/                    snapshot_indico.py, run_proceedings.py
docs/                     documentation
var/                      generated at runtime (git-ignored): html, run, log, snapshots, work
```

## Further documentation

| Document | Content |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Design of the compute service and of the Indico plugins |
| [docs/INSTALL.md](docs/INSTALL.md) | Environment setup notes |
| [docs/DOCKER.md](docs/DOCKER.md) | Docker image and containers |
| [docs/TESTING.md](docs/TESTING.md) | Indico mock, fixtures, snapshots, proceedings tests |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Requirements |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Changelog |
