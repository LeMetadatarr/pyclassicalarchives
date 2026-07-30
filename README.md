# pyclassicalarchives

A typed Python client for [Classical Archives](https://www.classicalarchives.com),
one of the largest classical music catalogues on the web.

The library wraps the site's public JSON API in dataclasses. Use it to browse
curated and full A-Z composer lists, search by name, and fetch a composer's
full page (biography, period, lifedates, **albums**, and **works**). Every
model exposes a canonical id for de-duplication, and an optional
[metadatarr](../metadatarr) provider cross-references that id with other
sources.

## Install

```bash
pip install pyclassicalarchives
pip install pyclassicalarchives[stealth]   # adds curl-cffi (Chrome TLS), if ever gated
pip install pyclassicalarchives[dev]       # adds pytest
```

## 30-second tour

```python
import pyclassicalarchives as ca

# Curated lists
for c in ca.get_notable_composers()[:5]:
    print(c.composer_id, c.display_name, c.country, c.birth, c.death)

# Search by name (surname-first or natural order both work)
bach = ca.search_composers("johann sebastian bach")[0]

# Full page: bio, period, albums, works
detail = ca.fetch_composer(bach.composer_id)
print(detail.life, detail.period)                 # (1685-1750) Baroque
print(len(detail.albums), "albums,", len(detail.works), "works")

# Canonical ids for dedup / cross-referencing
print(detail.to_external_ids_dict())
# {'classicalarchives_composer': '2113', 'classicalarchives_url': '.../composer/2113.html'}
```

## What you can fetch

| Function | Returns | Source endpoint |
|---|---|---|
| `get_notable_composers()` | `List[Composer]` | `composer_list_notable.json` |
| `get_must_know_composers()` | `List[Composer]` | `mustknow_composers.json` |
| `get_composers_by_letter("B")` | `List[Composer]` | `composer_list_all.json?letter=` |
| `iter_all_composers()` | `Iterator[Composer]` | the whole A-Z catalogue (lazy) |
| `search_composers("mozart")` | `List[Composer]` | client-side over the by-letter lists |
| `fetch_composer(id)` | `ComposerDetail` | `composer_page.json?composer_id=` |

A `ComposerDetail` carries nested `albums: List[Album]` and `works: List[Work]`.
The library flattens the works tree to leaf works, and tags each one with its
full category path.

## Documentation

Start with **[docs/quickstart.md](docs/quickstart.md)**, then:

- [docs/api.md](docs/api.md): every function, every model field
- [docs/advanced.md](docs/advanced.md): pagination, transport, error handling, rate limits
- [docs/canonical_ids.md](docs/canonical_ids.md): canonical ids (how metadatarr consumes this)
- [docs/dataset.md](docs/dataset.md): building a Hugging Face dataset

Runnable, numbered scripts live in [examples/](examples/).

## Canonical ids and metadatarr

This package is a pure scraper. It exposes Classical Archives' stable ids
through `site_id` and `to_external_ids_dict()`:

```python
bach = ca.search_composers("johann sebastian bach")[0]
bach.to_external_ids_dict()
# {'classicalarchives_composer': '2113',
#  'classicalarchives_url': 'https://www.classicalarchives.com/composer/2113.html'}
```

The metadatarr resolver consumes these ids. The `MetadataProvider` itself
lives in the [metadatarr](../metadatarr) repo
(`metadatarr/resolve/providers/classicalarchives.py`), not here, so
integration code stays out of client repos. Install both packages and
metadatarr auto-discovers the provider. See
[docs/canonical_ids.md](docs/canonical_ids.md).
