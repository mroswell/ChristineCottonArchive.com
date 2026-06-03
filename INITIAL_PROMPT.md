# Initial prompt for the Claude Code session

Copy everything in the block below into Claude Code (run from inside the `Cotton/` folder) to start the website project.

---

I'm building a preservation website for the work of **Christine Cotton**, a French biostatistician (founder of the CRO Statitec) who became a whistleblower with a Good Clinical Practice critique of Pfizer's COVID-19 vaccine trial. She has died, and her site (christinecotton.com) may not stay online — the goal is to **preserve her work and make it permanently accessible and searchable, in French and English**, as a static site I can host on **GitHub Pages**.

Please start by reading **CLAUDE.md** (project context, structure, conventions, constraints) and **TODO.md** (the backlog). Then confirm you understand the current state before changing anything.

The archive already exists in this repo:
- `pdfs/` — 13 original source PDFs (the canonical preservation copies — never delete these).
- `archive/` — readable text and translations of her pages and documents (incl. her 414-page English report and her 213-page English book).
- `catalog/index.html` — a working static, searchable table of contents (filter by type / tag / language), plus `interviews.html`, `external_links.html`, and `french_english_matching.md`.

What I want, in order:
1. **Set up the repo for hosting**: initialize git, configure **Git LFS for `pdfs/`** (they total ~280 MB; the Pfizer protocol is ~46 MB), and get a local preview working (`python3 -m http.server`).
2. **Turn `catalog/` into the site front-end**: make `index.html` the home page, add download links from each catalog entry to its local PDF in `pdfs/` (and keep the link to the live original as a fallback), and make the interview and links pages reachable from the home page. Keep it **plain static HTML/CSS/JS — no framework** unless we hit a real need (if we ever do use React, give me full install/deploy instructions).
3. **Deploy to GitHub Pages** and document the deploy steps.

Constraints to respect: keep both the French original and the English version of everything, and always note whether an English version is *Christine's own* or an *archive translation* (see `french_english_matching.md`). Keep provenance headers in the text files. Don't editorialize her conclusions — this is preservation, not commentary.

Work in small, reviewable steps and check with me before large restructures. I prefer concise, direct explanations.

---
