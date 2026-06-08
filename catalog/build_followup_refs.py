#!/usr/bin/env python3
"""Build a markdown document mapping each research follow-up (follow_ups.html /
briefs.json) to the matching passages in Christine Cotton's English book.

Input : the workflow result JSON (result.groups[]) + briefs.json (for titles/metadata).
Output: catalog/book_followup_references.md
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Merged, deduplicated, order-corrected workflow output (18 groups / 72 follow-ups).
WF = os.path.join(ROOT, 'catalog', 'book_followup_refs.data.json')

groups = json.load(open(WF))
briefs = json.load(open(os.path.join(ROOT, 'catalog', 'briefs.json')))['briefs']

# interview titles/authors from follow_ups.html videos[] mirror -> reuse briefs metadata
# map videoId -> (outlet, interviewer, pull_quote) from briefs; titles come from interviews.html
# Pull titles out of interviews.html videos[] if available; else from briefs outlet.
import re
titles = {}
ih = open(os.path.join(ROOT, 'catalog', 'interviews.html')).read()
for m in re.finditer(r'\{id:"([^"]+)",\s*platform:"[^"]*",\s*title:"((?:[^"\\]|\\.)*)",\s*author:"((?:[^"\\]|\\.)*)"', ih):
    titles[m.group(1)] = (m.group(2), m.group(3))

# index todo metadata by id
todo_meta = {}
for vid, b in briefs.items():
    for t in b.get('todos', []):
        todo_meta[t['id']] = t

# underlying source documents Cotton cites in the book (footnotes -> URLs), by todo id
sources_by_id = {}
sdata = json.load(open(os.path.join(ROOT, 'catalog', 'book_followup_sources.data.json')))
for g in sdata:
    for t in g['todos']:
        sources_by_id[t['id']] = t['sources']

total_todos = sum(len(g['findings']) for g in groups)
todos_with_refs = sum(1 for g in groups for f in g['findings'] if f['found'])
total_refs = sum(len(f['references']) for g in groups for f in g['findings'])
total_sources = sum(len(v) for v in sources_by_id.values())
todos_with_sources = sum(1 for v in sources_by_id.values() if v)

out = []
out.append("# Book references & cited sources for the research follow-ups\n")
out.append(
    "*Auto-generated cross-reference.* For every open research follow-up in "
    "[`follow_ups.html`](./follow_ups.html) (the 72 questions Christine Cotton raises across her 18 "
    "interviews), this document gives two things: (1) **where she discusses it** in her English book — "
    "*The Trial Was Almost Perfect* (20 October 2024, 213 pp) — with verbatim quotes, and (2) the "
    "**underlying source documents she cites** there, resolved from the book's footnotes to the actual "
    "publisher/URL (FDA briefings, the C4591001 protocol, EMA EPARs, the Moderna SEC 10-K, HAS/OPECST "
    "reports, etc.). Quotes are verbatim from "
    "[`archive/documents/Book_The_Trial_was_Almost_Perfect_EN.md`](../archive/documents/Book_The_Trial_was_Almost_Perfect_EN.md); "
    "page numbers are the book's own printed markers.\n"
)
out.append(
    f"\n**{todos_with_refs} of {total_todos}** follow-ups are addressed in the book "
    f"({total_refs} passages cited), resolving to **{total_sources} underlying source documents** "
    f"across {todos_with_sources} follow-ups. Items marked *Not found in book* are follow-ups the book does not cover.\n"
)
out.append("\n---\n")

# table of contents
out.append("\n## Contents\n")
for g in groups:
    vid = g['videoId']
    title, author = titles.get(vid, (briefs.get(vid, {}).get('outlet', vid), ''))
    n_found = sum(1 for f in g['findings'] if f['found'])
    anchor = vid.lower()
    out.append(f"- [{title} — {author}](#{anchor}) — {n_found}/{len(g['findings'])} addressed\n")

out.append("\n---\n")

for g in groups:
    vid = g['videoId']
    title, author = titles.get(vid, (briefs.get(vid, {}).get('outlet', vid), ''))
    out.append(f"\n## {title}\n")
    out.append(f"<a id=\"{vid.lower()}\"></a>\n")
    meta = []
    if author:
        meta.append(author)
    meta.append(f"[watch ▶](https://www.youtube.com/watch?v={vid})" if len(vid) == 11 else f"[watch ▶](https://www.dailymotion.com/video/{vid})")
    meta.append(f"[brief](./brief.html?id={vid})")
    out.append("*" + " · ".join(meta) + "*\n")

    for f in g['findings']:
        tm = todo_meta.get(f['id'], {})
        ts = tm.get('timestamp', '')
        q = (tm.get('text', {}) or {}).get('en', '')
        out.append(f"\n### {q}\n")
        sub = []
        if ts:
            sub.append(f"⏱ {ts}")
        docs = tm.get('documents', [])
        if docs:
            sub.append("cited: " + "; ".join(docs))
        if sub:
            out.append("> " + " · ".join(sub) + "\n")

        out.append(f"\n**Summary:** {f['summary']}\n")
        if not f['found'] or not f['references']:
            out.append("\n*Not found in book.*\n")
        else:
            out.append("\n**Where she discusses it in the book:**\n")
            for r in f['references']:
                page = r.get('page', 'unknown') or 'unknown'
                quote = r['quote'].strip()
                qlines = quote.split('\n')
                bq = "\n".join("> " + ln for ln in qlines)
                out.append(f"\n- **{page}** — {r['relevance']}\n")
                out.append(f"\n{bq}\n")

        # underlying source documents she cites (footnotes -> URLs)
        srcs = sources_by_id.get(f['id'], [])
        if srcs:
            out.append("\n**Underlying sources she cites:**\n\n")
            out.append("| Footnote | Source document | Cited for | Link |\n")
            out.append("|---|---|---|---|\n")
            for s in srcs:
                fn = s.get('footnote', '') or '—'
                if fn.lower() == 'none':
                    fn = '— (named in text)'
                doc = (s.get('document', '') or '').replace('|', '\\|')
                cf = (s.get('cited_for', '') or '').replace('|', '\\|')
                url = s.get('url', '') or ''
                link = f"[link]({url})" if url else "—"
                arch = s.get('archive_url', '')
                if arch:
                    link += f" · [archived]({arch})"
                out.append(f"| {fn} | {doc} | {cf} | {link} |\n")
    out.append("\n---\n")

dest = os.path.join(ROOT, 'catalog', 'book_followup_references.md')
open(dest, 'w').write("".join(out))
print("wrote", dest)
print("todos:", total_todos, "addressed:", todos_with_refs, "passages:", total_refs)
