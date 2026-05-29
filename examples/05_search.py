"""Example 05 — search composers by name.

There is no server-side search endpoint; ``search_composers`` builds one
client-side from the by-letter listings. Both surname-first and natural
order work, and multi-token queries are matched as an AND of tokens.

Run::

    python examples/05_search.py
"""
import pyclassicalarchives as ca


def main() -> None:
    for query in ["mozart", "johann sebastian bach", "beethoven"]:
        hits = ca.search_composers(query, limit=3)
        print(f"{query!r} -> {len(hits)} hit(s)")
        for c in hits:
            print(f"    [{c.composer_id}] {c.display_name}  ({c.country}, {c.birth}-{c.death})")
        print()


if __name__ == "__main__":
    main()
