"""Dataset row builders produce flat, stable, join-able rows."""
from pyclassicalarchives import dataset
from pyclassicalarchives.types import Composer, ComposerDetail
from tests.test_types import LIST_ITEM, PAGE


def test_composer_rows_columns():
    rows = list(dataset.composer_rows([Composer.from_api(LIST_ITEM)]))
    assert len(rows) == 1
    row = rows[0]
    assert row["composer_id"] == 2113
    assert row["display_name"] == "Johann Sebastian Bach"
    assert set(row) >= {"composer_id", "name", "country", "birth", "death",
                        "n_recordings", "url", "notable", "must_know"}


def test_work_and_album_rows_carry_composer():
    d = ComposerDetail.from_api(PAGE)
    for r in dataset.work_rows(d):
        assert r["composer_id"] == 2113
        assert r["composer_name"] == "Johann Sebastian Bach"
    for r in dataset.album_rows(d):
        assert r["composer_id"] == 2113
        assert "duration_seconds" in r


def test_write_jsonl(tmp_path):
    rows = list(dataset.composer_rows([Composer.from_api(LIST_ITEM)]))
    path = tmp_path / "out.jsonl"
    n = dataset.write_jsonl(str(path), rows)
    assert n == 1
    assert path.read_text().count("\n") == 1
