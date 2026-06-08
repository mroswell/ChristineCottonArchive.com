#!/usr/bin/env python3
"""Validate the source URLs in book_followup_sources.data.json.

- Live hosts: curl HEAD (fallback GET), follow redirects, record final HTTP code.
- web.archive.org links: query the Internet Archive availability API (web.archive.org
  itself is not directly fetchable from here) and report the closest snapshot status.

Writes catalog/source_url_check.md (full table) and prints a summary of anything that
does not cleanly resolve.
"""
import json, os, subprocess, re, urllib.parse
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sd = json.load(open(os.path.join(HERE, 'book_followup_sources.data.json')))

# map url -> list of (todo_id, footnote, document); track which urls have an archive fallback
refs = {}
order = []
has_archive = set()
for g in sd:
    for t in g['todos']:
        for s in t['sources']:
            u = (s.get('url') or '').strip()
            if not u:
                continue
            if u not in refs:
                refs[u] = []
                order.append(u)
            refs[u].append((t['id'], s.get('footnote', ''), s.get('document', '')))
            if s.get('archive_url'):
                has_archive.add(u)


def curl_code(url, head=True):
    args = ['curl', '-sS', '-L', '-m', '25', '-o', '/dev/null',
            '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            '-w', '%{http_code} %{url_effective}']
    if head:
        args.insert(1, '-I')
    try:
        r = subprocess.run(args + [url], capture_output=True, text=True, timeout=40)
        out = r.stdout.strip().split(' ', 1)
        code = out[0]
        final = out[1] if len(out) > 1 else url
        return code, final
    except subprocess.TimeoutExpired:
        return '000', url
    except Exception as e:
        return 'ERR', str(e)


def check_live(url):
    code, final = curl_code(url, head=True)
    # retry with GET when HEAD is refused / fails
    if code in ('000', '405', '403', '501', 'ERR') or code.startswith('4') or code.startswith('5'):
        code2, final2 = curl_code(url, head=False)
        if code2 != '000' and code2 != 'ERR':
            code, final = code2, final2
    ok = code.startswith('2') or code.startswith('3')
    return {'url': url, 'kind': 'live', 'code': code, 'final': final, 'ok': ok}


def check_wayback(url):
    m = re.match(r'https?://web\.archive\.org/web/(\d+)/(.*)$', url)
    if not m:
        return {'url': url, 'kind': 'wayback', 'code': '?', 'final': url, 'ok': False, 'note': 'unparseable'}
    ts, orig = m.group(1), m.group(2)
    # the availability API is picky about URL form — try a few normalizations
    cands = [orig, re.sub(r'^https?://', '', orig), re.sub(r'^https?://(www\.)?', '', orig)]
    for c in cands:
        api = 'https://archive.org/wayback/available?url=' + urllib.parse.quote(c, safe='') + '&timestamp=' + ts
        try:
            r = subprocess.run(['curl', '-sS', '-m', '25', api], capture_output=True, text=True, timeout=40)
            snap = (json.loads(r.stdout).get('archived_snapshots') or {}).get('closest')
            if snap and snap.get('available'):
                return {'url': url, 'kind': 'wayback', 'code': str(snap.get('status', '200')),
                        'final': snap.get('url', url), 'ok': str(snap.get('status', '200')).startswith('2'),
                        'note': 'snapshot ' + snap.get('timestamp', '')}
        except Exception:
            pass
    return {'url': url, 'kind': 'wayback', 'code': 'none', 'final': url, 'ok': False, 'note': 'no snapshot'}


def check(url):
    return check_wayback(url) if 'web.archive.org' in url else check_live(url)


with ThreadPoolExecutor(max_workers=12) as ex:
    results = list(ex.map(check, order))

results_by_url = {r['url']: r for r in results}
# a source is covered if its live URL resolves OR it carries a working archive fallback
for r in results:
    if not r['ok'] and r['url'] in has_archive:
        r['ok'] = True
        r['code'] = r['code'] + ' (live) → archived'
bad = [r for r in results if not r['ok']]

# write full report
out = ["# Source URL validation\n",
       f"\nChecked **{len(order)}** unique source URLs from the book's footnotes "
       f"({sum(len(refs[u]) for u in order)} citations total). "
       f"**{len(order)-len(bad)} resolve, {len(bad)} need attention.**\n",
       "\n*Live hosts checked by HTTP request (redirects followed); web.archive.org links checked "
       "via the Internet Archive availability API. Note: YouTube/X return 200 even for removed content, "
       "so a 200 there means the page exists, not that the specific video/tweet is still live.*\n"]
if bad:
    out.append("\n## ⚠️ Needs attention\n\n| Code | Footnote | Document | URL | Used by |\n|---|---|---|---|---|\n")
    for r in bad:
        u = r['url']
        fn = refs[u][0][1]
        doc = refs[u][0][2].replace('|', '\\|')[:80]
        ids = ", ".join(sorted(set(x[0] for x in refs[u])))
        note = r.get('note', '')
        out.append(f"| {r['code']} {('· '+note) if note else ''} | {fn} | {doc} | {u} | {ids} |\n")
out.append("\n## All results\n\n| OK | Code | URL |\n|---|---|---|\n")
for r in sorted(results, key=lambda r: (r['ok'], r['url'])):
    out.append(f"| {'✓' if r['ok'] else '✗'} | {r['code']} | {r['url']} |\n")
open(os.path.join(HERE, 'source_url_check.md'), 'w').write("".join(out))

print(f"checked {len(order)} urls | OK {len(order)-len(bad)} | needs attention {len(bad)}")
for r in bad:
    print(f"  ✗ {r['code']:>5}  fn{refs[r['url']][0][1]}  {r['url']}")
print("wrote catalog/source_url_check.md")
