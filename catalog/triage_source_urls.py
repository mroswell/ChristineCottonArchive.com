#!/usr/bin/env python3
"""Second-pass triage of the source URLs that failed the first check.

For each flagged URL:
- Re-test Wayback links with a normalized original URL (strip scheme/www) — the
  availability API is picky about exact form.
- For dead/blocked live links, query the Internet Archive availability API to see
  whether an archived snapshot exists (a usable fallback for the preservation archive).
Classifies each as: LIVE-BLOCKED (bot 403, almost certainly fine), DEAD-BUT-ARCHIVED
(live URL fails but a Wayback copy exists), or DEAD-NO-ARCHIVE (needs a real fix).
"""
import json, os, subprocess, re, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sd = json.load(open(os.path.join(HERE, 'book_followup_sources.data.json')))
refs = {}
for g in sd:
    for t in g['todos']:
        for s in t['sources']:
            u = (s.get('url') or '').strip()
            if u:
                refs.setdefault(u, []).append((t['id'], s.get('footnote', ''), s.get('document', '')))

# the 25 flagged by the first pass
FLAGGED = [
 "https://web.archive.org/web/20210225221652/https://www.vidal.fr/maladies/voies-respiratoires/coronavirus-covid-19/vaccins.html",
 "https://www.sec.gov/Archives/edgar/data/1682852/000168285220000006/moderna10-k12312019.htm",
 "https://www.nejm.org/doi/suppl/10.1056/NEJMoa2034577/suppl_file/nejmoa2034577_protocol.pdf",
 "https://www.bmj.com/content/378/bmj.o1731/rr-2",
 "https://multimedia.europarl.europa.eu/fr/webstreaming/special-committee-on-COVID-19-pandemic_202210101430-COMMITTEE-COVI",
 "https://cdn.pfizer.com/pfizercom/2020-11/C4591001_Clinical_Protocol_Nov2020.pdf",
 "https://www.has-sante.fr/upload/docs/application/pdf/2020-12/strategie_vaccination_COVID_19_place_vaccin_a_arnm_comirnaty_bnt162b2.pdf",
 "https://multimedia.europarl.europa.eu/en/webstreaming/-policy-department-a-workshop_20230309-1030COMMITTEE-COVI",
 "https://www.mckinsey.com/industries/healthcare/our-insights/ten-lessons-from-the-first-two-years-of-COVID19?cid=other-eml-dre-mip-mck&hlkid=ee011309d17944b68fae004742b199ec&hctky=2025206&hdpid=",
 "https://phmpt.org/wp-content/uploads/2023/05/001-Complaint-PHMPT-de-Garay-v.-FDA-2022-10-11.pdf",
 "https://www.mesvaccins.net/textes/20210608_CCNE_ethique_vaccination_COVID_enfants.pdf",
 "https://www.nejm.org/doi/full/10.1056/NEJMoa2034577",
 "https://www.biorxiv.org/content/10.1101/2020.09.08.280818v1.full.pdf",
 "https://cdn.who.int/media/docs/default-source/medicines/regulatory-updates/COVID-19/tech-brief_april-2021_regulation-of-COVID-19-vaccines_synopsis_-aug2020_feb2021.pdf",
 "https://www.ventaviaresearch.com/",
 "https://www.bmj.com/content/375/bmj.n2635",
 "https://www.sciencedirect.com/science/article/abs/pii/S0002937824000632",
 "https://ia902305.us.archive.org/28/items/pfizer-confidential-translated/pfizer-confidential-translated.pdf",
 "https://scdm.org/wp-content/uploads/2021/04/2021-eCF_SCDM-ATR-Industry-Position-Paper-Version-PR1-2.pdf",
 "https://phmpt.org/wp-content/uploads/2023/10/125742_S1_M1_meeting-correspondence.pdf",
 "https://www.fda.gov/media/142749/download",
 "https://www.washingtonpost.com/washington-post-live/2022/03/10/transcript-wp-subscriber-exclusive-albert-bourla-author-moonshot-inside-pfizers-nine-month-race-make-impossible-possible/",
 "https://web.archive.org/web/20201224122112/https://www.ema.europa.eu/en/documents/product-information/comirnaty-epar-product-information_en.pdf",
 "https://www.gov.uk/government/publications/regulatory-approval-of-pfizer-biontech-vaccine-for-COVID-19/summary-public-assessment-report-for-pfizerbiontech-COVID-19-vaccine",
 "https://phmpt.org/",
]


def avail(orig_url):
    """Query IA availability API; try a few normalizations. Return snapshot dict or None."""
    cands = [orig_url]
    s = re.sub(r'^https?://', '', orig_url)
    cands += [s, re.sub(r'^www\.', '', s)]
    for c in cands:
        api = 'https://archive.org/wayback/available?url=' + urllib.parse.quote(c, safe='')
        try:
            r = subprocess.run(['curl', '-sS', '-m', '20', api], capture_output=True, text=True, timeout=30)
            snap = (json.loads(r.stdout).get('archived_snapshots') or {}).get('closest')
            if snap and snap.get('available'):
                return snap
        except Exception:
            pass
    return None


rows = []
for u in FLAGGED:
    m = re.match(r'https?://web\.archive\.org/web/\d+/(.*)$', u)
    if m:  # it's a wayback link — verify the underlying snapshot exists
        snap = avail(m.group(1))
        if snap:
            rows.append(('LIVE-ARCHIVED', u, f"snapshot {snap.get('timestamp')} status {snap.get('status')}", snap.get('url', '')))
        else:
            rows.append(('DEAD-NO-ARCHIVE', u, 'no snapshot found via availability API', ''))
        continue
    # live link that failed: is there an archived copy?
    snap = avail(u)
    if snap:
        rows.append(('DEAD-BUT-ARCHIVED', u, f"archived {snap.get('timestamp')} status {snap.get('status')}", snap.get('url', '')))
    else:
        rows.append(('NO-ARCHIVE', u, 'live check failed AND no snapshot', ''))

order = {'DEAD-NO-ARCHIVE': 0, 'NO-ARCHIVE': 1, 'DEAD-BUT-ARCHIVED': 2, 'LIVE-ARCHIVED': 3}
rows.sort(key=lambda r: order.get(r[0], 9))

for status, u, note, snapurl in rows:
    fn = refs.get(u, [('', '?', '')])[0][1]
    print(f"[{status}] fn{fn}")
    print(f"    {u}")
    print(f"    -> {note}")
    if snapurl:
        print(f"    archive: {snapurl}")
print(f"\ntotals: " + ", ".join(f"{k}={sum(1 for r in rows if r[0]==k)}" for k in order))
