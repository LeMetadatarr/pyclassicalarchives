# API reference

Everything below is re-exported from the top-level `pyclassicalarchives`
package (aliased `ca` throughout).

## Functions

### `get_notable_composers() -> List[Composer]`
The curated "notable composers" list. Each result has `notable=True`.

### `get_must_know_composers() -> List[Composer]`
The curated "must know" list. The endpoint returns terse `[id, name, image]`
triples, so only `composer_id`, `name`, and `image` are populated. Each
result has `must_know=True`.

### `get_composers_by_letter(letter: str) -> List[Composer]`
Every composer whose **surname** begins with `letter` (a single A-Z letter).
Raises `ValueError` for non-letters.

### `iter_all_composers(letters: str | None = None) -> Iterator[Composer]`
Lazily iterates the full catalogue, one initial at a time. Pass `letters`
(e.g. `"ABC"`) to restrict the range. The catalogue holds tens of thousands
of composers.

### `get_all_composers(letters: str | None = None) -> List[Composer]`
The eager version of `iter_all_composers`. The result list is large. Prefer
the iterator.

### `fetch_composer(composer_id: int) -> ComposerDetail`
The full composer page: biography, period, lifedates, plus albums and works.
Raises **`ComposerNotFound`** if the id does not resolve.

### `search_composers(query: str, limit: int | None = None) -> List[Composer]`
A client-side search built on the by-letter listings. It fetches the
listings for the initials in `query`, keeps composers whose name contains
every query token, and ranks by:

1. exact `display_name` match, then full-phrase substring, then token-only.
2. **recording count** (popularity) descending.
3. shorter name.

Surname-first (`"Bach"`) and natural order (`"Johann Sebastian Bach"`) both
work. `limit` caps the result count.

## Models

All models are `@dataclass`es. Shared interface:

- **`site_id -> str`**: the canonical Classical Archives id, as a string.
- **`url -> str`**: the canonical web page.
- **`to_dict() -> dict`**: JSON-serializable. Properties (`url`,
  `display_name`) are folded in.
- **`to_external_ids_dict() -> dict[str, str]`**: keys for metadatarr's
  `ExternalIds(extra=...)`.

### `Composer` (list-level)

| Field | Type | Notes |
|---|---|---|
| `composer_id` | `int` | canonical id |
| `name` | `str` | surname-first, e.g. `"Bach, Johann Sebastian"` |
| `country` | `str \| None` | ISO 3166-1 **alpha-3**, e.g. `"DEU"` |
| `birth` / `death` | `str \| None` | year or `YYYY/MM/DD` |
| `flourished` | `int \| None` | site sort key (approximate activity) |
| `image` | `str \| None` | absolute cover URL |
| `n_recordings` | `int \| None` | recordings on the site |
| `n_performers` | `int \| None` | distinct performers |
| `n_albums` | `int \| None` | albums featuring the composer |
| `notable` / `must_know` | `bool` | which curated list it came from |

Properties: `site_id`, `display_name` (`"First Last"`), `url`
(`/composer/<id>.html`).

External ids: `{"classicalarchives_composer", "classicalarchives_url"}`.

### `ComposerDetail` (full page)

Adds, beyond the list-level fields:

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | here the **natural** `"First Last"` form |
| `life` | `str \| None` | raw lifedates, e.g. `"(1685-1750)"` |
| `birth` / `death` | `str \| None` | parsed from `life` |
| `period` | `str \| None` | e.g. `"Baroque"`, `"Contemporary"` |
| `bio` | `str \| None` | plain-text biography (HTML stripped, entities decoded) |
| `bio_html` | `List[str]` | the raw HTML fragments |
| `radio_id` | `str \| None` | e.g. `"composer:2113"` |
| `albums` | `List[Album]` | |
| `works` | `List[Work]` | recursively flattened leaf works |

### `Album`

| Field | Type | Notes |
|---|---|---|
| `album_id` | `int` | canonical id |
| `title` | `str` | |
| `label` | `str \| None` | issuing label |
| `release_date` | `str \| None` | `YYYY-MM-DD` |
| `upc` | `str \| None` | barcode |
| `price` | `float \| None` | list price |
| `image` | `str \| None` | cover URL |
| `n_discs` / `n_tracks` | `int \| None` | |
| `duration` | `int \| None` | total **seconds** |
| `performers` | `List[str]` | may be empty |

Properties: `site_id`, `url` (`/album/<id>.html`).
External ids: `{"classicalarchives_album", "classicalarchives_url"}`.

### `Work`

| Field | Type | Notes |
|---|---|---|
| `work_id` | `int` | canonical id |
| `title` | `str` | |
| `category` | `str \| None` | top-level category, e.g. `"Vocal Works"` |
| `category_path` | `List[str]` | full root-to-leaf category path |
| `n_recordings` / `n_performers` / `n_albums` | `int \| None` | |

Properties: `site_id`, `url` (`/work/<id>.html`).
External ids: `{"classicalarchives_work", "classicalarchives_url"}`.

## Exceptions

### `ComposerNotFound`
Raised by `fetch_composer` when the API responds with
`{"error": "Composer does not exist"}`.

## Endpoints used

| Path | Wrapped by |
|---|---|
| `/api/composer_list_notable.json` | `get_notable_composers` |
| `/api/mustknow_composers.json` | `get_must_know_composers` |
| `/api/composer_list_all.json?letter=` | `get_composers_by_letter`, `iter_all_composers`, `search_composers` |
| `/api/composer_page.json?composer_id=` | `fetch_composer` |

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Advanced usage →](advanced.md)
