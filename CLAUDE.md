# jm-glass — Project Entry

> ⭐ **LATEST SESSION — 2026-07-29/30.** **SHIPPED as a client preview:**
> **https://wyatt741.github.io/jm-glass/** — noindex, `robots.txt Disallow: /`, no CNAME, not
> their domain. **Three pages** after a post-preview edit merged scope into
> `on-the-job.html` and cut "commercial only" from 11 mentions to 4. Repo
> `wyatt741/jm-glass` is public (Pages requires it). Verified live: all three pages 200, and
> `docs/research/`, `docs/RESEARCH_BRIEF.md`, `build.py`, `tools/`, `CLAUDE.md` and
> `assets/src/` all **404** on the real origin, so the `_config.yml` exclusion holds.
>
> Built end to end with the **site-v2 runner** (the template's first real client site).
> **Class overlap 0 against all five prior registry sites** (131 authored classes after the
> merge); the attempt this replaces shared 41. jm-glass is now itself the 6th registry entry.
>
> **An Impeccable audit plus two adversarial rounds found 33 real defects; all fixed.** Four
> were regressions from my own fixes and two were bugs in my QA harness, so treat a green
> harness with suspicion. Final: `gate.py --ship` green, detector clean 3x, `visual_qa.py`
> 70/70.
>
> **The §12.8 verdict is still open and now gates the LIVE ship only** (rule changed this
> session: a preview is how a human gets to look at the site in order to judge it). The
> Worker deploy defers with it.
>
> **The research is NOT in this repo** — purged from history before the first push, gitignored
> on disk, backed up at `../jm-glass-research-private/`. Full detail:
> [docs/SESSION_STATE_2026-07-29.md](docs/SESSION_STATE_2026-07-29.md).

## What this is

A three-page static site for **J&M Glass LLC**, a commercial glazing and tenant-improvement
contractor in Phoenix, AZ. Built on the Website Template engine: `engine.py` supplies
mechanics only, and every visible component here was authored for this business.

| Page | Job |
|---|---|
| `index.html` | The whole case: the work they do, the checkable license, proof, the bid path |
| `on-the-job.html` | The 12 scopes with their photographs, then the 21-project record with its Commercial Shell / Tenant Improvement filter, then the curtain wall capability frames |
| `contact.html` | The bid path: what to send, direct contacts, the invitation form |

Was four pages until 2026-07-30. `scope.html` was cut after measuring that all twelve of its
photographs were already on `projects.html` and its twelve names and notes were byte-identical
to the list on the home page; the two were merged into `on-the-job.html`.

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
| `docs/SESSION_STATE_2026-07-29.md` | Full session record: what worked, what failed and why, every decision |
| `Backups/` | Timestamped CLAUDE.md snapshots taken before each state save |

## Resume

```bash
cd ~/Documents/Claude/jm-glass
python3 gate.py            # build + 5 tests + stylesheet + direction
```

Then read [docs/BUILD_LOG.md](docs/BUILD_LOG.md), which carries every red-to-green cycle and
the pending §12.8 row.

### Step 1, the client PREVIEW — DONE

Live at **https://wyatt741.github.io/jm-glass/**. To publish any further change:

```bash
python3 gate.py --ship && python3 ship.py
```

**Never** `git push`, `gh repo create` or `wrangler deploy` by hand; the pre-push hook enforces
the stamp and will block you (it did, once, this session).

### Step 2, the LIVE cutover, all in ONE motion

Standing rule (RUN.md phase 7): shipping and moving DNS happen together, because either order
alone leaves no working URL.

1. `docs/SETTLED.md`: `- domain: jmglassllc.com`, delete the `- preview:` line.
2. `build.py`: `domain="jmglassllc.com"`, `preview=False` (the switch is commented at the top).
3. `printf 'jmglassllc.com\n' > CNAME`
4. Point jmglassllc.com's DNS at GitHub Pages, or at Cloudflare if you want the hybrid Worker
   on `chat.jmglassllc.com`.
5. `python3 gate.py --ship && python3 ship.py`
6. `python3 "$HOME/Documents/Claude/Website Template/registry.py" add .`

## Open items Wyatt owes

- The `§12.8` verdict.
- The DNS cutover, whenever J&M approve the preview (the Worker at `chat.jmglassllc.com`
  needs it too).
- The FormSubmit one-time activation click, on the first real submission.
- An Anthropic key + spend cap for the hybrid Worker before it answers anything.
