"""pyclassicalarchives — typed Python client for Classical Archives.

Classical Archives (classicalarchives.com) is a large catalogue of classical
music: composers, the works they wrote, and the albums those works appear on.
This package wraps its public JSON API behind clean dataclasses.

Quick start::

    import pyclassicalarchives as ca

    # Curated lists
    for c in ca.get_notable_composers()[:5]:
        print(c.composer_id, c.display_name, c.country)

    for c in ca.get_must_know_composers()[:5]:
        print(c.display_name)

    # Search by name (client-side, built on the by-letter listings)
    bach = ca.search_composers("johann sebastian bach")[0]
    print(bach.composer_id, bach.url)

    # Full composer page: bio, period, albums and works
    detail = ca.fetch_composer(bach.composer_id)
    print(detail.life, detail.period)
    print(len(detail.albums), "albums,", len(detail.works), "works")

    # Stream the whole A–Z catalogue lazily
    import itertools
    for c in itertools.islice(ca.iter_all_composers(), 20):
        print(c.display_name)

    # Serialise anything to a plain dict / JSON
    import json
    print(json.dumps(detail.to_dict(), indent=2)[:400])

    # Canonical ids for dedup / metadatarr
    print(detail.to_external_ids_dict())

metadatarr integration (optional)::

    import pyclassicalarchives._provider          # registers the provider
    from metadatarr.resolve.base import resolve
    from mediavocab.models.signals import Signals
    from mediavocab import PlaybackType

    result = resolve(Signals(
        artist="Johann Sebastian Bach",
        playback_type=PlaybackType.AUDIO,
        content_genres=["classical"],
    ))
    print(result.external_ids.extra)
"""
from pyclassicalarchives.types import Album, Composer, ComposerDetail, Work
from pyclassicalarchives.composers import (
    ComposerNotFound,
    fetch_composer,
    get_all_composers,
    get_composers_by_letter,
    get_must_know_composers,
    get_notable_composers,
    iter_all_composers,
    search_composers,
)
from pyclassicalarchives.version import __version__

__all__ = [
    "Album",
    "Composer",
    "ComposerDetail",
    "Work",
    "ComposerNotFound",
    "fetch_composer",
    "get_all_composers",
    "get_composers_by_letter",
    "get_must_know_composers",
    "get_notable_composers",
    "iter_all_composers",
    "search_composers",
    "__version__",
]
