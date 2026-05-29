# AGENTS.md — pyclassicalarchives

Typed Python client for Classical Archives (classicalarchives.com): browse
curated and full A–Z composer lists, search by name, fetch full composer pages
(bio, period, albums, works), with optional metadatarr provider integration and
a dataset row builder.

## Setup

```bash
pip install -e .
pip install -e .[stealth]   # adds curl-cffi for Chrome TLS impersonation
pip install -e .[dev]       # adds pytest
```

## Test

```bash
pytest
```

The offline tests (`tests/`) parse representative API fixtures — no network.
In the shared OVOS dev venv `pytest-recording` and `pytest-vcr` clash (an
environment issue, not this package); if you hit it, run
`pytest -p no:recording`.

## Lint/Typecheck

No linter / type checker is configured. Source is fully type-annotated with
`from __future__ import annotations`; mypy/ruff could be added.

## Layout

- `pyclassicalarchives/__init__.py` — public API surface. Re-exports the models
  (`Composer`, `ComposerDetail`, `Album`, `Work`), the functions
  (`get_notable_composers`, `get_must_know_composers`, `get_composers_by_letter`,
  `iter_all_composers`, `get_all_composers`, `fetch_composer`,
  `search_composers`) and `ComposerNotFound`.
- `pyclassicalarchives/types.py` — the dataclasses and their `from_api`
  constructors, plus helpers: `_abs_image`, `_display_name`, `_strip_html`
  (strips tags + unescapes entities), `_parse_life` (parses `"(1685-1750)"`),
  and `_flatten_works` (recursively walks the nested category/work tree to leaf
  works, tagging each with its `category_path`).
- `pyclassicalarchives/composers.py` — the lookup functions and the
  client-side `search_composers` (no server search endpoint exists).
- `pyclassicalarchives/_transport.py` — `get_json()` over a shared session;
  `PYCLASSICALARCHIVES_TRANSPORT=curl_cffi` swaps in curl_cffi impersonation.
- `pyclassicalarchives/_provider.py` — optional metadatarr `MetadataProvider`.
  Import-time best-effort registration; no-ops if metadatarr/mediavocab absent.
  Matches `PlaybackType.AUDIO` + `content_genres` containing `"classical"`;
  emits external ids and an `EntityRole.COMPOSER` entity.
- `pyclassicalarchives/dataset.py` — flat row builders for HF datasets
  (`composer_rows`, `composer_detail_row`, `work_rows`, `album_rows`,
  `build_dataset`, `write_jsonl`).
- `docs/` — quickstart, api, advanced, metadatarr, dataset guides.
- `examples/` — numbered runnable scripts (01–10).

## API surface (classicalarchives.com)

Public JSON, no key required:

- `/api/composer_list_notable.json` — notable list (rich fields)
- `/api/mustknow_composers.json` — must-know list (terse `[id, name, img]`)
- `/api/composer_list_all.json?letter=X` — full catalogue per initial
- `/api/composer_page.json?composer_id=N` — full composer detail

There is **no public album/work/performer/search endpoint** — those JS-driven
asset bundles are bot-gated. Album and work data come embedded in the composer
page; search is built client-side over the by-letter listings.

## Conventions (Org hard rules)

- Branches: `dev` (work) / `master` (stable). NEVER `main`.
- Never edit `pyclassicalarchives/version.py`; gh-automations bumps semver from
  conventional-commit prefixes (`feat:`/`fix:`/`feat!:`).
- New repos private by default.
- Commit identity: JarbasAi <jarbasai@mailfence.com>.
- Reference OpenVoiceOS/gh-automations reusable workflows at `@dev`.
- No Neon / `neon-*` references.
- No meta-commentary in docs/commits/code (no history, dates, or "before times").

## Gotchas

- Composers are listed **surname-first** (`"Bach, Johann Sebastian"`); use
  `display_name` for natural order. The composer **page** `name` is already
  natural order.
- List endpoints carry clean `birth`/`death`; the composer page carries a
  combined `life` string instead, which `_parse_life` splits.
- `country` is ISO 3166-1 **alpha-3**; album `duration` is **seconds**.
- The works tree is arbitrarily deep — `_flatten_works` must stay recursive, or
  sub-category nodes leak in as fake works (they have no `rec` field).
- `search_composers` only fetches the listings for the **initials in the
  query**; a query whose tokens don't include the surname's initial won't find
  the composer. Ranking uses recording count as the popularity tiebreak.
- The HTTP session is a process-global singleton; `PYCLASSICALARCHIVES_TRANSPORT`
  is read only on first request.
