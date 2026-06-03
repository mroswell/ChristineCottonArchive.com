# CLAUDE.md — Christine Cotton Archive & Website

## What this project is

A preservation archive and (in progress) public website for the life's work of **Christine Cotton** (b. 27 April 1970), a French biostatistician and founder of the contract research organization **Statitec**. After ~25 years running clinical trials for the pharmaceutical industry, she became a whistleblower who produced a detailed **Good Clinical Practice (GCP) critique of Pfizer/BioNTech's COVID-19 vaccine clinical trial (C4591001)**, published a book, testified to the French Parliament's OPECST, and gave many interviews.

**Christine Cotton is deceased.** Her website (christinecotton.com) and the documents it hosts may not stay online. The mission of this project is to **preserve her work and make it permanently accessible and searchable**, in both the original French and in English.

Treat this as an act of preservation and faithful presentation: keep provenance, do not editorialize her conclusions, and keep both the original-language source (PDFs) and readable text/translations.

## Current state (what already exists)

- **`pdfs/`** — 13 original source PDFs (her reports, book, CV, OPECST slides, plus two cited source docs and the Pfizer protocol). **These are the canonical preservation artifacts and are kept locally**, but most are **git-ignored, not published** (see "Copyright & publishing policy" below). Only the CV and OPECST presentation PDFs are tracked/served.
- **`archive/pages/`** — every page of christinecotton.com, French originals, navigation stripped.
- **`archive/pages_en/`** — English translations of the French-only pages (home, criticism, legal notice, book sources). *These translations were produced for this archive, not by Cotton.*
- **`archive/documents/`** — readable text of her key works:
  - Clean text (text-based PDFs): English CV; 414-page English expertise (2024-12-30); 432-page French expertise (2025-01-27); OPECST presentation (French + an archive English translation); 54-page English update (2023-08-08); 36-page McCullough slides (2023-07-15); **the English book "The Trial Was Almost Perfect" (213 pp)**.
  - OCR text (scanned PDFs), in `*_OCR.md`: 2022 English & French expertise (105/111 pp) and the 2021/2022 summaries. OCR used the **English** Tesseract engine (the French language pack could not be installed offline), so the French scans have imperfect accents — see notes in each file.
- **`archive/sources/`** — external documents she cited (currently the Rose & Crawford VAERS analysis).
- **`catalog/`** — the navigable front-end:
  - `index.html` — master, searchable table of contents (filter by **document type**, **tag** [grouped into categories], and **language**).
  - `interviews.html` / `interviews.md` — her 18 video interviews (titles + links; transcripts NOT yet done).
  - `external_links.html` — 231 external links/sources she cited, categorized + searchable.
  - `french_english_matching.md` — pairs each French work with its English counterpart.
- **`README.md`** — human-facing overview.

## Repository structure

```
Cotton/
├── CLAUDE.md                 # this file
├── README.md                 # human overview
├── TODO.md                   # project backlog
├── catalog/                  # the website front-end (static HTML + reports)
│   ├── index.html            # master searchable table of contents
│   ├── interviews.html       # 18 interview videos
│   ├── external_links.html   # 231 cited external links
│   └── french_english_matching.md
├── archive/
│   ├── pages/                # FR site pages (markdown)
│   ├── pages_en/             # EN translations of FR-only pages
│   ├── documents/            # full-text + OCR text of her works
│   └── sources/              # external cited documents
├── pdfs/                     # 13 ORIGINAL source PDFs (preserve + serve)
└── ocr_work/                 # OCR scratch (gitignored)
```

## Conventions & important facts

- **French original + English** for everything where possible. Always note whether an English version is **Cotton's own** (her reports and book) or an **archive translation** (site pages, OPECST). See `catalog/french_english_matching.md`.
- **Never discard a PDF.** They are the preservation copy and are higher-fidelity than the extracted text (which can mangle tables/figures).
- **Provenance:** every derived text file links back to its source PDF / URL in a header. Keep this.
- **Document dating:** her flagship report exists as English (2024-12-30, 414 pp) and French (2025-01-27, 432 pp); the 2022 versions are earlier editions.
- **Copyright & publishing policy (decided by the owner).** Her GCP reports carry explicit copyright notices; the book is offered free but is also excluded by choice. So the following are **kept locally for preservation but git-ignored (not published in this repo)**, and the website links to the originals instead:
  - Her expertise reports (414-pg EN, 432-pg FR, 2022 EN/FR), the summaries, the 54-pg update, the McCullough slides, and the book — the site links to **her own christinecotton.com URLs**.
  - The two third-party documents (Pfizer C4591001 protocol, Rose & Crawford VAERS paper) — the site links to the **original publishers** (the protocol → NEJM supplementary; the VAERS paper → the regulations.gov docket CDC-2021-0089).
  - **Only her CV and the OPECST presentation** (no copyright notice) plus the site pages/translations are published in the repo.
  - The exclusions are enforced in `.gitignore`. If you add new copyrighted documents, git-ignore them and link to the source rather than committing them. Do not republish the git-ignored PDFs/text without the estate's permission.

## Building / running the site

The current front-end is **plain static HTML/CSS/JS** (no build step, no dependencies). To preview locally:

```bash
cd catalog && python3 -m http.server 8000   # then open http://localhost:8000
```

Target deployment is **GitHub Pages** (static hosting), which matches the owner's preference. Because the large copyrighted PDFs are git-ignored (see policy above), the **tracked** repo is small — only the CV and OPECST PDFs remain (~5 MB combined). Git LFS is therefore optional now; set it up only if you later add large tracked binaries (e.g., the critics-page images). GitHub Pages' 100 MB per-file cap is not a concern for the tracked files.

If the site is ever rebuilt in **React/Vite** (not required — static is fine and preferred), provide full install instructions to the owner: `npm create vite@latest`, `npm install`, `npm run dev`, and a GitHub Pages deploy via `npm run build` + a `gh-pages` action. Default to static HTML unless there's a clear reason to add a framework.

## Proposed site navigation (menu)

A suggested information architecture for the site. It loosely mirrors her own menu (Mon Livre / Interviews / Investigations et Expertises / CV / Auditions OPECST / Critiques / Me Soutenir) but reframes it as a bilingual preservation archive.

**Primary navigation**
1. **Home** — who Christine Cotton was, the preservation mission, and a short guide to the archive (source: a new page built from `archive/pages_en/index_EN.md` + a short bio).
2. **Expertise & Reports** — the heart of her work: the GCP critique of the Pfizer/BioNTech C4591001 trial (414-pg EN / 432-pg FR reports, the 2022 versions, the summaries, and the 2023 update). Documents link to the originals per the copyright policy (see `catalog/source_urls.md`). Include the **OPECST testimony** (2022) and the **McCullough slides** (2023) here or as sub-items.
3. **The Book** — "The Trial Was Almost Perfect" (EN) / "Tous vaccinés, tous protégés ?" (FR): about the book, the free English ebook (her Support page), and booksellers.
4. **Interviews** — her 18 video appearances (`catalog/interviews.html`).
5. **CV & Biography** — her career as a biostatistician and Statitec founder (`archive/documents/CV_Christine_Cotton_EN.md`).
6. **Sources & Links** — the 231 external sources she cited (`catalog/external_links.html`) plus the cited third-party documents (Pfizer protocol → NEJM; Rose & Crawford VAERS paper → regulations.gov).
7. **Archive Index** — the full searchable table of contents (`catalog/index.html`), filterable by type / tag / language.

**Utility / footer**
- **About this Archive** — preservation purpose, who maintains it, attribution, and a contact for corrections/takedown.
- **Criticism** — her "Critiques de mon travail" page and responses (`archive/pages_en/critics_EN.md`); includes the ~27 critics screenshots once downloaded.
- **Legal notice** — Mentions légales (`archive/pages_en/mentions_legales_EN.md`).
- **Language toggle EN / FR** — everything exists in both; let visitors switch.
- **Search** — a search box (header or on the Archive Index page).

## Owner preferences

- Prefers **Python notebooks, shell scripts, or GitHub Pages**. Keep code in those forms when possible.
- If a solution ends up in **React, give detailed step-by-step install instructions.**
- Communication: **concise and direct.**

## Known constraints (learned while building this)

- Downloading binaries directly was firewalled in the assistant's environment; the PDFs here were downloaded by the owner via a browser. The owner can fetch anything still-missing the same way.
- **Interview transcripts are not done.** YouTube/Dailymotion serve captions only to a real (JS-running) browser. Route: a browser (e.g., the Claude in Chrome extension) opening each video's transcript panel, or a captions/transcript download. 18 videos, listed in `catalog/interviews.html`.
- Image-only scanned PDFs were OCR'd locally (Tesseract); the French scans need a real French OCR pass or human proofreading for accent accuracy.
```
