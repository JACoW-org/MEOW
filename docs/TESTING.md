# Testing

```
./venv/bin/pytest ./tests
```

Tests run fully offline: no Indico, PostgreSQL or Redis.

## Indico mock

MEOW reads everything from Indico (PURR plugin endpoints, attachments) over
HTTP. `tests/mock_indico` is a small Starlette app, served by uvicorn on a
random local port, that emulates those endpoints from files.

It is a *file-tree server*: `GET /<path>` returns `tests/fixtures/indico/<scenario>/<path>[.json]`,
so a fixture mirrors the URLs MEOW calls:

```
tests/fixtures/indico/minimal/
  event.json                                  # task params: {event, settings}
  event/1/manage/purr/
    abstract-booklet-sessions-data.json
    abstract-booklet-contributions-data/<session_block_id>.json
```

- requests without the `indico_session_http` cookie get `403`, missing files `404`
- the mock records every request (`indico_mock.mock.requests`) so tests can assert on them
- `event.url` is rewritten to the mock's address by the `task_params` fixture

## Writing a test

Use the `task_params` fixture (the `params` the plugin sends to a task) and run the
task as the worker does. See `tests/test_abstract_booklet.py`.

To cover a new endpoint or scenario, add files to a fixture directory; the mock needs no code changes.
