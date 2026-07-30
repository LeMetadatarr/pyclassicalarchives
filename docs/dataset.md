# Building a Hugging Face dataset

Classical Archives' data is a **graph** (composer to works, composer to
albums). A good HF dataset is **flat tables**. `pyclassicalarchives.dataset`
emits three row streams that share `composer_id` as a join key, so you can
publish them as three configs of one dataset, or as three separate datasets.

## What columns and rows?

### Table 1: `composers` (the headline table)

**One row per composer.** This is the table most people load. It comes in
two grades:

*Cheap* (`composer_rows`, from the by-letter listings, no per-composer fetch):

| Column | Type | Example |
|---|---|---|
| `composer_id` | int64 | `2113` |
| `name` | string | `"Bach, Johann Sebastian"` |
| `display_name` | string | `"Johann Sebastian Bach"` |
| `country` | string | `"DEU"` (ISO 3166-1 alpha-3) |
| `birth` | string | `"1685"` |
| `death` | string | `"1750"` |
| `flourished` | int64 | `3363` (site sort key) |
| `image_url` | string | cover URL or null |
| `url` | string | canonical page |
| `n_recordings` | int64 | `69996` |
| `n_performers` | int64 | `21196` |
| `n_albums` | int64 | `4009` |
| `notable` | bool | `false` |
| `must_know` | bool | `false` |

*Rich* (`composer_detail_row`, one HTTP fetch per composer, adds the good NLP
columns): adds `life`, `period` (`"Baroque"`), `bio` (a substantial
plain-text biography, the headline text feature), `radio_id`, and the counts
`n_works_listed` / `n_albums_listed`.

**Rows:** roughly tens of thousands of composers (the full A-Z catalogue).

### Table 2: `works`

**One row per work**, from `work_rows(detail)`:

| Column | Type | Notes |
|---|---|---|
| `work_id` | int64 | canonical id |
| `composer_id` | int64 | **join key** |
| `composer_name` | string | denormalized for convenience |
| `title` | string | `"Cantata No.1: Wie schön leuchtet…"` |
| `category` | string | top-level group, e.g. `"Vocal Works"` |
| `n_recordings` | int64 | popularity signal |
| `n_performers` | int64 | |
| `n_albums` | int64 | |
| `url` | string | |

**Rows:** hundreds to a couple thousand per prolific composer. J. S. Bach
alone has about 1,250 leaf works.

### Table 3: `albums`

**One row per album**, from `album_rows(detail)`:

| Column | Type | Notes |
|---|---|---|
| `album_id` | int64 | canonical id |
| `composer_id` | int64 | **join key** |
| `composer_name` | string | |
| `title` | string | |
| `label` | string | issuing label |
| `release_date` | string | `YYYY-MM-DD` |
| `upc` | string | barcode |
| `price` | float64 | |
| `n_discs` | int64 | |
| `n_tracks` | int64 | |
| `duration_seconds` | int64 | |
| `image_url` | string | |
| `url` | string | |

## Why this shape

- **`composer_id` everywhere** makes the three tables joinable and gives
  every row a stable primary or foreign key, the canonical id, not a row
  index.
- **Counts** (`n_recordings`, `n_performers`, `n_albums`) are ready-made
  popularity and relevance signals for ranking or weighting.
- **`bio`** is the one substantial free-text field, the natural target for
  text tasks such as classification by period, retrieval, or summarization.
- **`period` and `country`** are clean categorical labels.
- Consistent `None`/null for missing values keeps the Arrow schema stable.

## Recipe

```python
from pyclassicalarchives import dataset
import pyclassicalarchives as ca

# 1. Cheap headline table for one initial (no per-composer fetch)
rows = list(dataset.composer_rows(ca.get_composers_by_letter("A")))

# 2. Or stream the whole catalogue to JSONL
n = dataset.write_jsonl("composers.jsonl", dataset.build_dataset())          # cheap rows
# ...or the rich variant (slow: one request per composer, throttle yourself)
# dataset.write_jsonl("composers_rich.jsonl", dataset.build_dataset(with_detail=True))

# 3. Works + albums tables for a set of composers
import itertools
works, albums = [], []
for c in itertools.islice(ca.iter_all_composers(), 100):
    detail = ca.fetch_composer(c.composer_id)
    works.extend(dataset.work_rows(detail))
    albums.extend(dataset.album_rows(detail))
dataset.write_jsonl("works.jsonl", works)
dataset.write_jsonl("albums.jsonl", albums)
```

## Load into Hugging Face `datasets`

```python
from datasets import Dataset, DatasetDict

composers = Dataset.from_json("composers.jsonl")
works     = Dataset.from_json("works.jsonl")
albums    = Dataset.from_json("albums.jsonl")

ds = DatasetDict({"composers": composers, "works": works, "albums": albums})
ds.push_to_hub("your-org/classical-archives")
```

> Be polite when you scrape the whole catalogue for the rich, works, or
> albums tables. `robots.txt` asks for a 1-second crawl delay. See
> [advanced.md](advanced.md).

See `examples/10_build_dataset.py` for a runnable version.

---
[← Canonical ids](canonical_ids.md) · [Home](../README.md)
