# TODO — Christine Cotton Archive & Website

Status legend: `[ ]` to do · `[~]` partially done · `[x]` done

## Done so far
- [x] Mirror all christinecotton.com pages (French) + English translations of French-only pages
- [x] Capture full text of her text-based works (414-pg EN & 432-pg FR expertise, CV, OPECST FR+EN, 54-pg update, McCullough slides)
- [x] Capture the English **book** "The Trial Was Almost Perfect" (213 pp) as text
- [x] OCR the 4 scanned PDFs (2022 EN/FR expertise, 2021/2022 summaries)
- [x] Searchable master catalog (`catalog/index.html`) with type/tag/language filters
- [x] Interview catalog of 18 videos (titles + links)
- [x] External links/sources page (231 links, categorized + searchable)
- [x] French↔English matching report
- [x] Preserve all 13 original PDFs in `pdfs/`

## 1. Repo & hosting setup
- [ ] `git init`; create the GitHub repo
- [x] Copyright decision: the copyrighted reports/summaries/book + third-party docs are git-ignored (kept locally, not published); site links to originals. See `.gitignore` and CLAUDE.md
- [ ] Git LFS is now **optional** (only the CV + OPECST PDFs, ~5 MB, remain tracked). Set it up only if you later commit large binaries (e.g., critics-page images): `git lfs install && git lfs track "pdfs/**"`
- [ ] Decide hosting: GitHub Pages (static). Confirm repo size/LFS bandwidth is acceptable, or host the largest PDFs (Pfizer protocol, 46 MB) elsewhere and link out
- [ ] Local preview: `cd catalog && python3 -m http.server 8000`

### Custom domain — christinecottonarchive.com (purchased)
- [ ] In the GitHub repo: **Settings → Pages → Custom domain**, enter `christinecottonarchive.com` and Save. This commits a `CNAME` file to the repo containing that domain (don't delete it — a plain static build can overwrite it, so keep the file)
- [ ] At the domain registrar's DNS, point the **apex** domain `christinecottonarchive.com` at GitHub Pages with four `A` records → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` (and/or the matching `AAAA` IPv6 records). Verify GitHub's current IPs in their Pages docs before entering — they can change
- [ ] Add a `www` subdomain as a `CNAME` record → `<your-github-username>.github.io`
- [ ] Back in Settings → Pages, wait for the DNS check to pass, then tick **Enforce HTTPS** (GitHub auto-provisions the TLS certificate; can take up to ~24 h)
- [ ] Test both `https://christinecottonarchive.com` and `https://www.christinecottonarchive.com` resolve and redirect sensibly to one canonical version

## 2. Build the website
- [ ] Build the **site navigation/menu** per the "Proposed site navigation" in CLAUDE.md: Home · Expertise & Reports · The Book · Interviews · CV & Biography · Sources & Links · Archive Index, with footer items (About this Archive, Criticism, Legal notice), an EN/FR language toggle, and search
- [ ] Decide the home page: a proper **Home** landing page (intro + mission + guide), with `catalog/index.html` linked as the "Archive Index" rather than itself being the front door
- [ ] For the **non-copyrighted** items only (CV, OPECST), add a "Download PDF" link to the local file in `pdfs/`. Copyrighted items intentionally link only to the original (her site / NEJM / regulations.gov) — do not add local download links for those
- [ ] Render the `.md` reports (matching report, book, documents) as readable HTML pages, or convert key ones to HTML
- [ ] Mobile/responsive pass + basic accessibility (alt text, contrast, headings)
- [ ] Deploy to GitHub Pages; document the deploy command/workflow

## 3. Content still to capture
- [ ] **Interview transcripts (18 videos)** — needs a real browser (Claude in Chrome) to open each transcript panel, or a captions download. Then translate FR→EN. Videos listed in `catalog/interviews.html`
- [ ] **Translate the French OCR** to clean English: `archive/documents/Summary_2021-02-16_FR_OCR.md` (21 pp, quick) and `Expertise_2022-02-28_FR_OCR.md` (111 pp — note: largely redundant with the captured 432-pg French / 414-pg English reports)
- [ ] **Re-OCR the French scans with a real French engine** (install `tesseract-ocr-fra`, or use a cloud OCR) for correct accents; proofread
- [ ] Optional: extract the **Pfizer protocol** text (`pdfs/m5351-…-protocol-final.pdf`, 3,790 pp, text-based) if you want it searchable on-site — it's large
- [ ] **Download the ~27 "Critiques de mon travail" screenshots** — embedded images on her critics page (https://christinecotton.com/critics/1.png … /25.png, /26.jpg, /27.jpg). We have the page text but not these images; grab them via browser into `pdfs/` or an `images/` folder
- [ ] Download the site's cosmetic images for visual fidelity: `book_cover.jpg`, `book_cover_en.jpg`, `book_back_en.jpg`, `cv_preview.png`, `web_preview.png`, and the OPECST thumbnail
- [ ] Optional: capture her social feeds (Twitter/X @StatChrisCotton, Telegram) if you want those preserved too

## 4. Quality & integrity
- [ ] Proofread the auto-extracted text against the PDFs (tables/figures extract imperfectly), especially the flagship reports
- [ ] Spot-check the English translations of the site pages for fidelity
- [ ] Verify every catalog link (local + live) resolves

## 5. Legal & attribution
- [x] Copyright handling decided: copyrighted reports/summaries + the book + third-party docs are git-ignored and the site links to originals (her site / NEJM / regulations.gov). Still worth confirming with the **estate** if you ever want to republish her works in full
- [ ] Add an "About this archive" page: who Christine was, the preservation purpose, attribution, and a contact for corrections/takedown
- [ ] Add clear source attribution for third-party documents (e.g., the Rose & Crawford VAERS paper, the Pfizer protocol)

## 6. Nice-to-haves
- [ ] Full-text search across all documents (e.g., a prebuilt index with Lunr.js, or Pagefind for static sites)
- [ ] A short biography / timeline of her career and the C4591001 critique
- [ ] Set up a scheduled check that the live christinecotton.com is still up (alert if it goes down)
