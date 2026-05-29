"""Public surface is importable and stable."""
import pyclassicalarchives as ca


def test_version():
    assert isinstance(ca.__version__, str)


def test_exports():
    for name in [
        "Album", "Composer", "ComposerDetail", "Work", "ComposerNotFound",
        "fetch_composer", "get_all_composers", "get_composers_by_letter",
        "get_must_know_composers", "get_notable_composers",
        "iter_all_composers", "search_composers",
    ]:
        assert hasattr(ca, name), name
