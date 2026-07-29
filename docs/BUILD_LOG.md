# BUILD_LOG — J&M Glass LLC

Run: site-v2 runner, 2026-07-29. Engine: `~/Documents/Claude/Website Template`.
One row per work-list item. The work list froze at the grill (`docs/SETTLED.md`).

## Phase 0-3, setup and derivation

| Item | Status | The settled answer or source behind it |
|---|---|---|
| Repo re-entry | built | `preflight --start jm-glass --resume-site`. The folder was a staged rebuild carrying `KICKOFF.md` + the 2026-07-26 research. 3 colliding items backed up to `.preflight-backup/20260729T192845Z/` |
| Engine set | built | 13 items copied verbatim. `styles.css`, `test_knobs.py` and `worker/` had drifted from a pre-rename copy and were replaced; `engine.py`, `app.js`, `test_seo.py` were already byte-identical |
| Research | **not re-run** | `KICKOFF.md` is explicit: the 10-agent sweep is settled fact. Part 2 was appended instead, carrying the asset re-pull and a proposed answer per §8 checklist line |
| Asset re-pull | built | 107 files via a real browser session against their own WP API. **Corrected a §10 defect:** the media endpoint is 2 pages / 198 items, and a first pass that stopped at page 1 silently lost Life Time, Taylor Morrison, 5 unattached job photos and every full-resolution logo. `X-WP-TotalPages` is the authority |
| Image inspection | built | 71 photographs opened at full size by 9 agents. 55 usable, 25 strong, 11 rejected. Recorded in `docs/research/asset-inventory.json` with per-frame alt text |
| Direction | built | `docs/direction.json` + `docs/DESIGN_READ.md`. 14/16 knobs off neutral, zero drift against `styles.css`, verified with gate.py's own parser before a line of CSS was written |
| Logo knockout | built | Source is RGB with no alpha. Flood-filled inward from the border only, because the mark contains white *inside* it; a global white-to-alpha punches holes through the logo. Verified 0 non-white source pixels cleared |
| Favicons | built | Generated from the window-grid portion of the wordmark: 16/32/180/512 + `.ico` |
| Type | built | Archivo + Archivo Narrow, self-hosted, 53KB total. See the gate failure below |

## Phase 4, the face

| Item | Status | The settled answer or source behind it |
|---|---|---|
| Page set, 4 pages | built | Research §8: the job is surviving ten seconds on a bid list. `index` / `scope` / `projects` / `contact`. Not a default five |
| Title-block masthead | built | Derived device. A drawing sheet carries its project data in a title block; this is the one place the checkable licence belongs without reading as boasting |
| Mullion-grid layout | built | Derived from the trade: glazing is lites set into aluminium, so photographs sit flush in hairline-ruled cells |
| Licence record block | built | ROC 302375, Specialty Dual CR-65, active through 2027-11-30, first issued 2015-11-09, bond 27806, zero ROC and BBB complaints. Every row public at roc.az.gov |
| Scope page, 12 scopes | built | Grill answer 4: all 12. Every scope is tied to a named photograph, which is what made the list legitimate at all |
| Project record, 22 projects | built | 54 published frames. Per-project Commercial Shell / Tenant Improvement read from **their own WP taxonomy** (terms 37 and 36), never inferred |
| Curtain wall, called out | built | `cfc_1/4/5` show reflective IGUs in a multi-storey curtain wall. The highest-value scope in the trade, absent from their current copy entirely |
| GC partner marks, 23 | built | Grill answer 2: show the logos. Every `alt` names the company as **read off the mark** during inspection; the pass corrected several of my filename guesses (`bmc` is Bailey Marshall, not "BMC"; `dcbg` is DC Building Group) |
| Team photo | built | Rights cleared. Shown once, captioned "The crew, 2023", with no employee count attached |
| Contact, bid path | built | FormSubmit to `wyatt741@gmail.com` (lowercase, never displayed); `jmglassllc@gmail.com` displayed |
| Chat widget | built | Grill answer 3: hybrid. Logic ported from `git show 60db2db:chat.js`, markup and class names 100% new |
| Commercial-only statement | built | KICKOFF. Stated flatly in the footer and on contact, without their current site's apologetic phrasing |
| Reviews | **cut** | No usable positive public review exists. Never invented |
| Prequalification block | **cut** | Grill answer 1: omit entirely |
| Leadership headshots | **cut** | Rights NOT cleared |
| Careers, pricing, testimonials | **cut** | Defaulted cut at the grill and recorded there |
| Employee count, years of experience | **cut** | Four conflicting sources for the first; their own Facebook contradicts the second. Neither ships |

## Phase 5, the gate loop

Red to green, in order.

| # | Failure | Cause | Fix |
|---|---|---|---|
| 1 | `test_content`: no qualifying hero visual | The `.ask-panel` was a `<section>` inside `<header>`, so it became index's FIRST section and the hero check looked at the chat panel | Panel became a `role="dialog"` div. It was never a document section |
| 2 | stylesheet check: un-linted remote sheet on all 4 pages | Google Fonts `<link>`. gate.py refuses any remote stylesheet, because a sheet the linter never sees can still win the cascade | Self-hosted both families from `assets/fonts/` via `@font-face`, `fonts_href=""`. Both are OFL so this is compliant, recorded in `LICENSES.md`, and it removes a third-party round trip from first paint |

Two defects I caught by eye before QA, both design-discipline rather than gate failures:

| # | Defect | Fix |
|---|---|---|
| 3 | Hero headline ran **4 lines** at 1440. The taste skill is explicit that this is a font-size error, not a copy-length one | Headline shortened to "Commercial glazing for Arizona general contractors.", clamp max 4.05rem to 3rem, measure 19ch to 28ch |
| 4 | **The chat opener shipped bottom-right** — the exact reflex `KICKOFF.md` names, and a direct contradiction of my own `DESIGN_READ.md`, which said it opens from the title block | Opener moved into the title block beside the daylight control. The panel now anchors under its trigger on desktop (a popover scales from its trigger) and is a bottom sheet only on phones, where a thumb is. `--tb-h` is published by JS so the anchor survives the masthead going from three rows to one |

### Class-name overlap, the KICKOFF bar

The bar was "near-zero class-name overlap with the old sites, because you author the
furniture." `test_unique.py` measures it against all five registry sites:

```
overlap anderson-it: 0
overlap andersontech-site: 0
overlap bwraps: 0
overlap jr-liquor-mart: 0
overlap jr-smoke-zone: 0
```

**Zero, against every prior site, on 128 authored class names.** For contrast, the attempt
this rebuild replaces shared **41** with v1 after a full per-business derivation. No waiver
was needed, so `docs/WAIVERS.md` does not exist: none of the 20 banned names is in use.

The KICKOFF's named reflexes, each checked: no floating pill nav, no bottom-right chat
bubble (defect 4 above, caught and fixed), no logo marquee, no three-across feature cards,
no dark CTA band before the footer, no eyebrow-pill section heads, no `.wrap`/`.section`
rhythm. Eyebrow count across the site: zero.

## Phase 6, QA and the §12.8 verdict

_Filled in below as the QA pass runs._
