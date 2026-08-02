"""Example 09 — build flat rows for a Hugging Face dataset.

Emits the three join-able tables (composers / works / albums) and writes
a small JSONL sample. See docs/dataset.md for the full column dictionary.

Run::

    python examples/09_build_dataset.py
"""
import pyclassicalarchives as ca
from pyclassicalarchives import dataset

BACH = 2113


def main() -> None:
    # Cheap headline table: list-level composer rows for one initial.
    rows = list(dataset.composer_rows(ca.get_composers_by_letter("A")))
    print(f"composer_rows(A): {len(rows)} rows")
    print("  columns:", list(rows[0].keys()))
    print("  sample :", rows[0])

    # Rich per-composer detail row + nested work/album tables.
    detail = ca.fetch_composer(BACH)
    print("\ncomposer_detail_row:")
    print("  ", dataset.composer_detail_row(detail))

    works = list(dataset.work_rows(detail))
    albums = list(dataset.album_rows(detail))
    print(f"\nwork_rows: {len(works)} (sample: {works[0]})")
    print(f"album_rows: {len(albums)} (sample: {albums[0]})")

    n = dataset.write_jsonl("composers_A_sample.jsonl", rows[:25])
    print(f"\nwrote {n} rows to composers_A_sample.jsonl")
    print("Load it with:  datasets.Dataset.from_json('composers_A_sample.jsonl')")


if __name__ == "__main__":
    main()
