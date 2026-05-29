"""Optional metadatarr ``MetadataProvider`` for Classical Archives.

Importing this module registers :class:`ClassicalArchivesProvider` with the
metadatarr resolver. It is a no-op if metadatarr / mediavocab are not
installed, so it is always safe to import.

The provider activates for ``PlaybackType.AUDIO`` signals tagged with the
``"classical"`` genre. Given a composer name it resolves:

- **canonical cross-reference ids** in ``ExternalIds.extra``:
  ``classicalarchives_composer`` (the stable numeric id) and
  ``classicalarchives_url``;
- a **composer entity** under ``EntityRole.COMPOSER`` (a
  :class:`ProviderEntity`), from which metadatarr derives a deterministic
  canonical entity id via :func:`allocate_entity_id` — seeded from the
  Classical Archives id, so the same composer always collapses to the same
  entity across providers.

Usage::

    import pyclassicalarchives._provider          # register
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
"""
from __future__ import annotations

from typing import ClassVar, Optional, Set

try:
    from metadatarr.resolve.base import MetadataProvider, ProviderMatch, register
    from metadatarr.resolve.entities import EntityRole, ProviderEntity
    from mediavocab import PlaybackType
    from mediavocab.models import ExternalIds
    from mediavocab.models.signals import Signals
    _AVAILABLE = True
except ImportError:  # pragma: no cover - metadatarr/mediavocab optional
    _AVAILABLE = False

import pyclassicalarchives as _lib


if _AVAILABLE:

    def _confidence(query: str, hit_name: str) -> float:
        q, h = query.lower().strip(), hit_name.lower().strip()
        if not q:
            return 0.0
        if q == h:
            return 0.95
        if q in h or h in q:
            return 0.75
        # token overlap
        qt, ht = set(q.split()), set(h.split())
        overlap = len(qt & ht) / max(1, len(qt))
        return 0.4 + 0.3 * overlap

    class ClassicalArchivesProvider(MetadataProvider):
        """Resolve a classical composer to Classical Archives ids + entity."""

        name: ClassVar[str] = "classicalarchives"
        playback_type: ClassVar[Set["PlaybackType"]] = {PlaybackType.AUDIO}
        genre_filter: ClassVar[Set[str]] = {"classical"}

        def is_available(self) -> bool:
            return True

        def lookup(self, signals: "Signals") -> Optional["ProviderMatch"]:
            # The composer is the most reliable anchor; fall back to title.
            query = (signals.artist or signals.title or "").strip()
            if not query:
                return None
            try:
                hits = _lib.search_composers(query, limit=1)
            except Exception:
                return None
            if not hits:
                return None
            best = hits[0]

            ext = ExternalIds(extra=best.to_external_ids_dict())
            entity = ProviderEntity(
                role=EntityRole.COMPOSER,
                name=best.display_name,
                image_url=best.image,
                external_ids=ExternalIds(
                    extra={"classicalarchives_composer": best.site_id}
                ),
            )
            return ProviderMatch(
                provider=self.name,
                confidence=_confidence(query, best.display_name),
                external_ids=ext,
                relations={EntityRole.COMPOSER: [entity]},
            )

    register(ClassicalArchivesProvider())
