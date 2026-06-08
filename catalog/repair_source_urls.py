#!/usr/bin/env python3
"""Repair the source URLs: (1) fix OCR-mangled URLs, (2) attach an `archive_url`
Wayback fallback to any source whose live URL is unreachable (moved or bot-blocked).
Edits book_followup_sources.data.json in place.
"""
import json, os, subprocess, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'book_followup_sources.data.json')
sd = json.load(open(P))

# 1) corrections: substring-in-old -> exact-new
CORRECT = {
    "special-committee-on-COVID-19-pandemic_202210101430-COMMITTEE-COVI":
        "https://multimedia.europarl.europa.eu/en/webstreaming/special-committee-on-covid-19-pandemic_20221010-1430-COMMITTEE-COVI",
    "workshop_20230309-1030COMMITTEE-COVI":
        "https://multimedia.europarl.europa.eu/en/webstreaming/-policy-department-a-workshop_20230309-1030-COMMITTEE-COVI",
    "ten-lessons-from-the-first-two-years-of-COVID19?cid=":
        "https://www.mckinsey.com/industries/healthcare/our-insights/ten-lessons-from-the-first-two-years-of-covid-19",
}
corrected = 0
for g in sd:
    for t in g['todos']:
        for s in t['sources']:
            u = s.get('url', '') or ''
            for needle, new in CORRECT.items():
                if needle in u and u != new:
                    s['url'] = new
                    corrected += 1


def live_ok(url):
    for head in (True, False):
        args = ['curl', '-sS', '-L', '-m', '20', '-o', '/dev/null',
                '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', '-w', '%{http_code}']
        if head:
            args.insert(1, '-I')
        try:
            r = subprocess.run(args + [url], capture_output=True, text=True, timeout=30)
            c = r.stdout.strip()
            if c.startswith('2') or c.startswith('3'):
                return True
        except Exception:
            pass
    return False


def wayback(url):
    for c in (url, url.replace('https://', '').replace('http://', '')):
        api = 'https://archive.org/wayback/available?url=' + urllib.parse.quote(c, safe='')
        try:
            r = subprocess.run(['curl', '-sS', '-m', '20', api], capture_output=True, text=True, timeout=30)
            snap = (json.loads(r.stdout).get('archived_snapshots') or {}).get('closest')
            if snap and snap.get('available') and str(snap.get('status', '')).startswith('2'):
                return snap['url']
        except Exception:
            pass
    return None


# 2) attach archive_url where the live URL is unreachable (skip wayback-native urls)
uniq = {}
for g in sd:
    for t in g['todos']:
        for s in t['sources']:
            u = s.get('url', '') or ''
            if u and 'web.archive.org' not in u:
                uniq.setdefault(u, []).append(s)

attached, no_archive = 0, []
for u, srcs in uniq.items():
    if live_ok(u):
        continue
    wb = wayback(u)
    if wb:
        for s in srcs:
            s['archive_url'] = wb
        attached += 1
    else:
        no_archive.append(u)

json.dump(sd, open(P, 'w'), ensure_ascii=False)
print(f"corrected URLs: {corrected}")
print(f"archive fallbacks attached: {attached}")
print(f"still no archive ({len(no_archive)}):")
for u in no_archive:
    print("   ", u)
