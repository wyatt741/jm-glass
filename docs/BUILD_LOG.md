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

KICKOFF's own `comm -12` command, run against the generated HTML, agrees:

```
$ comm -12 <(grep -ho 'class="[^"]*"' *.html | tr ' "' '\n\n' | sed 's/class=//' | sort -u) \
           <(grep -ho 'class="[^"]*"' ../bwraps/*.html | tr ' "' '\n\n' | sed 's/class=//' | sort -u)
(no output)
```

**0 shared class names with bwraps, 0 with anderson-it, out of 117 distinct class names in
the markup.**

The KICKOFF's named reflexes, each checked: no floating pill nav, no bottom-right chat
bubble (defect 4 above, caught and fixed), no logo marquee, no three-across feature cards,
no dark CTA band before the footer, no eyebrow-pill section heads, no `.wrap`/`.section`
rhythm. Eyebrow count across the site: zero.

## Phase 6, QA and the §12.8 verdict

### Automated QA

`gate.py --ship` green, stamp written over 247 files. `qa.py`: 4 pages x 2 widths x
2 themes, zero horizontal overflow anywhere, `#main` present everywhere, all 16 knobs
verified by **computed style on a loaded page**, and both fonts proven to RENDER
(`body` computes `archivo`, `h1` computes `archivo narrow`) rather than merely being
declared.

`qa.py` does not cover §12.6 tap targets, §12.6 contrast or §12.7 keyboard focus, and it
screenshots `full_page` on a page it never scrolls, so lazy images below the fold came out
blank. `tools/visual_qa.py` closes both gaps: **70 assertions, 0 failures.**

| Check | Result |
|---|---|
| Tap targets >= 44px, both dimensions | green after 8 fixes (see below) |
| Text contrast, WCAG AA (4.5:1, 3:1 large) | green on all 16 combos, first pass |
| Focus ring on every control | green on all 16 combos, first pass |
| Daylight control toggles the theme | green |
| Assistant opens from the title block and greets | green |
| Assistant closes on Escape, focus returns to the opener | green |
| Quote wizard advances and offers its options | green |
| Project filter narrows the record | green, 22 to 9 |
| All images decode | green after the keep-alive fix |

Fixes this pass forced:

| # | Failure | Cause and fix |
|---|---|---|
| 5 | 8 tap targets under 44px: the logo link, the title-block phone, 3 footer contact links, footer nav links, the nudge dismiss, 3 contact data links | Real. The hit area now reaches 44px via `inline-flex` + `min-height`/`min-width`, so the 12px data strip keeps its density while the control is thumb-sized |
| 6 | 6 GC logos reported as failed to load | **My QA harness, not the site.** I set `protocol_version` on a `functools.partial` instead of on the handler class, so the server silently stayed HTTP/1.0, closed every connection, and a sheet requesting 60 images at once got resets that look exactly like broken images. This is PLAYBOOK §10's documented trap and it bit the tool built to catch it |
| 7 | The pass hung 12 minutes on the project sheet | `html` has `scroll-behavior: smooth`, so `scrollTo(bottom)` **animates**. On a 15000px sheet it never traversed the middle, those lazy images never started loading, and awaiting their `load` event waited forever. Now: disable smooth for the settle, step through in viewport increments, force `loading="eager"`, and race the wait against a timeout |
| 8 | Contrast walk was very slow | `getComputedStyle` up the ancestor chain for every text node, over 54 identical captions. Deduped by style signature |
| 9 | Hero headline 4 lines, then 3 | Measured across 5 widths rather than guessed. Now 2 lines at 1440, 1280, 1100 and 430; 3 at exactly 900px, where the two-column split first engages and the CTA still sits at 468px |
| 10 | "Reach us directly" collided with the list above it | `.bid-h + .bid-h` could not match across the intervening `<ul>`. Added `.bid-list + .bid-h` |
| 11 | The nudge landed on top of the h1 at 430px | Suppressed below 700px. The opener is already a thumb's reach away in the masthead, and moving the nudge to the bottom would just rebuild the floating bubble this design deliberately does not have |

### The side-by-side

`docs/qa/side-by-side/jm-glass-vs-anderson-it-vs-andersontech-site.png`, four panels at
1440 wide, matched viewport height. The two nearest registry sites are **anderson-it** and
**andersontech-site** (all five overlaps are 0, so the tie broke on registry order, first
listed wins). **bwraps** is included as a fourth panel because KICKOFF names it explicitly.
anderson-it came from its live URL with one overlay dismissed before the shot; the other two
have no live URL in the registry and were served from their own repos.

Per-axis reading:

| Axis | J&M Glass | anderson-it | andersontech-site | bwraps |
|---|---|---|---|---|
| **Nav** | flush full-width title block, licence data strip, underline-active links, no CTA pill | dark bar, pill CTA | dark bar, pill CTA | dark bar, pink pill CTA |
| **Section rhythm** | hairline-ruled document sections and data tables | dark full-bleed bands, card rows | dark bands, centred statements | dark bands, big media |
| **Type** | Archivo Narrow condensed, tight, left-aligned, small | wide grotesque, large, centred | wide grotesque, centred | very large display, coloured words |
| **Light** | light paper, cool neutrals, red accent, `--glow-a: 0`, zero halo | dark, blue, emissive | dark, blue, emissive | dark, pink gradient, emissive |
| **Chat** | labelled button in the masthead | bottom-right circular bubble plus "Questions? I can help" nudge | none visible | bottom-right circular bubble plus nudge |

The three prior sites read as siblings of each other: all dark, all emissive, all pill-CTA,
two with the same bottom-right bubble and the same nudge copy. This one is the only light
one, the only square one, the only one whose accent is not blue or pink, and the only one
that reads as a document rather than a pitch. No waivers exist to echo here, because
`docs/WAIVERS.md` was never needed.

### Post-QA fix, found while reporting

| # | Defect | Fix |
|---|---|---|
| 12 | **`worker/` was still template boilerplate**: 11 TODO markers, `PLACEHOLDER-domain.com` in the origin allowlist, `555-555-5555`, and a system prompt naming "BUSINESS NAME". No gate catches this, because `settled_check` only proves `wrangler.jsonc` exists. Since the settled tier is hybrid, `ship.py` would have deployed it, and the origin allowlist alone would have rejected every real request | Filled from the brief: real origins, real phone, the licence and bond record, all 12 scopes, the bid-package checklist, and a price deflection rewritten for bid work. The reusable HOW TO TALK / HARD RULES / SAFETY guardrails were kept verbatim. `wrangler.jsonc` named `jm-glass-chat` with the `chat.jmglassllc.com` route ready to uncomment at cutover |

### Wyatt's §12.8 verdict

The row below is the one thing in this run I must not fill in myself. Replace `PENDING`
with the single word ACCEPT or REJECT. `ship.py` refuses on a missing token, refuses on
both tokens, and refuses on REJECT, so the ship gate stays shut until you rule.

| Judgement | Nav | Rhythm | Type | Light | Verdict |
|---|---|---|---|---|---|
| §12.8 would a stranger file these under one designer | distinct | distinct | distinct | distinct | PENDING |
