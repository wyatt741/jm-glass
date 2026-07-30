# jm-glass — Project Entry

> ⭐ **LATEST SESSION — 2026-07-29.** Rebuilt from scratch with the **site-v2 runner**
> (`~/Documents/Claude/Website Template`, `RUN.md`), the first real client site the
> engine has produced. Phases 0 through 6 are complete and committed; **nothing is
> public.** The run stops at RUN.md stop (d) / KICKOFF gate (c): the `§12.8` row in
> [docs/BUILD_LOG.md](docs/BUILD_LOG.md) carries `PENDING` and needs Wyatt's single-word
> `ACCEPT` or `REJECT` before `ship.py` will go outward.
>
> **The bar was near-zero class-name overlap with the older sites. Result: 0 against all
> five registry entries**, on 128 authored class names, confirmed both by `test_unique.py`
> and by KICKOFF's own `comm -12` command. The attempt this replaces shared 41 with v1.
>
> The read: this is a **bid document for GC estimators**, not a marketing funnel
> (research §8). The layout language is the **mullion grid** plus a drawing-sheet **title
> block**; light paper, cool neutrals, brand red `#db1e22`, `--glow-a: 0`, condensed
> Archivo Narrow. Full derivation in [docs/DESIGN_READ.md](docs/DESIGN_READ.md) and
> [docs/direction.json](docs/direction.json).
>
> Biggest content win: their live site describes the entire offering in two words. This one
> ships **12 scopes, each tied to a photograph of their own work**, including **curtain
> wall**, which they have genuinely done and never claimed.

## What this is

A four-page static site for **J&M Glass LLC**, a commercial glazing and tenant-improvement
contractor in Phoenix, AZ. Built on the Website Template engine: `engine.py` supplies
mechanics only, and every visible component here was authored for this business.

| Page | Job |
|---|---|
| `index.html` | The whole case: what they self-perform, the checkable licence, proof of work, the bid path |
| `scope.html` | 12 scopes, each with a photograph of the work behind it |
| `projects.html` | 22 named Arizona projects, 54 photographs, filterable by Commercial Shell / Tenant Improvement |
| `contact.html` | The bid path: what to send, direct contacts, the invitation form |

## Facts that are settled and must not drift

- **Licensed since 2015-11-09**, never "since 2016" (their own site is wrong; ROC and BBB agree).
- **AZ ROC 302375**, Specialty Dual CR-65 Glazing, active through 2027-11-30. Bond 27806.
- **Commercial only**, stated flatly. No residential glass.
- **No reviews anywhere.** No usable positive public review exists. Never invent one.
- **No employee count, no years-of-experience claim, no superlative.** All contradicted by sources.
- FormSubmit inbox `wyatt741@gmail.com` (never displayed); display `jmglassllc@gmail.com`.
- The four leadership headshots are **not rights-cleared** and do not ship.
- `lifetime_peoria.jpg` is a **rendering**, not a photograph. It does not ship.

Everything above is sourced in `docs/RESEARCH_BRIEF.md` and frozen in
[docs/SETTLED.md](docs/SETTLED.md).

> **The research is not in this repo.** GitHub Pages requires a public repo and the client is
> sent that URL, so `docs/RESEARCH_BRIEF.md` and `docs/research/` were purged from history on
> 2026-07-30 before the first push. They remain on disk here (gitignored) and are backed up at
> `../jm-glass-research-private/`. They document the client's own 1-star reviews, six named
> competitors and a teardown of their current site: correct working papers, wrong thing for
> the client to find. Restore them into a repo only if that repo is private.

## Files

| Path | Purpose |
|---|---|
| `build.py` | THE FACE. Config, content, the 4 pages, and the markup for every component. Never hand-edit generated HTML |
| `styles.css` | Base engine CSS above the marked line, this site's component rules below it |
| `app.js` | Base theme mechanism above, this site's behaviour below: daylight label, project filter, bid assistant |
| `tools/make_assets.py` | Rebuilds `assets/work/` + `assets/gc/` + favicons from the inspected originals in `assets/src/` (gitignored) |
| `tools/make_logo.py` | Knocks the white background out of the wordmark and builds the reversed variant |
| `tools/visual_qa.py` | The §12.6/§12.7 half of the contract: tap targets, contrast, focus rings, every authored control |
| `tools/capture_peers.py` | Captures the registry sites for the §12.8 side-by-side |
| `tools/serve.py` | Preview server, HTTP/1.1 + threads (a 54-image sheet resets an HTTP/1.0 server) |
| `docs/research/asset-inventory.json` | Per-frame verdict on all 71 photographs. **Gitignored working paper**, see the note above |

## Resume

```bash
cd ~/Documents/Claude/jm-glass
python3 gate.py            # build + 5 tests + stylesheet + direction
```

Then read [docs/BUILD_LOG.md](docs/BUILD_LOG.md), which carries every red-to-green cycle and
the pending §12.8 row.

**To ship** (only after Wyatt writes the verdict):

1. Replace `PENDING` with `ACCEPT` on the `§12.8` row in `docs/BUILD_LOG.md`.
2. `printf 'jmglassllc.com\n' > CNAME` — **only at DNS cutover.** `ship.py` requires the
   CNAME to already match the settled domain, and KICKOFF forbids creating it earlier
   because GitHub would 301 the working preview URL to a domain it does not serve. See the
   hosting note in `docs/SETTLED.md`.
3. `python3 gate.py --ship` then `python3 ship.py`. **Never** `git push`, `gh repo create`
   or `wrangler deploy` by hand; a pre-push hook enforces the stamp.
4. `python3 "$HOME/Documents/Claude/Website Template/registry.py" add .`

## Open items Wyatt owes

- The `§12.8` verdict.
- Whether to cut over DNS (the chatbot Worker at `chat.jmglassllc.com` needs it too).
- The FormSubmit one-time activation click, on the first real submission.
- An Anthropic key + spend cap for the hybrid Worker before it answers anything.
