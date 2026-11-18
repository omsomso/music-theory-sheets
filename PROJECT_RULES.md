# music-theory-sheets project rules

- Change a sheet's content only through its data tables in `src/<sheet>.py`. Never
  hand-edit the generated HTML or PDFs.
- Every sheet keeps its own `validate()`, and its tests plant mistakes that `validate()` must
  catch. Theory facts and fingerings are checked, not trusted.
- Run `make` before committing. Tests and checks must pass, every sheet must render to A4 pages
  with no overflow, and the phone-width check must pass. Look at `build/<sheet>-page-*.png`
  after layout changes; the overflow check can't see content clipped inside a table's scroll
  box.
- `docs/` is committed on purpose: it is the GitHub Pages site (index, each sheet's page and
  PDF). Regenerate it with `make` in the same commit as any content change. `build/` is never
  committed.
- The site is unlisted, not private: keep the noindex tag on every page, and never put
  personal or private material in a sheet or on the index.
- When adding or changing a fingering or fact that isn't standard teaching practice, add its
  source to the README.
- The repository is public. Keep personal details, private links and local paths out of
  committed files and commit messages. Each sheet's private claude.ai artifact URL is in
  `LOCAL.md` (gitignored); after content changes, republish `build/<sheet>.html` to that URL
  and don't create a new artifact.
