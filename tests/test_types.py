"""Offline parsing tests against representative API fixtures."""
from pyclassicalarchives.types import (
    Album,
    Composer,
    ComposerDetail,
    Work,
    _flatten_works,
    _parse_life,
)

LIST_ITEM = {
    "id": 2113, "n": "Bach, Johann Sebastian", "f": 3363, "b": "1685",
    "d": "1750", "nat": "DEU", "img": "/images/artists_cma/wp/2113.jpg",
    "rec": 69996, "prf": 21196, "alb": 4009,
}

PAGE = {
    "id": 2113, "name": "Johann Sebastian Bach", "notable": True, "mkn": True,
    "d": "(1685-1750)", "p": "Baroque", "n": "DEU",
    "img": "/images/artists_cma/wp/2113.jpg", "radio_id": "composer:2113",
    "rec": 69996, "prf": 21196, "alb": 4009,
    "bio": ["<p>Son of Johann Ambrosius Bach &#8212; organist.</p>"],
    "albums": [{
        "album_id": 71964, "album_title": "Sacred Choral", "label_name": "Capriccio",
        "release_date": "2013-03-26", "album_upc": "845221071558", "album_price": 49.99,
        "image": {"url": "https://cdn.prs.net/x.jpg", "width": 100, "height": 100},
        "n_dsk": 5, "n_trk": 100, "dur": 21977, "performers": [],
    }],
    "works": [{
        "t": "c", "id": 1, "title": "Vocal Works", "children": [
            {"t": "c", "id": 2, "title": "Cantatas", "children": [
                {"t": "w", "id": 962, "title": "Cantata No.1", "rec": 51, "prf": 15, "alb": 15},
            ]},
            {"t": "w", "id": 9, "title": "Mass in B minor", "rec": 200, "prf": 30, "alb": 40},
        ],
    }],
}


def test_composer_from_list():
    c = Composer.from_api(LIST_ITEM, notable=True)
    assert c.composer_id == 2113
    assert c.name == "Bach, Johann Sebastian"
    assert c.display_name == "Johann Sebastian Bach"
    assert c.country == "DEU" and c.birth == "1685" and c.death == "1750"
    assert c.flourished == 3363
    assert c.image.endswith("/2113.jpg") and c.image.startswith("http")
    assert c.notable is True
    assert c.site_id == "2113"
    assert c.url == "https://www.classicalarchives.com/composer/2113.html"
    assert c.to_external_ids_dict()["classicalarchives_composer"] == "2113"


def test_parse_life():
    assert _parse_life("(1685-1750)") == ("1685", "1750")
    assert _parse_life("(1947/02/15-)") == ("1947/02/15", None)
    assert _parse_life(None) == (None, None)


def test_flatten_works_is_recursive():
    works = list(_flatten_works(PAGE["works"]))
    titles = {w.title for w in works}
    assert titles == {"Cantata No.1", "Mass in B minor"}     # only leaf works
    deep = next(w for w in works if w.title == "Cantata No.1")
    assert deep.category == "Vocal Works"
    assert deep.category_path == ["Vocal Works", "Cantatas"]
    assert deep.n_recordings == 51


def test_composer_detail_from_page():
    d = ComposerDetail.from_api(PAGE)
    assert d.name == "Johann Sebastian Bach"
    assert d.life == "(1685-1750)" and d.birth == "1685" and d.death == "1750"
    assert d.period == "Baroque" and d.country == "DEU"
    assert d.must_know is True and d.notable is True
    assert "organist" in d.bio and "&#8212;" not in d.bio  # entities unescaped
    assert len(d.albums) == 1 and isinstance(d.albums[0], Album)
    assert len(d.works) == 2 and all(isinstance(w, Work) for w in d.works)
    assert d.to_dict()["url"].endswith("/composer/2113.html")


def test_album_and_work_ids():
    d = ComposerDetail.from_api(PAGE)
    a = d.albums[0]
    assert a.site_id == "71964" and a.duration == 21977 and a.n_tracks == 100
    assert a.to_external_ids_dict()["classicalarchives_album"] == "71964"
    w = d.works[0]
    assert w.url.startswith("https://www.classicalarchives.com/work/")
