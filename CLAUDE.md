# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv run pytest                   # run all tests (or: just test)
uv run pytest tests/test_doffin.py::test_name  # run a single test
uv run ruff check .             # lint (just lint)
uv run ruff format .            # format (just fmt)
uv run pre-commit run --all-files  # run all pre-commit hooks
```

CI (`.github/workflows/ci.yml`) runs `ruff format --check`, `ruff check`, and `pytest`. Pushing a `v*` tag additionally builds with `uv build` and attaches `dist/*` to a GitHub Release (PyPI package `ymse`, Python >=3.13, hatchling).

## Architecture

Small utility package managed with `uv`. Two independent modules, both re-exported from `ymse/__init__.py` as the public API (`run`, `search_doffin`):

- `ymse/core.py` — Lettermint email: `send_email()` and `run()` (a smoke test that sends a real email to a hardcoded address; do not call it in tests).
- `ymse/doffin.py` — `search_doffin()` queries the Doffin procurement API, paginating per query and returning a flat list of normalized dicts (each tagged with the originating `query`).
- `tests/` — `test_core.py`, `test_doffin.py`. Doffin tests mock `ymse.doffin.requests.get`; patch at that path.

Note: `send_email` is not in `__all__`; import it via `ymse.core`.

## Configuration (env vars, loaded via python-dotenv from `.env`)

- `LETTERMINT_API_TOKEN`, `LETTERMINT_SENDER` — required by `send_email` (sender can be overridden per call). `core.py` calls `load_dotenv()` at import time.
- `DOFFIN_API_KEY` — required unless `api_key` is passed. `DOFFIN_BASE_URL` overrides the default endpoint. `doffin.py` calls `load_dotenv()` inside `search_doffin`.

## Gotchas

- `search_doffin` always sends `numHitsPerPage=100` regardless of the `page_size` arg; `page_size` is only used for the "last page" check.
- `DEFAULT_BASE_URL` ends in `/` and the request URL is built as `f"{base_url}/search"`, producing `//search`.

## Git

Keep all commit messages one-liners (short).
Pre-commit enforces ruff lint + format on every commit.
