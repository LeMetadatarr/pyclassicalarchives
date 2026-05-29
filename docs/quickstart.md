# Quickstart — zero to hero

This guide takes you from `pip install` to fetching a composer's complete
catalogue. No API key is required; Classical Archives' JSON API is public.

## 1. Install

```bash
pip install pyclassicalarchives
```

If the site ever starts blocking plain HTTP clients, install the stealth extra
and flip one environment variable (see [advanced.md](advanced.md)):

```bash
pip install pyclassicalarchives[stealth]
export PYCLASSICALARCHIVES_TRANSPORT=curl_cffi
```

## 2. The mental model

Classical Archives is organised around three things, and so is this library:

```
Composer ──┬── writes ──▶ Work   (a piece of music: a cantata, a concerto, …)
           └── appears on ─▶ Album (a recording release)
```

- A **`Composer`** is the lightweight shape you get from any *list* endpoint.
- A **`ComposerDetail`** is the *full page*: biography, period, lifedates, plus
  the composer's **albums** and **works**.
- **`Album`** and **`Work`** are always reached through a `ComposerDetail`.

## 3. Browse the curated lists

```python
import pyclassicalarchives as ca

notable = ca.get_notable_composers()
print(len(notable), "notable composers")        # ~300+

for c in notable[:5]:
    print(c.composer_id, c.display_name, c.country, f"{c.birth}-{c.death or ''}")
```

`get_must_know_composers()` returns a smaller, curated "must know" set (these
come back as terse triples, so only id / name / image are populated).

## 4. Browse the full A–Z catalogue

```python
# One initial at a time
bs = ca.get_composers_by_letter("B")
print(len(bs), "composers whose surname starts with B")

# Or stream the whole alphabet lazily
import itertools
for c in itertools.islice(ca.iter_all_composers(), 20):
    print(c.name)
```

> Composers are listed **surname-first** (`"Bach, Johann Sebastian"`). Use the
> `display_name` property for the natural `"Johann Sebastian Bach"` form.

## 5. Search by name

There is no server-side search endpoint, so the library builds one from the
by-letter listings. It works with surname-first or natural order, and ranks
the most-recorded composer first:

```python
ca.search_composers("mozart")[0].display_name        # 'Wolfgang Amadeus Mozart'
ca.search_composers("johann sebastian bach")[0]       # the real J. S. Bach (id 2113)
ca.search_composers("beethoven", limit=1)
```

## 6. Fetch a full composer page

A single call returns the biography, period, lifedates, and the composer's
albums and works:

```python
bach = ca.fetch_composer(2113)
print(bach.display_name)        # Johann Sebastian Bach
print(bach.life, bach.period)   # (1685-1750) Baroque
print(bach.country)             # DEU
print(bach.bio[:120])           # plain-text biography
print(len(bach.albums), "albums,", len(bach.works), "works")
```

An unknown id raises `ComposerNotFound`:

```python
try:
    ca.fetch_composer(999_999_999)
except ca.ComposerNotFound as e:
    print(e)        # 999999999: Composer does not exist
```

## 7. Explore albums and works

```python
detail = ca.fetch_composer(2113)

for a in detail.albums[:3]:
    print(a.title, "—", a.label, f"({a.n_tracks} tracks, {a.duration}s)")

for w in detail.works[:3]:
    print(" > ".join(w.category_path), "::", w.title, f"({w.n_recordings} recordings)")
```

`category_path` is the full root→leaf path through the site's nested work
groups; `category` is just the top-level group.

## 8. Serialise

Every model has `to_dict()` (JSON-friendly) and `to_external_ids_dict()`:

```python
import json
print(json.dumps(detail.albums[0].to_dict(), indent=2))
print(detail.to_external_ids_dict())
```

## Next steps

- [api.md](api.md) — the complete reference
- [metadatarr.md](metadatarr.md) — canonical ids and the resolver provider
- [dataset.md](dataset.md) — turn the catalogue into a Hugging Face dataset
- [advanced.md](advanced.md) — transport, rate limits, error handling
