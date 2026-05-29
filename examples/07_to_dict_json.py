"""Example 07 — serialise to plain dicts / JSON.

Every model has ``to_dict()``. The dataclasses are JSON-friendly, so a
whole composer page (with nested albums and works) round-trips cleanly.

Run::

    python examples/07_to_dict_json.py
"""
import json

import pyclassicalarchives as ca

BACH = 2113


def main() -> None:
    detail = ca.fetch_composer(BACH)
    d = detail.to_dict()

    # Trim the nested lists so the print stays readable
    d["albums"] = d["albums"][:1]
    d["works"] = d["works"][:1]
    d["bio_html"] = ["..."]
    print(json.dumps(d, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
