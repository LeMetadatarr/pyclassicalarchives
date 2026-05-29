"""Example 06 — a composer's albums and works.

Run::

    python examples/06_albums_and_works.py
"""
import pyclassicalarchives as ca

BACH = 2113


def main() -> None:
    detail = ca.fetch_composer(BACH)

    print(f"Top albums for {detail.display_name}:")
    for a in detail.albums[:5]:
        mins = (a.duration or 0) // 60
        print(f"  [{a.album_id}] {a.title[:48]:<48} {a.label or '':<14} "
              f"{a.n_tracks or '?'} trk  {mins}m")
        print(f"        {a.url}")

    print(f"\nWorks grouped by category (first per category):")
    seen = set()
    for w in detail.works:
        if w.category in seen:
            continue
        seen.add(w.category)
        print(f"  {w.category:<22} — {w.title}  ({w.n_recordings} recordings)")
        if len(seen) >= 8:
            break


if __name__ == "__main__":
    main()
