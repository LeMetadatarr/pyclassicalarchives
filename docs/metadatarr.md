# metadatarr integration — canonical ids & entity lookup

This page answers two questions:

1. **What are the canonical / unique identifiers?**
2. **How do you do entity and media lookup with them?**

## Canonical identifiers

Classical Archives assigns a stable integer id to every composer, work and
album. Those ids are the canonical keys this library exposes:

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

These keys live under `ExternalIds.extra` in
[mediavocab](../../mediavocab) — a free-form, string→string namespace that any
provider can extend without changing the typed schema. Use them as your
**dedup / join key**: two records with the same `classicalarchives_composer`
are the same composer.

## Entity lookup

The interesting part for cross-referencing is that a composer is a **person
entity**, not just an id. The provider emits a `ProviderEntity` under
`EntityRole.COMPOSER`, and metadatarr turns that into a deterministic
**canonical entity id** via `allocate_entity_id`:

```python
from metadatarr.resolve.entities import EntityRole, ProviderEntity, allocate_entity_id
from mediavocab.models import ExternalIds

entity = ProviderEntity(
    role=EntityRole.COMPOSER,
    name="Johann Sebastian Bach",
    external_ids=ExternalIds(extra={"classicalarchives_composer": "2113"}),
)
canonical = allocate_entity_id(EntityRole.COMPOSER, name=entity.name,
                               external_ids=entity.external_ids)
# a stable sha1 seeded from the Classical Archives id — same id ⇒ same entity,
# regardless of how the name is spelled across providers.
```

Because the seed prefers the authoritative external id over the name, the same
composer collapses to one entity even when other sources spell the name
differently ("J.S. Bach", "Bach, Johann Sebastian", …).

## The resolver provider

Importing `pyclassicalarchives._provider` registers a `MetadataProvider` with
the metadatarr resolver. It is a no-op if metadatarr / mediavocab are not
installed, so the import is always safe.

It activates for `PlaybackType.AUDIO` signals tagged with the `"classical"`
genre, resolves the composer (preferring `signals.artist`, falling back to
`signals.title`), and returns a `ProviderMatch` carrying the external ids and
the composer entity.

```python
import pyclassicalarchives._provider          # registers the provider
from metadatarr.resolve.base import resolve
from mediavocab.models.signals import Signals
from mediavocab import PlaybackType

result = resolve(Signals(
    title="Goldberg Variations",
    artist="Johann Sebastian Bach",
    playback_type=PlaybackType.AUDIO,
    content_genres=["classical"],
))
print(result.external_ids.extra)
# {'classicalarchives_composer': '2113', 'classicalarchives_url': '...'}
```

### Confidence

The match `confidence` reflects how well the composer name matched:

| Match | Confidence |
|---|---|
| exact name | 0.95 |
| one name contains the other | 0.75 |
| partial token overlap | 0.40–0.70 |

### Driving the provider directly

`resolve()` fans signals out across **every** registered provider. To exercise
just this one (useful in tests or focused tooling), call it directly:

```python
import pyclassicalarchives._provider as p
prov = p.ClassicalArchivesProvider()
match = prov.lookup(Signals(artist="Beethoven",
                            playback_type=PlaybackType.AUDIO,
                            content_genres=["classical"]))
print(match.external_ids.extra, match.confidence)
```

See `examples/09_metadatarr.py` for a complete, runnable script.

## What this provider does **not** resolve

It resolves **composers** (the entity classical music is catalogued by). It
does not attempt recording- or release-level identity — Classical Archives'
album/work ids are exposed on `ComposerDetail` for you to use, but the resolver
match anchors on the composer. For recording-level cross-references, combine
with MusicBrainz / Discogs providers in the same resolve call.
