"""Typed dataclass models for pyclassicalarchives.

Every model is a plain :func:`dataclasses.dataclass` with:

- a ``site_id`` property — the canonical Classical Archives identifier;
- a ``url`` property — the canonical web page for the entity;
- ``to_dict()`` — a JSON-serialisable plain ``dict``;
- ``to_external_ids_dict()`` — a dict suitable for ``ExternalIds(extra=...)``
  in metadatarr (see :mod:`pyclassicalarchives._provider`).

The raw API uses terse keys (``n``, ``b``, ``d``, ``nat``, ``f`` …). These
models are the friendly, stable surface — build them with the
``from_api`` classmethods so callers never touch the wire format.
"""
from __future__ import annotations

import dataclasses
import html
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

BASE = "https://www.classicalarchives.com"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r"<[^>]+>")
_LIFE_RE = re.compile(r"\(?\s*([0-9/]+)?\s*-\s*([0-9/]+)?\s*\)?")


def _abs_image(img: Optional[str]) -> Optional[str]:
    """Absolutise a Classical Archives image path."""
    if not img:
        return None
    if img.startswith("http"):
        return img
    return f"{BASE}{img}"


def _display_name(listed: str) -> str:
    """Turn a surname-first listing (``"Bach, Johann Sebastian"``) into a
    natural ``"Johann Sebastian Bach"``."""
    if ", " in listed:
        last, first = listed.split(", ", 1)
        return f"{first} {last}".strip()
    return listed


def _strip_html(chunks: Any) -> Optional[str]:
    """Flatten a list/str of HTML bio fragments into plain text."""
    if not chunks:
        return None
    if isinstance(chunks, str):
        chunks = [chunks]
    text = " ".join(_TAG_RE.sub("", c or "") for c in chunks)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _flatten_works(nodes: Any, path: Optional[List[str]] = None):
    """Recursively yield leaf works (``t == 'w'``) from the nested
    category/work tree, carrying the category path that led to each.

    The works tree is arbitrarily deep: category nodes (``t == 'c'``) hold
    ``children`` that are either sub-categories or leaf works.
    """
    from pyclassicalarchives.types import Work  # local import: defined below
    path = path or []
    for node in nodes or []:
        children = node.get("children")
        if node.get("t") == "w" or (children is None and "id" in node):
            yield Work.from_api(node, category_path=path)
        elif children is not None:
            yield from _flatten_works(children, path + [node.get("title", "")])


def _parse_life(life: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """Parse a ``"(1685-1750)"`` / ``"(1947/02/15-)"`` lifedate string into
    ``(birth, death)``."""
    if not life:
        return None, None
    m = _LIFE_RE.search(life)
    if not m:
        return None, None
    return (m.group(1) or None), (m.group(2) or None)


# ---------------------------------------------------------------------------
# Composer (list-level)
# ---------------------------------------------------------------------------

@dataclass
class Composer:
    """A composer as it appears in a listing (notable / by-letter / must-know).

    This is the lightweight shape returned by the list endpoints. Call
    :func:`pyclassicalarchives.fetch_composer` with :attr:`composer_id` to
    obtain the full :class:`ComposerDetail` (bio, albums, works).

    Example::

        import pyclassicalarchives as ca

        for c in ca.get_notable_composers()[:3]:
            print(c.composer_id, c.display_name, c.country, c.birth, c.death)
            print(c.url)
    """

    composer_id: int
    name: str                          # surname-first, e.g. "Bach, Johann Sebastian"
    country: Optional[str] = None      # ISO 3166-1 alpha-3, e.g. "DEU"
    birth: Optional[str] = None        # year or ISO-ish date, e.g. "1685"
    death: Optional[str] = None
    flourished: Optional[int] = None   # site sort key (approx. activity year)
    image: Optional[str] = None
    n_recordings: Optional[int] = None
    n_performers: Optional[int] = None
    n_albums: Optional[int] = None
    notable: bool = False
    must_know: bool = False

    @classmethod
    def from_api(cls, d: Dict[str, Any], *, notable: bool = False,
                 must_know: bool = False) -> "Composer":
        """Build from a ``composer_list_*`` / ``composer_list_all`` element."""
        return cls(
            composer_id=int(d["id"]),
            name=d.get("n", ""),
            country=d.get("nat"),
            birth=d.get("b"),
            death=d.get("d"),
            flourished=d.get("f"),
            image=_abs_image(d.get("img")),
            n_recordings=d.get("rec"),
            n_performers=d.get("prf"),
            n_albums=d.get("alb"),
            notable=notable,
            must_know=must_know,
        )

    @property
    def site_id(self) -> str:
        """Canonical Classical Archives composer id (as a string)."""
        return str(self.composer_id)

    @property
    def display_name(self) -> str:
        """Natural ``"First Last"`` form of :attr:`name`."""
        return _display_name(self.name)

    @property
    def url(self) -> str:
        """Canonical composer web page."""
        return f"{BASE}/composer/{self.composer_id}.html"

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["display_name"] = self.display_name
        d["url"] = self.url
        return d

    def to_external_ids_dict(self) -> Dict[str, str]:
        """Dict for ``ExternalIds(extra=...)`` — see :mod:`._provider`."""
        return {
            "classicalarchives_composer": self.site_id,
            "classicalarchives_url": self.url,
        }


# ---------------------------------------------------------------------------
# Album
# ---------------------------------------------------------------------------

@dataclass
class Album:
    """An album featuring a composer's works (from a composer page).

    Example::

        detail = ca.fetch_composer(2113)   # J. S. Bach
        a = detail.albums[0]
        print(a.title, a.label, a.release_date, a.duration, "seconds")
    """

    album_id: int
    title: str
    label: Optional[str] = None
    release_date: Optional[str] = None
    upc: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    n_discs: Optional[int] = None
    n_tracks: Optional[int] = None
    duration: Optional[int] = None     # total seconds
    performers: List[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, a: Dict[str, Any]) -> "Album":
        img = a.get("image") or {}
        return cls(
            album_id=int(a["album_id"]),
            title=a.get("album_title", ""),
            label=a.get("label_name"),
            release_date=a.get("release_date"),
            upc=a.get("album_upc"),
            price=a.get("album_price"),
            image=img.get("url") if isinstance(img, dict) else None,
            n_discs=a.get("n_dsk"),
            n_tracks=a.get("n_trk"),
            duration=a.get("dur"),
            performers=list(a.get("performers") or []),
        )

    @property
    def site_id(self) -> str:
        return str(self.album_id)

    @property
    def url(self) -> str:
        return f"{BASE}/album/{self.album_id}.html"

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["url"] = self.url
        return d

    def to_external_ids_dict(self) -> Dict[str, str]:
        return {
            "classicalarchives_album": self.site_id,
            "classicalarchives_url": self.url,
        }


# ---------------------------------------------------------------------------
# Work
# ---------------------------------------------------------------------------

@dataclass
class Work:
    """A musical work by a composer (from a composer page).

    Works are grouped by :attr:`category` on the site (e.g. ``"Stage Works"``,
    ``"Orchestral"``). The flat list on :class:`ComposerDetail` carries the
    category each work belongs to.

    Example::

        detail = ca.fetch_composer(2113)
        for w in detail.works[:5]:
            print(w.category, "—", w.title, f"({w.n_recordings} recordings)")
    """

    work_id: int
    title: str
    category: Optional[str] = None        # top-level category, e.g. "Vocal Works"
    category_path: List[str] = field(default_factory=list)  # full root→leaf path
    n_recordings: Optional[int] = None
    n_performers: Optional[int] = None
    n_albums: Optional[int] = None

    @classmethod
    def from_api(cls, w: Dict[str, Any], category_path: Optional[List[str]] = None) -> "Work":
        path = list(category_path or [])
        return cls(
            work_id=int(w["id"]),
            title=w.get("title", ""),
            category=path[0] if path else None,
            category_path=path,
            n_recordings=w.get("rec"),
            n_performers=w.get("prf"),
            n_albums=w.get("alb"),
        )

    @property
    def site_id(self) -> str:
        return str(self.work_id)

    @property
    def url(self) -> str:
        return f"{BASE}/work/{self.work_id}.html"

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["url"] = self.url
        return d

    def to_external_ids_dict(self) -> Dict[str, str]:
        return {
            "classicalarchives_work": self.site_id,
            "classicalarchives_url": self.url,
        }


# ---------------------------------------------------------------------------
# ComposerDetail (full page)
# ---------------------------------------------------------------------------

@dataclass
class ComposerDetail:
    """Full composer page: biography, period, albums and works.

    Obtain via :func:`pyclassicalarchives.fetch_composer`.

    Example::

        detail = ca.fetch_composer(2113)        # J. S. Bach
        print(detail.display_name, detail.life, detail.period)
        print(detail.bio[:120])
        print(len(detail.albums), "albums,", len(detail.works), "works")
    """

    composer_id: int
    name: str                          # display form, e.g. "Johann Sebastian Bach"
    country: Optional[str] = None
    life: Optional[str] = None         # raw lifedates, e.g. "(1685-1750)"
    birth: Optional[str] = None        # parsed from `life`
    death: Optional[str] = None
    period: Optional[str] = None       # e.g. "Baroque"
    image: Optional[str] = None
    bio: Optional[str] = None          # plain-text biography
    bio_html: List[str] = field(default_factory=list)
    radio_id: Optional[str] = None
    notable: bool = False
    must_know: bool = False
    n_recordings: Optional[int] = None
    n_performers: Optional[int] = None
    n_albums: Optional[int] = None
    albums: List[Album] = field(default_factory=list)
    works: List[Work] = field(default_factory=list)

    @classmethod
    def from_api(cls, d: Dict[str, Any]) -> "ComposerDetail":
        life = d.get("d")
        birth, death = _parse_life(life)
        bio_html = d.get("bio") or []
        if isinstance(bio_html, str):
            bio_html = [bio_html]

        works = list(_flatten_works(d.get("works", [])))
        albums = [Album.from_api(a) for a in d.get("albums", [])]

        return cls(
            composer_id=int(d["id"]),
            name=d.get("name", ""),
            country=d.get("n"),
            life=life,
            birth=birth,
            death=death,
            period=d.get("p"),
            image=_abs_image(d.get("img")),
            bio=_strip_html(bio_html),
            bio_html=list(bio_html),
            radio_id=d.get("radio_id"),
            notable=bool(d.get("notable", False)),
            must_know=bool(d.get("mkn", False)),
            n_recordings=d.get("rec"),
            n_performers=d.get("prf"),
            n_albums=d.get("alb"),
            albums=albums,
            works=works,
        )

    @property
    def site_id(self) -> str:
        return str(self.composer_id)

    @property
    def display_name(self) -> str:
        return self.name

    @property
    def url(self) -> str:
        return f"{BASE}/composer/{self.composer_id}.html"

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d["url"] = self.url
        return d

    def to_external_ids_dict(self) -> Dict[str, str]:
        return {
            "classicalarchives_composer": self.site_id,
            "classicalarchives_url": self.url,
        }
