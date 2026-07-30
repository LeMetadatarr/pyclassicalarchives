# Canonical identifiers (for dedup and cross-referencing)

This client exposes Classical Archives' **stable identifiers**, so a
downstream resolver can de-duplicate and cross-reference. The resolver
itself, the metadatarr `MetadataProvider`, lives in the
**[metadatarr](../../metadatarr)** repo, not here. This package is a pure
scraper. metadatarr *consumes* it.

## What this client exposes

Classical Archives assigns a stable integer id to every composer, work, and
album. Each model surfaces them two ways:

| Entity | `site_id` | Canonical web URL | `to_external_ids_dict()` keys |
|---|---|---|---|
| Composer | composer id | `/composer/<id>.html` | `classicalarchives_composer`, `classicalarchives_url` |
| Work | work id | `/work/<id>.html` | `classicalarchives_work`, `classicalarchives_url` |
| Album | album id | `/album/<id>.html` | `classicalarchives_album`, `classicalarchives_url` |

```python
import pyclassicalarchives as ca

bach = ca.search_composers("johann sebastian bach")[0]
bach.site_id                    # '2113'
bach.to_external_ids_dict()
# {'classicalarchives_composer': '2113',
#  'classicalarchives_url': 'https://www.classicalarchives.com/composer/2113.html'}
```

`to_external_ids_dict()` returns exactly the shape metadatarr stores under
`ExternalIds.extra`, a free-form string-to-string namespace. Two records that
share `classicalarchives_composer` are the same composer. That is your
**dedup / join key**.

## How metadatarr consumes this

metadatarr ships a provider (`metadatarr/resolve/providers/classicalarchives.py`)
that imports this library, resolves a composer for `PlaybackType.AUDIO` and
`"classical"` signals, and emits the external ids above plus an
`EntityRole.COMPOSER` entity. From that entity, metadatarr derives a
deterministic canonical entity id (`allocate_entity_id`), so the same
composer collapses to one entity across providers.

You do not import or configure anything here for that to work. Installing
both `pyclassicalarchives` and `metadatarr` is enough. metadatarr
auto-discovers the provider and disables itself if this library is not
installed. See the metadatarr repo for resolver usage.

---
[← Advanced usage](advanced.md) · [Home](../README.md) · [Building a dataset →](dataset.md)
