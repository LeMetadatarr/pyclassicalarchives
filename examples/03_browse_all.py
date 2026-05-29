"""Example 03 — browse the full A–Z catalogue.

``get_composers_by_letter`` returns one initial; ``iter_all_composers``
streams the whole alphabet lazily.

Run::

    python examples/03_browse_all.py
"""
import itertools

import pyclassicalarchives as ca


def main() -> None:
    bs = ca.get_composers_by_letter("B")
    print(f"{len(bs)} composers whose surname starts with B")
    print("e.g.", ", ".join(c.name for c in bs[:5]), "...\n")

    print("Streaming the first 20 of the whole catalogue:")
    for c in itertools.islice(ca.iter_all_composers(), 20):
        print(f"  {c.name:<32} ({c.country or '?'})")


if __name__ == "__main__":
    main()
