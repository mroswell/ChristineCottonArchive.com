# Transcript cleanup notes

Working notes about the 18 interview transcripts under
[`archive/transcripts/`](archive/transcripts/) — what's been done, what's
known to still be wrong, and how to do another cleanup pass without
re-running the whole whisperX pipeline.

The 18 interviews live as `<video-id>_FR.md` (the diarized French
auto-transcript) and `<video-id>_EN.md` (the opus-mt English
translation). Both versions inherit the same Whisper artifacts because
the EN side was machine-translated from the FR side, so name fixes
apply to both files in lockstep.

## Naming convention in the speaker labels

- **First mention** of each speaker in a file: full name —
  `**Christine Cotton [00:01]**`, `**Pierre-Yves Rougeyron [00:06]**`,
  `**Michèle Rivasi [00:06]**`, `**Didier Maïsto [00:53]**`, etc.
- **Subsequent mentions** in the same file: surname only — `**Cotton
  [01:44]**`, `**Rougeyron [08:10]**`, `**Rivasi [00:30]**`, `**Maïsto
  [01:02]**`.
- **Generic roles**: French labels in FR files, English in EN files.
  In FR: `Animateur`, `Co-animateur`, `Auditeur`, `Indicatif`,
  `Jingle`, `Député`, `Commissaire`, `Intervenant`, `(inaudible)`.
  In EN: `Host`, `Co-host`, `Caller`, `Station ID`, `Bumper`, `MP`,
  `Commissioner`, `Speaker`, `(unclear)`.

## Body-text fixes already applied (chronological)

| Commit | What it fixed | Count |
|---|---|---|
| `b66be2c` | `Coton` → `Cotton` (her own surname) | 111 |
| `b66be2c` | `Berkoff` / `Verkoff` → `Bercoff` (André Bercoff) | 10 |
| `b66be2c` | `Venner` → `Wonner` (Martine Wonner) | 8 |
| `b66be2c` | `Michel/Michelle Rivasi` → `Michèle Rivasi` | 4 |
| `b66be2c` | `VAER` → `VAERS` | 2 |
| `b66be2c` | `biotech` → `BioNTech` (where it meant the company) | 2 |
| `4c7575a` | `Maisto` → `Maïsto` (canonical diaeresis spelling) | 4 |
| `f8ef10c` | `Michel Rivasy` → `Michèle Rivasi` (wrong final letter) | 2 |
| _this commit_ | `Opex` → `OPECST` (parliamentary office) | 26 |
| _this commit_ | `Ibsen` → `Ipsen` (French pharma) | 8 |
| _this commit_ | `Avantis` → `Aventis` (now Sanofi) | 6 |
| _this commit_ | `Abscience` → `AB Science` (French pharma) | 2 |
| _this commit_ | `Neroche` → `Roche` (Swiss pharma) | 2 |
| _this commit_ | `Pfizer-415` → `Pfizer, à 95 %` (efficacy reference) | 2 |

## Definitively not in the audio (no fix possible)

These terms were checked carefully and Cotton simply doesn't say them
out loud in any of the 18 interviews:

- **Statitec** (her own CRO). Across every Cotton self-introduction,
  she uses descriptive language only — "ma société", "une CRO",
  "Clinical Research Organization" — never the brand name. Verified
  by grepping every Cotton paragraph that contains "ma société" or
  "j'ai monté"; none follows it with a brand. The brand name appears
  on the site in third-person prose (About page, Expertise page),
  but Cotton herself never says it in these recorded conversations.

## Remaining known issues (open work)

### Mishearings without a stable surface form

These terms were probably said by Cotton but Whisper rendered them too
inconsistently / phonetically for a simple substitution to catch:

- **C4591001** — the Pfizer trial code. Zero exact matches in the
  corpus. Cotton names this trial repeatedly in her written work, so
  it's almost certainly spoken in some interviews. Whisper either
  dropped the alphanumeric or wrote out the digits phonetically
  (e.g. "C 4-5-9-1, zéro zéro un"). Fixing requires either an
  LLM-assisted pass that knows to look for it in trial-discussion
  contexts, or a human ear scrubbing the audio.
- **Comirnaty** — appears just once (correctly spelled, in
  `LIPps6b8LgE`). Cotton likely said it more often but Whisper
  rendered it as "communauté" (the unrelated French word for
  "community") or similar. Many "communauté" hits in the corpus are
  legitimate uses of the French word, so a blanket substitution
  would corrupt the text. Requires context-aware review.

### Translation artifacts in the EN files

The opus-mt-fr-en pass carried some FR-side mishearings into English
verbatim (e.g. an EN paragraph might still say "Aventis" because the
FR side now says "Aventis" — fine — but it might also say "Coton" if
the FR side did, because opus-mt doesn't fix proper nouns; the body
fixes above run on both languages). Re-translating individual EN
files after a FR fix is a possibility if quality matters more than
churn.

### Pipeline artifacts

- **Diarization quirk in `KwUr6wqeVT0`**: the channel's standard
  intro pitch ("Bonjour à tous. Je vous invite à vous abonner…") is
  labeled as Cotton at the top of the transcript, because pyannote
  merged Cotton's voice cluster with the host's voice cluster.
  Easy manual fix: open the file, retag the first paragraph (and
  any visibly host-style lines among the early "Cotton" turns) to
  `Animateur` / `Host`.
- **Diarization quirk in `snXhb5p5uTY`**: Cotton's voice was split
  across two clusters. Both are now labeled "Cotton" so the file
  reads as if she's one continuous speaker (which she is); no
  visible issue.
- **Six `(unclear)` / `(inaudible)` placeholders** survive across
  three files (`D69Q58E0rMM`, `Jn-2b0fUsrk`, `WmDFTibK-Ek`) —
  pyannote's fallback for ultra-brief / mostly-silent segments
  (just "…", "»"). They could be deleted entirely without losing
  content.

## How to do another cleanup pass

1. **Add a new row to the "Body-text fixes applied" table above** in
   the same commit that fixes the issue, so the corpus history stays
   readable.

2. **Scan tooling**: keep using the small Python helpers in the
   commit history (`ocr_work/` had earlier examples — those scripts
   are git-ignored but the patterns are visible in the commit diffs).
   Pattern: regex with word boundaries, case-sensitive, single
   canonical replacement per surface form. The substitutions should
   run on _both_ `_FR.md` and `_EN.md` for any proper noun.

3. **Verify**: after fixing, `grep -l <misspelling> archive/transcripts/`
   should return nothing.

4. **Local Jekyll build** before committing: `LANG=en_US.UTF-8
   bundle exec jekyll build` — confirms nothing in the transcript
   pages broke (they're rendered by the `document` layout per the
   default rule in `_config.yml`).

5. **Commit + push**. The deploy workflow rebuilds the site within
   ~1 minute.
