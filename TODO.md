# TODO — pyclassicalarchives

## Open issues

None open.

## Gaps

- [ ] No CI workflows. Add gh-automations reusable workflows (`build-tests`,
      `coverage`, `license-check`, `release_workflow`, `publish_stable`)
      referenced at `@dev`.
- [ ] No `.github/` directory.
- [ ] No linter/type checker configured (mypy/ruff) despite fully annotated source.
- [ ] No live/VCR smoke test — the suite is purely offline fixture parsing.
- [ ] `search_composers` only scans the initials present in the query, so a
      query that omits the surname's initial misses the composer. A
      whole-catalogue fallback (opt-in, expensive) could be added.

## Possible enhancements

- [ ] Work- and album-level detail are embedded in the composer page only;
      if dedicated endpoints surface, add `fetch_work` / `fetch_album`.
- [ ] `to_mediavocab()` helpers building `Work`/`Release`/`Entity` objects
      (current integration is via the resolver provider + `to_external_ids_dict`).

## Code TODOs

None found.
