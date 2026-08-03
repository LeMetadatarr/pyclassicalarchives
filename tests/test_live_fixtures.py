"""Tests replayed from real HTTP responses recorded from classicalarchives.com.

Fixtures live under ``tests/fixtures/`` and were captured with a bounded,
one-shot live GET against the real API (see file docstring comments below
for the exact endpoint/params/date). No network access happens at test time:
:func:`pyclassicalarchives.composers.get_json` is monkeypatched to replay
the recorded JSON instead of hitting the network.

Recorded 2026-08-03 from https://www.classicalarchives.com :

- composer_page_46287_small.json  <- GET /api/composer_page.json?composer_id=46287
  (Frank Zabel: a small, real composer page — 1 album, 1 work, empty bio/
  image/country — exercises the empty-field edge cases the big pages hide.)
- composer_page_6220_living.json  <- GET /api/composer_page.json?composer_id=6220
  (John Adams: a living composer, lifedate "(1947/02/15-)" with no death year.)
- composer_page_notfound.json     <- GET /api/composer_page.json?composer_id=999999999
  ({"error": "Composer does not exist"} — the real not-found payload.)
- composer_list_all_Z.json        <- GET /api/composer_list_all.json?letter=Z
- composer_list_notable.json      <- GET /api/composer_list_notable.json
- mustknow_composers.json         <- GET /api/mustknow_composers.json
"""
import json
import os

import pytest

from pyclassicalarchives import composers
from pyclassicalarchives.composers import ComposerNotFound

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def fake_get_json(monkeypatch):
    """Route composers.get_json(path, **params) to a recorded fixture."""
    routes = {}

    def register(path, fixture, **params):
        routes[(path, tuple(sorted(params.items())))] = fixture

    def fake(path, **params):
        key = (path, tuple(sorted(params.items())))
        if key not in routes:
            raise AssertionError(f"unregistered fixture route: {key}")
        return _load(routes[key])

    monkeypatch.setattr(composers, "get_json", fake)
    return register


def test_fetch_composer_small_real_page(fake_get_json):
    fake_get_json("/api/composer_page.json", "composer_page_46287_small.json",
                   composer_id=46287)
    detail = composers.fetch_composer(46287)
    assert detail.composer_id == 46287
    assert detail.display_name == "Frank Zabel"
    assert detail.period == "Contemporary"
    assert detail.image is None          # empty "" img must not become "https://...."
    assert detail.country == ""          # raw "n" passed through as-is (no country listed)
    assert detail.bio is None            # empty bio list normalises to None
    assert len(detail.albums) == 1 and len(detail.works) == 1
    assert detail.works[0].category == "Chamber Works"


def test_fetch_composer_living_no_death(fake_get_json):
    fake_get_json("/api/composer_page.json", "composer_page_6220_living.json",
                   composer_id=6220)
    detail = composers.fetch_composer(6220)
    assert detail.birth == "1947/02/15"
    assert detail.death is None


def test_fetch_composer_not_found_raises(fake_get_json):
    fake_get_json("/api/composer_page.json", "composer_page_notfound.json",
                   composer_id=999999999)
    with pytest.raises(ComposerNotFound):
        composers.fetch_composer(999999999)


def test_get_composers_by_letter_real_page(fake_get_json):
    fake_get_json("/api/composer_list_all.json", "composer_list_all_Z.json",
                   letter="Z")
    result = composers.get_composers_by_letter("Z")
    raw = _load("composer_list_all_Z.json")
    assert len(result) == len(raw) == 190
    # site groups by locale-aware first letter, so a couple of diacritic
    # "Z"-like surnames (e.g. "Żółtowski") sneak into the ASCII "Z" bucket
    assert sum(c.name.upper().startswith("Z") for c in result) >= len(result) - 2


def test_get_notable_composers_real_page(fake_get_json):
    fake_get_json("/api/composer_list_notable.json", "composer_list_notable.json")
    result = composers.get_notable_composers()
    raw = _load("composer_list_notable.json")
    assert len(result) == len(raw)
    assert all(c.notable for c in result)


def test_get_must_know_composers_real_page(fake_get_json):
    fake_get_json("/api/mustknow_composers.json", "mustknow_composers.json")
    result = composers.get_must_know_composers()
    raw = _load("mustknow_composers.json")
    assert len(result) == len(raw)
    assert all(c.must_know for c in result)
    # terse [id, name, img] triple only carries id/name/image
    assert result[0].composer_id == raw[0][0]
    assert result[0].name == raw[0][1]


# ---------------------------------------------------------------------------
# regression tests for bugs found and fixed during this pass
# ---------------------------------------------------------------------------

def test_to_dict_nested_albums_and_works_carry_url(fake_get_json):
    """Bug: ComposerDetail.to_dict() used dataclasses.asdict() directly, so
    nested Album/Work dicts lost their `url` (and any other @property-derived
    field) even though Album.to_dict()/Work.to_dict() add it when called
    standalone. metadatarr consumes these nested dicts, so a missing `url`
    silently drops the canonical link."""
    fake_get_json("/api/composer_page.json", "composer_page_46287_small.json",
                   composer_id=46287)
    detail = composers.fetch_composer(46287)
    d = detail.to_dict()
    assert d["albums"][0]["url"].startswith("https://www.classicalarchives.com/album/")
    assert d["works"][0]["url"].startswith("https://www.classicalarchives.com/work/")


def test_letter_validation_rejects_empty_string():
    """Bug: `"" not in string.ascii_uppercase` is False (empty string is a
    substring of everything in Python), so an empty/blank `letter` silently
    bypassed validation instead of raising ValueError."""
    with pytest.raises(ValueError):
        composers.get_composers_by_letter("")
    with pytest.raises(ValueError):
        composers.get_composers_by_letter("   ")


def test_search_composers_limit_zero_returns_empty(fake_get_json, monkeypatch):
    """Bug: `results[:limit] if limit else results` treated limit=0 as
    falsy, so `search_composers(q, limit=0)` returned every match instead
    of zero, contradicting the documented "cap the number of results"."""
    raw = _load("composer_list_all_Z.json")
    monkeypatch.setattr(composers, "get_composers_by_letter", lambda letter: [
        composers.Composer.from_api(c) for c in raw
    ])
    results = composers.search_composers("z", limit=0)
    assert results == []
