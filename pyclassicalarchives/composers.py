"""Composer lookup functions backed by the Classical Archives JSON API.

The public surface is composer-centric, mirroring the site itself. Each
composer page embeds that composer's albums and works, so a single
:func:`fetch_composer` call returns a rich graph.

Endpoints used:

- ``/api/composer_list_notable.json``     — curated "notable" list
- ``/api/mustknow_composers.json``         — curated "must know" list
- ``/api/composer_list_all.json?letter=X`` — full A–Z catalogue, per initial
- ``/api/composer_page.json?composer_id=`` — full composer detail
"""
from __future__ import annotations

import string
from typing import Dict, Iterator, List, Optional

from pyclassicalarchives._transport import get_json
from pyclassicalarchives.types import Composer, ComposerDetail


class ComposerNotFound(Exception):
    """Raised by :func:`fetch_composer` when the id does not exist."""


def get_notable_composers() -> List[Composer]:
    """Return the curated list of *notable* composers.

    Example::

        import pyclassicalarchives as ca
        notable = ca.get_notable_composers()
        print(len(notable), "notable composers")
        print(notable[0].display_name)
    """
    data = get_json("/api/composer_list_notable.json")
    return [Composer.from_api(c, notable=True) for c in data]


def get_must_know_composers() -> List[Composer]:
    """Return the curated *must know* composers.

    This endpoint returns terse ``[id, name, image]`` triples, so the
    resulting :class:`Composer` objects carry only id, name and image.

    Example::

        import pyclassicalarchives as ca
        for c in ca.get_must_know_composers()[:5]:
            print(c.composer_id, c.display_name)
    """
    data = get_json("/api/mustknow_composers.json")
    out: List[Composer] = []
    for composer_id, name, img in data:
        c = Composer(composer_id=int(composer_id), name=name, must_know=True)
        from pyclassicalarchives.types import _abs_image
        c.image = _abs_image(img)
        out.append(c)
    return out


def get_composers_by_letter(letter: str) -> List[Composer]:
    """Return every composer whose surname starts with *letter* (A–Z).

    Example::

        import pyclassicalarchives as ca
        bs = ca.get_composers_by_letter("B")
        print(len(bs), "composers under B")
    """
    letter = letter.strip().upper()[:1]
    if letter not in string.ascii_uppercase:
        raise ValueError(f"letter must be A-Z, got {letter!r}")
    data = get_json("/api/composer_list_all.json", letter=letter)
    return [Composer.from_api(c) for c in data]


def iter_all_composers(
    letters: Optional[str] = None,
) -> Iterator[Composer]:
    """Lazily iterate the full A–Z composer catalogue.

    Args:
        letters: Restrict to these initials (e.g. ``"ABC"``). Defaults to
                 the whole alphabet.

    Example::

        import itertools, pyclassicalarchives as ca
        first_50 = list(itertools.islice(ca.iter_all_composers(), 50))
    """
    for letter in (letters or string.ascii_uppercase):
        yield from get_composers_by_letter(letter)


def get_all_composers(letters: Optional[str] = None) -> List[Composer]:
    """Eagerly collect the full A–Z catalogue (large: tens of thousands).

    Prefer :func:`iter_all_composers` for streaming. ``letters`` restricts
    to a subset of initials.
    """
    return list(iter_all_composers(letters))


def fetch_composer(composer_id: int) -> ComposerDetail:
    """Fetch the full composer page (bio, albums, works).

    Args:
        composer_id: Classical Archives composer id (int or str).

    Raises:
        ComposerNotFound: when the id does not resolve to a composer.

    Example::

        import pyclassicalarchives as ca
        bach = ca.fetch_composer(2113)
        print(bach.display_name, bach.life, bach.period)
        print(bach.n_albums, "albums")
    """
    data = get_json("/api/composer_page.json", composer_id=composer_id)
    if isinstance(data, dict) and data.get("error"):
        raise ComposerNotFound(f"{composer_id}: {data['error']}")
    return ComposerDetail.from_api(data)


def search_composers(query: str, limit: Optional[int] = None) -> List[Composer]:
    """Search the catalogue for composers matching *query* by name.

    Classical Archives exposes no server-side search endpoint, so this
    builds one client-side: it fetches the by-letter listings for the
    initials present in *query* (surname-first ``"Bach"`` and natural
    ``"Johann Sebastian Bach"`` both work) and returns composers whose
    name contains every query token, ranked by how early the strongest
    token matches.

    Args:
        query: Free-text name fragment.
        limit: Cap the number of results returned.

    Example::

        import pyclassicalarchives as ca
        hits = ca.search_composers("mozart")
        print(hits[0].display_name, hits[0].composer_id)

        ca.search_composers("johann bach")   # multi-token also works
    """
    tokens = [t for t in query.lower().split() if t]
    if not tokens:
        return []

    initials = {t[0].upper() for t in tokens if t[0].upper() in string.ascii_uppercase}
    seen: Dict[int, Composer] = {}
    for letter in sorted(initials):
        for c in get_composers_by_letter(letter):
            seen.setdefault(c.composer_id, c)

    phrase = query.lower().strip()

    def matches(c: Composer) -> bool:
        hay = f"{c.name} {c.display_name}".lower()
        return all(t in hay for t in tokens)

    def score(c: Composer) -> tuple:
        name = c.display_name.lower()
        # tier 0: exact name; 1: full-phrase substring; 2: tokens only.
        # shorter names break ties, so the plain composer beats arrangement
        # ("X / Y") and teacher/pupil composite entries.
        if name == phrase:
            tier = 0
        elif phrase in name:
            tier = 1
        else:
            tier = 2
        # within a tier, more-recorded composers rank first (popularity),
        # then shorter names.
        return (tier, -(c.n_recordings or 0), len(c.name))

    results = sorted((c for c in seen.values() if matches(c)), key=score)
    return results[:limit] if limit else results
