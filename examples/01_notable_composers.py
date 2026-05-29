"""Example 01 — the curated 'notable composers' list.

Run::

    python examples/01_notable_composers.py
"""
import pyclassicalarchives as ca


def main() -> None:
    notable = ca.get_notable_composers()
    print(f"{len(notable)} notable composers\n")
    for c in notable[:10]:
        years = f"{c.birth or '?'}–{c.death or ''}".rstrip("–")
        print(f"  [{c.composer_id:>6}] {c.display_name:<28} {c.country or '   '}  {years}")
    print("\nFirst composer as a dict:")
    print(notable[0].to_dict())


if __name__ == "__main__":
    main()
