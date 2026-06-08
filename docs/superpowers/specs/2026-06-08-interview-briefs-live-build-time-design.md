# Port In Brief panels + cited sources to the live Jekyll site (build-time, searchable)

**Date:** 2026-06-08
**Status:** approved (owner asked me to decide; going with Approach B as designed)

## Problem

The In Brief panels, research follow-ups, and book-cited sources exist only under
`catalog/`, which `_config.yml` **excludes** from the Jekyll build. The live site
(`christinecottonarchive.com`, built from `en/` + `fr/`) therefore shows none of it.
The live `/en/interviews/` page is a simple client-rendered video grid.

## Goal

Show the In Brief content — pull quote, key statements, documents cited, and research
follow-ups with their **clickable cited book sources (+ archived fallbacks)** — on the
live `/en/interviews/` and `/fr/interviews/` pages, rendered **at build time** so the
content is in the static HTML and indexed by Pagefind (searchable). Follow-ups are
**read-only** on the public site (no checkboxes / localStorage). Bilingual, driven by
`page.lang`.

## Approach: build-time (Liquid) rendering

### Data (canonical home becomes `_data/`)
- `_data/interviews.json` — the 18 videos (id, platform, title, author, url, thumb),
  moved out of the inline JS array in `_includes/interviews-script.html`.
- `_data/briefs.json` — In Brief content, relocated from `catalog/briefs.json`
  (structure `{ briefs: { <videoId>: {...} } }`).
- `_data/followup_sources.json` — the 160 validated cited sources, relocated from
  `catalog/book_followup_sources.data.json` (array of `{ videoId, todos:[{id, sources[]}] }`).
- Generator scripts (`catalog/build_followup_refs.py` et al.) repointed to write the
  sources file into `_data/`.
- `catalog/` is left frozen (legacy, not built); plan to retire it later. Accepted
  drift risk until then.

### Rendering
- New include `_includes/interview-briefs.html`: given a video object + `page.lang`,
  renders a read-only `<details class="brief">` "In Brief" panel: header
  (date · interviewer · outlet), pull quote, key statements (with timestamp deep-links),
  documents cited, and research follow-ups as read-only bullets. For each follow-up,
  join its cited sources by matching `followup_sources[videoId].todos[id]` via Liquid
  `where` filters, and render each source as `document` → link to `url`, plus an
  `archived` link to `archive_url` when present, with a footnote chip.
- `_includes/interviews-script.html`: stop building cards in JS. A Liquid loop over
  `site.data.interviews` emits each card (thumbnail, title, author, watch/transcript
  links) with `{% include interview-briefs.html %}` inside. The remaining JS only
  **filters** the static cards by the search box (show/hide) and updates the count.
- `_includes/interviews-styles.html`: add styles for `.brief`, `.todo-sources`,
  `.fn-num`, `.arch-link`, etc. (ported from catalog).

### Bilingual
- `page.lang` (`en` on `/en/...`, `fr` on `/fr/...`) selects en/fr fields from the
  brief data (which already carries both). New UI strings added to
  `_data/interviews_labels_{en,fr}.yml` (e.g. `in_brief`, `sources_label`,
  `follow_ups_label`, `documents_label`, `key_statements_label`).

### Searchability
- Because cards + briefs render to static HTML at build time, Pagefind (run on `_site/`
  in the deploy workflow) indexes the brief text and cited-source labels → the site
  search box finds them.

## Out of scope
- Standalone follow-ups page and per-brief pages (catalog had these) — not ported now.
- Interactive checkboxes / localStorage progress tracking (public site is read-only).
- Retiring `catalog/` (separate later cleanup).

## Verification
- Build locally (`bundle exec jekyll build`), screenshot `_site/en/interviews/` and
  `_site/fr/interviews/` (headless Chrome), confirm In Brief panels + cited-source
  links render in both languages. Do NOT push until owner approves the screenshots.

## Files
- New: `_data/interviews.json`, `_data/briefs.json`, `_data/followup_sources.json`,
  `_includes/interview-briefs.html`.
- Edited: `_includes/interviews-script.html`, `_includes/interviews-styles.html`,
  `_data/interviews_labels_en.yml`, `_data/interviews_labels_fr.yml`.
- Repointed: `catalog/build_followup_refs.py` (write sources to `_data/`).
