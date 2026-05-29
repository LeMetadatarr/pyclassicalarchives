"""Example 04 — fetch a full composer page.

A single ``fetch_composer`` call returns the bio, period, lifedates,
and the composer's albums and works.

Run::

    python examples/04_fetch_composer.py
"""
import pyclassicalarchives as ca

BACH = 2113


def main() -> None:
    detail = ca.fetch_composer(BACH)
    print(detail.display_name)
    print(f"  lifedates : {detail.life}  (birth={detail.birth}, death={detail.death})")
    print(f"  period    : {detail.period}")
    print(f"  country   : {detail.country}")
    print(f"  catalogue : {detail.n_recordings} recordings, "
          f"{detail.n_performers} performers, {detail.n_albums} albums")
    print(f"  page      : {detail.url}")
    print(f"  bio       : {(detail.bio or '')[:140]}")
    print(f"\n  {len(detail.works)} works listed, {len(detail.albums)} albums listed")

    print("\nMissing composer raises ComposerNotFound:")
    try:
        ca.fetch_composer(999_999_999)
    except ca.ComposerNotFound as e:
        print(f"  {e}")


if __name__ == "__main__":
    main()
