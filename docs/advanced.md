# Advanced usage

## Transport and the shared session

All HTTP traffic goes through one process-global session, created on first
use (`pyclassicalarchives._transport.default_session`). It is a
`requests.Session` with browser-like headers.

### Stealth mode (curl_cffi)

If Classical Archives ever starts gating plain clients, switch to Chrome TLS
impersonation:

```bash
pip install pyclassicalarchives[stealth]
export PYCLASSICALARCHIVES_TRANSPORT=curl_cffi
```

The library reads this variable once, when it creates the session. Set it
before your first API call.

## Pagination and streaming

The catalogue is large. Prefer the lazy iterator and slice it:

```python
import itertools
import pyclassicalarchives as ca

# First 200 composers across the whole alphabet, without materializing all of it
head = list(itertools.islice(ca.iter_all_composers(), 200))

# Only a sub-range of initials
for c in ca.iter_all_composers("ABC"):
    ...
```

`get_composers_by_letter` returns a whole initial in one request. Some
letters hold well over a thousand composers.

## Rate limits and politeness

`robots.txt` declares `Crawl-delay: 1`. When you walk the full catalogue or
fetch many composer pages, throttle your requests:

```python
import time
import pyclassicalarchives as ca

for c in ca.iter_all_composers():
    detail = ca.fetch_composer(c.composer_id)
    ...
    time.sleep(1)        # be a good citizen
```

`fetch_composer` is the expensive call: one HTTP request per composer. A
prolific composer's page can carry thousands of works and albums.

## Error handling

| Situation | What happens |
|---|---|
| Unknown composer id | `fetch_composer` raises `ComposerNotFound` |
| Non-letter passed to `get_composers_by_letter` | `ValueError` |
| Network / non-2xx | the underlying `requests.HTTPError` propagates |

```python
import pyclassicalarchives as ca

try:
    detail = ca.fetch_composer(some_id)
except ca.ComposerNotFound:
    detail = None
```

## The works tree

A composer page nests works under arbitrarily deep category groups
(`Vocal Works → Sacred Cantatas → Cantatas BWV1-50 → …`). The library walks
the tree and returns a **flat list of leaf works only**, each tagged with:

- `category`: the top-level group title.
- `category_path`: the full list of group titles from root to the work.

So `len(detail.works)` counts actual pieces, not category headers.

## Field name notes

The wire format uses terse keys. The dataclasses normalize them. A few
things worth knowing:

- List endpoints give clean `birth`/`death` years. The composer **page**
  gives a combined `life` string (`"(1685-1750)"`), which the library also
  parses into `birth`/`death`.
- `country` is ISO 3166-1 **alpha-3** (`"DEU"`, `"USA"`, `"FRA"`).
- Album `duration` is in **seconds**.

---
[← API reference](api.md) · [Home](../README.md) · [Canonical ids →](canonical_ids.md)
