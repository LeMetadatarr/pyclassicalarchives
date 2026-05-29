"""Build flat, tabular rows from Classical Archives data for datasets.

The site's data is a graph (composer → albums, composer → works). For a
Hugging Face dataset you want flat tables. This module emits three row
streams that share ``composer_id`` as a join key:

- :func:`composer_rows`  — one row per composer (the headline table)
- :func:`work_rows`      — one row per work, carrying its composer
- :func:`album_rows`     — one row per album, carrying its composer

Every row is a plain JSON-serialisable ``dict`` with stable column names
and consistent types (``None`` for missing values). Feed them straight to
``datasets.Dataset.from_list(list(rows))`` or stream to JSONL with
:func:`write_jsonl`.

See ``docs/dataset.md`` for the column dictionary and a full recipe.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Iterator

from pyclassicalarchives.composers import fetch_composer, iter_all_composers
from pyclassicalarchives.types import Composer, ComposerDetail


def composer_rows(composers: Iterable[Composer]) -> Iterator[Dict[str, Any]]:
    """Yield one flat row per :class:`Composer` (list-level fields only)."""
    for c in composers:
        yield {
            "composer_id": c.composer_id,
            "name": c.name,
            "display_name": c.display_name,
            "country": c.country,
            "birth": c.birth,
            "death": c.death,
            "flourished": c.flourished,
            "image_url": c.image,
            "url": c.url,
            "n_recordings": c.n_recordings,
            "n_performers": c.n_performers,
            "n_albums": c.n_albums,
            "notable": c.notable,
            "must_know": c.must_know,
        }


def composer_detail_row(detail: ComposerDetail) -> Dict[str, Any]:
    """Yield a single rich row for a fetched :class:`ComposerDetail`.

    Includes biography, period and parsed lifedates that the list-level
    rows do not carry.
    """
    return {
        "composer_id": detail.composer_id,
        "name": detail.name,
        "country": detail.country,
        "life": detail.life,
        "birth": detail.birth,
        "death": detail.death,
        "period": detail.period,
        "image_url": detail.image,
        "url": detail.url,
        "bio": detail.bio,
        "radio_id": detail.radio_id,
        "notable": detail.notable,
        "must_know": detail.must_know,
        "n_recordings": detail.n_recordings,
        "n_performers": detail.n_performers,
        "n_albums": detail.n_albums,
        "n_works_listed": len(detail.works),
        "n_albums_listed": len(detail.albums),
    }


def work_rows(detail: ComposerDetail) -> Iterator[Dict[str, Any]]:
    """Yield one row per work on a composer page."""
    for w in detail.works:
        yield {
            "work_id": w.work_id,
            "composer_id": detail.composer_id,
            "composer_name": detail.name,
            "title": w.title,
            "category": w.category,
            "n_recordings": w.n_recordings,
            "n_performers": w.n_performers,
            "n_albums": w.n_albums,
            "url": w.url,
        }


def album_rows(detail: ComposerDetail) -> Iterator[Dict[str, Any]]:
    """Yield one row per album on a composer page."""
    for a in detail.albums:
        yield {
            "album_id": a.album_id,
            "composer_id": detail.composer_id,
            "composer_name": detail.name,
            "title": a.title,
            "label": a.label,
            "release_date": a.release_date,
            "upc": a.upc,
            "price": a.price,
            "n_discs": a.n_discs,
            "n_tracks": a.n_tracks,
            "duration_seconds": a.duration,
            "image_url": a.image,
            "url": a.url,
        }


def build_dataset(
    letters: str | None = None,
    *,
    with_detail: bool = False,
) -> Iterator[Dict[str, Any]]:
    """Stream composer rows for the whole catalogue (or a subset of initials).

    Args:
        letters:     Restrict to these initials, e.g. ``"ABC"``.
        with_detail: When ``True``, fetch each composer page and emit the
                     richer :func:`composer_detail_row` (bio, period). This
                     is one HTTP request per composer — slow for the full
                     catalogue. When ``False`` (default), emit the cheap
                     list-level :func:`composer_rows`.

    Example::

        from pyclassicalarchives.dataset import build_dataset, write_jsonl
        write_jsonl("composers_A.jsonl", build_dataset("A"))
    """
    if with_detail:
        for c in iter_all_composers(letters):
            yield composer_detail_row(fetch_composer(c.composer_id))
    else:
        yield from composer_rows(iter_all_composers(letters))


def write_jsonl(path: str, rows: Iterable[Dict[str, Any]]) -> int:
    """Write *rows* to *path* as JSON Lines; return the count written."""
    n = 0
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n
