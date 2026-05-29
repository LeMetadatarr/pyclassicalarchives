"""Example 02 — the curated 'must know' composers.

These come back as terse id/name/image triples, so the resulting
``Composer`` objects carry only id, name and image.

Run::

    python examples/02_must_know.py
"""
import pyclassicalarchives as ca


def main() -> None:
    must_know = ca.get_must_know_composers()
    print(f"{len(must_know)} must-know composers\n")
    for c in must_know[:15]:
        print(f"  [{c.composer_id:>6}] {c.display_name}")
        if c.image:
            print(f"           {c.image}")


if __name__ == "__main__":
    main()
