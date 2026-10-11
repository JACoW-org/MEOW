# Testing

```
./venv/bin/pytest ./tests
```

Tests run fully offline: no Indico, PostgreSQL or Redis.

## Indico mock

MEOW reads everything from Indico (PURR plugin endpoints, attachments) over
HTTP. `tests/mock_indico` is a small Starlette app, served by uvicorn on a
random local port, that emulates those endpoints from files.

It is a *file-tree server*: `GET /<path>` returns `<fixture>/<path>[.json]`,
so a fixture mirrors the URLs MEOW calls:

```
tests/fixtures/indico/minimal/
  snapshot.json                               # {"origin": "<host used in the JSON>"}
  event/1/manage/purr/
    settings-and-event-data.json              # task params: {event, settings}
    abstract-booklet-sessions-data.json
    abstract-booklet-contributions-data/<session_block_id>.json
```

- requests without the `indico_session_http` cookie get `403`, missing files `404`
- the mock records every request (`indico_mock.mock.requests`) so tests can assert on them
- the `origin` of `snapshot.json` is replaced, in JSON bodies, with the mock's own address:
  fixtures keep the real Indico host (`http://indico:8000`) and the file URLs
  they contain (`external_download_url`) resolve to the mock

## Writing a test

Use the `task_params` fixture (the `params` the plugin sends to a task) and run the
task as the worker does. See `tests/test_abstract_booklet.py`.

To cover a new endpoint or scenario, add files to a fixture directory; the mock needs no code changes.

## Snapshots of a real event

`tools/snapshot_indico.py` crawls a running Indico and writes everything MEOW
consumes in the layout above: the PURR JSON endpoints and the files MEOW
downloads (papers, slides and posters of the latest revision of each editable,
and event attachments), checked against the `md5sum` Indico reports.

```
export INDICO_SESSION=<value of the indico_session_http cookie of an admin>
./venv/bin/python tools/snapshot_indico.py \
    --event-url http://indico:8000/event/1/ --out var/snapshots/fel2024

# a small, consistent subset
... --sessions MOB TUP --max-contributions 3
```

Options: `--no-files` (JSON only), `--sessions`, `--max-contributions`. The
subset keeps the same contributions in the final-proceedings and abstract-booklet
exports. Re-running resumes: files already present with the right md5 are not downloaded.

A snapshot contains personal data (author emails) and unpublished papers, so keep it
outside version control (`var/` is ignored). Tests that need one are skipped unless
`MEOW_INDICO_SNAPSHOT` points to it:

```
MEOW_INDICO_SNAPSHOT=$PWD/var/snapshots/fel2024 ./venv/bin/pytest ./tests
```

Their expectations are derived from the snapshot itself, so they work with any event.

## Pre-press and final proceedings

`tests/test_proceedings_snapshot.py` runs `EventPrePressProceedingsTask` and
`EventFinalProceedingsTask` end to end on a snapshot: download of papers from
the mock, PDF checks and metadata, concatenation, site generation with `bin/hugo`.
It needs no Indico and no Redis: Redis is [fakeredis](https://github.com/cunla/fakeredis-py)
(`dbs.redis_client` is replaced, so the event lock works as usual).

The pipelines use paths relative to the repository root (`var/`, `bin/`,
`jinja/`, `venv/bin/python3`, ...) and some tools from `PATH`. The `meow_workdir`
fixture runs the test in a scratch directory that links to those resources, so
output goes to a throw-away `var/` and the repository is left untouched.

The checks are consistency checks between the generated files (every included
paper is in the volume and in the site, positions match page counts, the brief
has one page per paper, ...), so they work with any event. On the FEL 2024
snapshot (230 contributions, 73 papers) both pipelines take about 20 s each.

Tools required on the host: those in `bin/` (hugo, qpdf, mutool, gs, ...) and `java`
for `pdftk`.

### Generating proceedings from a snapshot

To inspect the output (the tests discard it), `tools/run_proceedings.py` runs the
same task and keeps the result in `--workdir`:

```
./venv/bin/python tools/run_proceedings.py \
    --snapshot var/snapshots/fel2024 --kind final --workdir var/work/fel2024
# open var/work/fel2024/var/html/1/index.html
```

`--kind prepress` generates the pre-press instead. Outputs under `<workdir>/var/`:
`html/<event_id>/` (site, with `pdf/` volume and brief), `run/<event_id>_doi` and
`run/<event_id>_hep` (DOI and INSPIRE payloads), `run/<event_id>_refs`,
`run/<event_id>_tmp` (downloaded PDFs, reused by re-runs). The `.7z` archive is
produced by a separate task (compress proceedings) and is not part of this run.
