"""Example 08 — canonical ids for dedup and cross-referencing.

Every model exposes ``site_id`` (the stable Classical Archives id) and
``to_external_ids_dict()`` (the dict you hand to metadatarr's
``ExternalIds(extra=...)``). These are the keys you dedup and join on.

Run::

    python examples/08_canonical_ids.py
"""
import pyclassicalarchives as ca


def main() -> None:
    bach = ca.search_composers("johann sebastian bach", limit=1)[0]
    print("Composer canonical id:", bach.site_id)
    print("Composer external ids:", bach.to_external_ids_dict())

    detail = ca.fetch_composer(bach.composer_id)
    if detail.albums:
        a = detail.albums[0]
        print("\nAlbum canonical id:  ", a.site_id)
        print("Album external ids:  ", a.to_external_ids_dict())
    if detail.works:
        w = detail.works[0]
        print("\nWork canonical id:   ", w.site_id)
        print("Work external ids:   ", w.to_external_ids_dict())


if __name__ == "__main__":
    main()
