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

## Phase 6b, the Impeccable audit

Run on Wyatt's instruction after the §12.8 composite. `context.mjs` reported
`SCOPED_EXISTING_ALLOWED` (a narrow refinement command may treat the incumbent code as
authority), so the audit proceeded without PRODUCT.md. **Impeccable's mechanical detector
returned zero findings, twice.**

Then four adversarial critics were told to REFUTE the favourable self-assessment, one per
lens (a11y, performance, implementation integrity, content truth), at high effort, with
permission to drive a real browser. **Three of four returned `refuted`, one
`partially-refuted`, for 30 findings.** They were right, and several were things my own QA
harness structurally could not see:

| # | What they found | Verdict |
|---|---|---|
| 13 | **P0: twelve list-item disc markers rendering inside the scope grid.** `.glazing` is a `<ul>` and I never reset `list-style` | Real, and visible on a shipped page. My own QA screenshotted that page and I never opened the file |
| 14 | **The mullion frame never closed on 20 of 22 project records.** My earlier per-cell border fix put the top and left rules on the container, so a row with 1 photo in a 4-column grid left them hanging | Real. Every rule now lives on the cell with a `-1px` margin collapse |
| 15 | **`assets/og-image.jpg` did not exist.** Two critics found it independently. Every og:image, twitter:image and the JSON-LD image pointed at a 404, so every share previewed blank | Real. Generated 1200x630 from the hero frame with the reversed wordmark on a legible band |
| 16 | **All 26 portrait `-sm` files declared `500w` but are 281px wide.** `SMALL` caps the LONG edge, so browsers upscaled them on plain desktop | Real, and I introduced it an hour earlier "fixing" performance. `make_assets.py` now returns the true width and `build.py` emits it |
| 17 | **`sizes` switched at 900px while `.glazing` switches at 700px**, and every value described one column while the grid is 2-up from 0px. Measured 290KB wasted in one fold at 800px | Real. Five named constants now match the grid's own breakpoints and real column widths |
| 18 | **Keyboard focus dropped to `<body>` at every wizard step** (WCAG 2.4.3), and `setInput(false)` disabled the input that held focus | Real. Focus now moves before the element is destroyed, and Close takes it before the input is disabled |
| 19 | **Tab escaped the open assistant onto controls hidden behind it** (WCAG 2.2 SC 2.4.11) | Real. Tab is now contained while the panel is open |
| 20 | **Form field borders measured 1.3:1**, far under the 3:1 a non-text UI component needs (1.4.11), in both themes | Real. New `--field-line` token. **My contrast check only measured text, never component boundaries** |
| 21 | **Accent-as-text hover measured 3.5:1 in dark** (1.4.3) on five rules | Real. New `--accent-text` token, dark-only lift. **My contrast check only measured the resting state, never `:hover`** |
| 22 | **`aria-pressed` never tracked the theme.** An OS-dark visitor got `aria-pressed="false"` on load and the first click changed nothing in the a11y tree (4.1.2) | Real. Derived from the live theme in `paint()` |
| 23 | **`.filterbar` set `display:flex`, which beats the UA `[hidden]` rule**, so the no-JS guard did nothing | Real. `[hidden]` guard added |
| 24 | **"What we self-perform" is not established anywhere.** `docs/research/own-site.md`: "Whether they self-perform install vs. subcontract ... not stated". A photograph proves a product is on their job, not who installed it | Real, and the worst finding of the set: exactly the unsourced-claim class this build was supposed to refuse. Reworded sitewide, including the chat answers and the Worker prompt |
| 25 | **"Bonded and insured" in all four footers.** The bond is public; insurance is recorded UNVERIFIED | Real. Now "Bonded, no claim ever paid" |
| 26 | **Two Life Time frames show no glazing at all**, under a heading claiming every photograph is our own | Real. Both demoted to unusable in the inventory. The project count is now DERIVED from the manifest, so it dropped to 21 by itself instead of drifting |
| 27 | **Four scope notes asserted detail no photograph shows** ("swing stages", "between slabs", "large single-piece runs", "tied into the framing") | Real. All four trimmed to what the frame supports |
| 28 | **British spellings in US copy**, including "Licence" for an Arizona ROC license, and headings reading "Aluminium" while their own alt text said "aluminum" | Real. Normalised; a parser-based sweep of rendered text now confirms zero |
| 29 | **The sticky masthead was a fixed three-row grid: 178px, 21% of a 390x844 phone, permanently** | Real. Now 106px, 13%, and **tap-to-call stayed** (my first attempt dropped the phone to save 26px, which was the wrong trade for a trade contractor on a phone) |
| 30 | **`?v=1` was a hand-written literal no build step ever bumped**, so the cache-bust mechanism was inert | Real. Now an 8-char content hash of each file |
| 31 | Both masthead logos fetched eagerly at 1567px to render at 172px, one of them `display:none` | Real. A 344px mark per theme, ~4KB each |
| 32 | No font preload, so the faces were discovered only after CSS parsed | Real. Both woff2 preloaded in `extra_head` |
| 33 | The panel claimed in its own comment to anchor to its trigger but was positioned off the page gutter | Real. Now `position:absolute` inside `.ask` |
| 34 | JSON-LD published `wyatt741@gmail.com` as the business email, which KICKOFF says is never displayed | Real. `engine.Site.email` is now the public address; a separate `FORM_INBOX` drives the FormSubmit action |
| 35 | Dead CSS: `.sheet-in` matched nothing, two unreachable sibling selectors, a shadowed `display` | Real. Removed |

Two of these were defects in my **QA harness**, not the site, and both are now fixed:
`protocol_version` set on a `functools.partial` instead of the handler class (so the server
silently served HTTP/1.0), and a focus check that flagged elements sitting inside a
`display:none` ancestor as having no focus ring.

**After the fixes:** `gate.py` green, Impeccable detector zero findings,
`tools/visual_qa.py` **70 assertions 0 failures**, masthead 8-13% of viewport across
360-1440px, zero horizontal overflow at every width tested, and a parser-based sweep of all
rendered text clean of every banned string.

Accepted and NOT fixed, with reasons:

| Item | Why it stands |
|---|---|
| `prefers-reduced-motion` uses the engine's global `0.01ms` kill | Engine-provided base CSS, and nothing on this site communicates state by motion alone, so nothing is lost |
| Portrait frames are cropped to 4:3 in the grid | Inherent to a uniform mullion grid. Mitigated with `object-position: 50% 38%`, since the subject of a glazing photograph sits above centre |
| `ship.py` publishes `docs/`, so the competitor research would go live | **Template-level, flagged to Wyatt.** `SHIP_SET_DIRS` includes `docs/`, which would publish `competitors.md`, `gbp-reviews.md` and the raw research JSON to the live origin. Not changed here because it is engine behaviour affecting every site |
| No metric-matched font fallback | Preloading both faces removes the reflow in practice; a full metric override is a template-level concern |

### Round 2, the re-verification

Three verifiers re-checked all 23 fixes at high effort with a real browser, and confirmed
**every one as `fixed`** with pixel-level evidence (border runs measured in CSS px, contrast
recomputed per theme, focus walked with 14 forward and 14 reverse Tabs, the no-JS case run
with `javaScriptEnabled=False`). They also caught what round 1 missed:

| # | Found | Note |
|---|---|---|
| 36 | `app.js` still shipped the chat chip **"What you self-perform"** and asked "What do you self-perform?" | The round-1 sweep only checked rendered HTML. JS-authored copy is never inspected by any gate |
| 37 | The projects **meta and og:description still said "Twenty-two"** while the visible copy said the derived 21 | Deriving the visible count left the share card behind. Now derived too |
| 38 | **"travel centre"** survived in a chat answer | Same blind spot as 36 |
| 39 | `SZ_HERO` over-declared by 11% at 1440 and ignored the 32px gutters at 768 | Now measured exact: declared 592px renders 592px, declared `calc(100vw - 64px)` renders 704px at 768 |
| 40 | **My focus fix stole focus while the visitor was typing.** The follow-up offer renders mid-sentence and grabbed the caret out of the input | Regression from fix 18. Now gated on whether the input holds focus |
| 41 | **My Tab trap armed in a non-modal dialog.** Clicking the page left focus on `<body>` with the loop still live, so the sheet behind was keyboard-unreachable until Escape | Regression from fix 19. An outside press now closes the panel |
| 42 | **The panel covered the masthead rule and had no top edge**, measured as a 380px gap in a previously continuous rule | Regression from fix 33. Top border restored |
| 43 | **The photo grid sat 1px left of the type column** at every breakpoint, because the -1px collapse also applied to the first row and column | Regression from fix 14. Cancelled with a 1px pad; measured aligned at x=128 and x=32 |
| 44 | Quiet button borders were still `--line` at **1.31:1** while the same argument had raised the inputs | Pre-existing, and the outline is the only thing marking those as controls. Now `--field-line` |
| 45 | `worker.js` still carried **"swing stages"** and **"large single-piece runs"** after `build.py` dropped both | The Worker prompt is a third copy of the scope list and was missed |

Fixed all ten. Final state: `gate.py` green, Impeccable detector **zero findings on a third
run**, `tools/visual_qa.py` **70 assertions 0 failures**, project count 21 in the visible
copy, the meta description, the share card and the rendered record count alike, and a
string sweep of both JS files clean.

**A template gap worth carrying upstream**, raised by the verifier and confirmed: all four
gates exit 0 while two of these defects were live, because `test_content.py` inspects
generated HTML only. Copy that ships inside `app.js` or `worker/worker.js` is never checked
for fabrication, dashes, or overclaims, and this site has three separate copies of the scope
list. Two of the three were wrong at once.

### Two template gaps, closed upstream

Both were engine-level, so they were fixed in `~/Documents/Claude/Website Template`
(commit `a6c8c77`) and the updated `engine.py`, `test_content.py` and `ship.py` were synced
back into this repo. Every future site gets them at `preflight --start`.

| Gap | Fix | Proof |
|---|---|---|
| **No gate ever inspected shipped JS copy.** All four gates exited 0 while the chat shipped a chip contradicting the page it sat on, a stale "travel centre", and the Worker carried `555-555-5555` and `PLACEHOLDER-domain.com`. This site keeps **three** copies of the scope list and two were wrong at once | `test_content.py` now scans every string literal in `app.js` and `worker/worker.js` for dashes, placeholder residue and TODO markers. A literal that is *about* dashes may name them, so the Worker's own house rule still passes | Tested both directions on a fixture: clean JS exits 0, the four real shakedown defects all report. **The first version was wrong** and the fixture caught it: stripping comments with `//[^\n]*` also blanks the rest of any line holding a URL, because `https://` contains `//`, so it was blind to `PLACEHOLDER-domain.com`, the main thing it exists to catch. Replaced with a single-pass tokenizer |
| **Pages would have served the working papers.** Jekyll copies the whole repo to the live origin, so `docs/research/competitors.md`, the GBP review notes and the raw research JSON would have been fetchable from jmglassllc.com | `engine.build()` now writes `_config.yml` excluding `docs/`, `tools/`, `worker/`, `assets/src/` and the build chain. `ship.py` refuses on a missing or incomplete exclusion | Negative-controlled: absent config refuses, and a config that forgets `docs/` refuses by name. Now reports "the live origin will serve 7 html/css/js file(s) plus assets/" |

`ship.py` also prints an honest note that `docs/` remains in the **public repo** even though
the domain will not serve it, because Pages requires a public repo and that exposure cannot be
designed away.

**That call was then made, 2026-07-30.** Wyatt chose to strip the working papers before the
first push. `git filter-repo` purged `docs/research/` and `docs/RESEARCH_BRIEF.md` from all 16
commits and redacted the client's review numbers from the four other tracked files that
repeated them (`KICKOFF.md`, `CLAUDE.md`, `docs/SETTLED.md`, this log). Verified: 0 occurrences
of either path or the disclosure string anywhere in history. The files stay on disk, gitignored,
and are backed up at `../jm-glass-research-private/`. Nothing had been pushed, so this cost
nothing; after a first push it would have been impossible.

### Phase 7, SHIPPED as a preview, 2026-07-30

**Live at https://wyatt741.github.io/jm-glass/** — noindex, `robots.txt Disallow: /`, no
CNAME, not the client's domain. Repo `wyatt741/jm-glass` created public (Pages requires it),
Pages build `7c8710e` succeeded in 39s.

Verified live, not assumed: all 4 pages, `styles.css`, `app.js`, `og-image.jpg` and the
woff2 return **200**; `docs/research/competitors.md`, `docs/research/gbp-reviews.md`,
`docs/RESEARCH_BRIEF.md`, `docs/BUILD_LOG.md`, `build.py`, `tools/serve.py` and
`assets/src/media.json` all return **404**, so the `_config.yml` exclusion holds on the real
origin. Served canonicals point at the preview base, never at jmglassllc.com. Rendered in a
browser at 1440 to confirm it looks like what was built.

**The §12.8 verdict was NOT required and was NOT written.** Wyatt changed the rule
mid-session: *"the site template should auto accept and produce the preview. i shouldnt be
stopping you telling you to do so."* The judgement exists to protect the client's public
face, and a noindex preview on a URL that is not theirs is how a human gets to look at the
site in order to judge it, so gating the preview on it made the deciding artifact
unreachable until you had decided. `ship.py` and `preflight.py` now defer both the verdict
and the Worker deploy to the LIVE ship (template commit `1c1a410`). Every mechanical gate
still ran.

The Worker was deliberately not deployed: the widget's `WORKER_URL` is
`chat.jmglassllc.com`, which does not resolve until the cutover, so deploying now would
leave an orphan Worker on a workers.dev URL that PLAYBOOK §6 forbids serving the bot from.
The canned answers carry the preview.

## Phase 8, structural edit after the preview, 2026-07-30

Wyatt read the shipped preview and asked two questions. Both were right, and both were
checked against the files before acting rather than agreed with.

**1. "Shouldn't the scope and projects be the same page?"** Measured: `scope.html`'s twelve
photographs were **all twelve already on `projects.html`** (zero unique), and its twelve names
and notes were **byte-identical** to the list already on the home sheet. It was a third
presentation of content that existed twice. The two pages are two indexes of the same evidence,
which is also how an estimator reads it: what do you do, and where have you done it.

Merged into **`on-the-job.html`** — his name, chosen over "Work" (a designer's word, not a
glazier's) and over the literal "Scope and projects". Structure: the 12 scopes with their
photographs, then the 21-project record with its filter, then the curtain wall capability
frames, then the bid CTA. Home keeps its text-only scope list as the teaser. **Page set is now
three:** `index.html`, `on-the-job.html`, `contact.html`.

**2. "Why are we saying commercial only? Isn't that a given?"** Half right, and the half that
matters. It appeared **11 times across 4 pages**, including the masthead data strip of every
page. To a GC estimator it IS a given. It is not a given from the outside though: their ROC
class is CR-65 **Specialty Dual**, which covers residential; their Facebook posted pool-fence
work; one of their current homepage icons is a shower; and the two recent Google reviews
describe automotive work. So the fact earns its place, but its job is deflecting residential
callers, not informing estimators.

Cut from the masthead strip (all pages), the hero sub, and the crew copy. Kept in the footer
and on the contact sheet, where a residential caller actually lands. **11 mentions to 4**, and
the masthead is down to ROC and the phone number.

Both counts on the merged page are now **derived** (`len(SCOPES)`, `SHOWN_PROJECTS`) after a
review caught the sub mixing a spelled "Twelve" with a numeral "21".

Re-verified after the edit: `gate.py` green, **overlap still 0 against all five** registry
sites on 131 classes, `visual_qa.py` **54 assertions 0 failures** across 3 pages x 2 widths x
2 themes.

## Phase 9, image-forward hero and motivated motion, 2026-07-30

Wyatt: *"shouldnt we lead with pictures first? wheres the animations or the taste design
skill?"* Checked before answering.

**The taste skills did run** — `design-taste-frontend` and `emil-design-eng`, both loaded in
phase 3 before any CSS, dials recorded in `docs/DESIGN_READ.md`. Their output was almost
entirely **subtractive** (0 eyebrows sitewide, no three-across cards, no centred hero, no
marquee, no scroll cues, no decorative dots), which is real work that is invisible by
construction. A fair complaint even so, because you cannot see an absence.

**On animations he was right.** Measured: 11 transitions, 1 keyframe, and the only
`IntersectionObserver` was wired to the chat nudge. No entrance motion anywhere. "Near-zero
motion" was derived correctly from the trade row of PLAYBOOK §9 and then **over-applied**:
press feedback is motivated motion, and so is revealing evidence in the order a reader meets
it. Added `.set-in`, an IntersectionObserver reveal on the photo grids, the credential rows,
the scope list and the GC marks only. Nav, type and controls never animate. Verified: **42
elements reveal on scroll; under `prefers-reduced-motion` zero are marked and everything
renders at full opacity.**

**On leading with pictures he was right too, and it was the biggest of the three.** The hero
was text-left / photo-right, giving type primacy on a site whose entire value is 52
photographs. Now a **full-bleed photograph** with the claim on an opaque title-block panel
over it.

Three things that fell out of building it, each caught by measurement rather than eye:

| Found | Fix |
|---|---|
| The old hero frame was `storage-co-3.jpg`, whose source is only **960x720** — too soft for full bleed | Switched to `cfc_4.jpg`, the largest usable landscape frame (**1920x1440**, strong, no identifiable face) and the one that shows curtain wall, the highest-value scope. Re-emitted at 1800px. The curtain wall scope cell moved to `cfc-5` so the hero is not repeated |
| Text on a photograph has **no measurable contrast** — a checker reads `background-color`, not image pixels, so a gradient scrim only makes legibility likely | The claim sits on an **opaque** panel. Contrast becomes a fact, and it echoes the drawing-sheet title block the rest of the site is built from |
| The primary CTA **lost its fill** on the dark panel, so the outlined secondary read as more important. Contrast passed; hierarchy was inverted | Primary inverts to a solid paper button on the panel in both themes |

Also: the first reveal implementation set `--i` per element with `el.style.setProperty`, which
is a runtime inline style. Replaced with a CSS `nth-child` stagger so the whole look stays in
the stylesheet. **0 inline style attributes in the output.**

Verified across 360, 390, 430, 768, 1440 and 1920: full bleed at every width, both CTAs above
the fold everywhere, **0 horizontal overflow**. `gate.py` green, Impeccable detector clean,
`visual_qa.py` **54/54**, overlap still **0 against all five** registry sites.

## Phase 10, rebuilt in the Walters language, 2026-07-30

Wyatt: *"this website is ass"*, then *"what prompt do most people use"*, then
`waltersgroupinc.com` *"looks good"*, then *"make the entire website like theirs"*.

**The honest diagnosis of why it was plain.** KICKOFF's headline bar was near-zero class
overlap with the prior sites, and the PLAYBOOK bans the whole popular vocabulary (pill nav,
three-across cards, gradient hero, CTA band). So the build optimised hard for *"a stranger
would not file this under one designer"* and hit it five times over. But that is a **proxy**,
and the thing it was a proxy for is what Wyatt was judging. Distinct is not the same as good.
Every design input was a rule or a research finding; there was never a site he could point at.

**What was adopted from the reference** (its language, not its markup): a full-viewport
photograph of a person doing skilled work, type set large directly on the image, a one-line
statement between the photo and the proof, then the work, then the way in.

**What was deliberately NOT adopted:** their testimonial block (J&M have no usable review),
their careers block (no evidence they are hiring), their news feed (none exists), their blue.
Those sections do not exist here rather than being filled with invention.

**The hero photograph is the whole change.** The reference leads with an ironworker on a beam.
J&M own exactly one frame of that kind, `storage-co-3.jpg`: a glazier in a lift, arm raised,
setting reflective glass into a two-storey curtain wall. It had been the hero, and **I moved
away from it in phase 9 because it is only 960px wide and I wanted resolution for a full
bleed**. That was the wrong trade, and it is why the hero read as a stock building shot. It is
back, cropped low (`object-position: 50% 70%`) so the glazier is actually in frame, with the
type on the right because he stands on the left.

Three defects found by measurement while building it:

| Found | Fix |
|---|---|
| **The veil was a SIBLING of the type, not an ancestor.** A contrast checker walks ancestors, so it never saw the veil and measured white-on-white: **1.08:1** across the whole hero | The veil now wraps the copy. It is also simply true: the veil is what the type sits on |
| **`.act--ghost` was used on the light sections** ("All 21 projects"), so white text sat on white | Those revert to `act--quiet` |
| **The stage buttons used theme tokens.** The stage is dark in BOTH themes, so in dark mode `var(--ink)` inverted to light and gave a white button with white text | Literal colours on the stage only |

**A third bug in my own QA harness**, exposed by the veil: `bgOf` discarded the alpha the moment
it met a translucent layer, then fed a bare array back into the compositor and threw. No element
had ever had a semi-transparent background over another background, so the path had never run.
It now collects layers up to the first opaque one and composites bottom-up.

Also caught: the rebuild added `body_class="sheet home"`, and **`home` is a class in three prior
sites** — overlap went 0 to 1. Dropped; back to **0 against all five**.

Final: `gate.py` green, Impeccable detector clean, `visual_qa.py` **54/54**, overlap **0**,
148 authored classes.

## Phase 11, the copy pass, 2026-07-30

Wyatt: *"21 Arizona projects, 12 scopes, and a license you can check in under a minute? who
cares? this is also really old info. theyve done waaaaay more jobs. the hero should be
confident and inspirational. theres too much ai slop text everywhere."*

**The count was the serious one, and it was my error.** `SHOWN_PROJECTS` was derived from the
manifest, which made it accurate about the photographs and **wrong about the business**. 21 is
the number of projects that still had photographs on a WordPress site last touched around 2019.
The research already contained the correction and I did not act on it: their Procore profile
claims **217 total projects, 84 active** (`RESEARCH_BRIEF` §1). The site was advertising a tenth
of the company.

The fix is not a bigger number. 217 is claimed, unverified, and not ours to print. It is **no
number at all**: the photo set is a selection and nothing may imply it is an inventory.
`SHOWN_PROJECTS` is deleted, "All 21 projects" became "More of the work", and the record heading
became "Selected projects".

**The slop.** Every line where the site narrated its own credibility instead of just being
credible:

| Cut | Why |
|---|---|
| "21 Arizona projects, 12 scopes, and a license you can check in under a minute." | Counting is not a claim. Replaced with a range statement |
| "Every line below can be verified without asking us." | The table is the verification. Reduced to "Public at roc.az.gov" |
| "Every photograph on this site is from one of our own jobs. Nothing here is stock." | Protesting authenticity invites the doubt it answers |
| "These frames are shown as capability photographs because the project they belong to is not published." | That is my internal reasoning, narrated to a customer |
| "The crew works every scope **listed on this site**" | Self-referential |

Kept, because they are concrete rather than decorative: the twelve scope descriptions, the bid
checklist (drawings, spec sections 08 40 00 and 08 80 00, alternates), the founding facts, and
the ROC record.

**Hero:** "Glass and aluminum, set by the crew that bid it." was inward and technical. Now
**"Glass is the first thing anyone sees."** Confident, true, elevates the trade rather than the
company, and it carries no unverifiable claim.

Two defects the restructure introduced, both caught by measurement:

- Making the veil an ancestor turned it into a flow element sized to the copy, so it covered
  only the lower two thirds and drew **a hard band edge across the photograph**. Frame and veil
  now share one grid cell.
- With the frame stretching, `min-height` let it take the photograph's natural 4:3 and run to
  **1080px**, pushing the controls off the fold. It is a fixed height now.

Verified 360 to 1920: veil covers fully, controls above the fold, **0 overflow**. `gate.py`
green, detector clean, `visual_qa.py` **54/54**, overlap **0** against all five.

## Phase 12, Wyatt's review round two, 2026-07-30

Four changes, all his calls.

**Volume is publishable after all.** *"there projects are in the hundreds. why cant we just
generalize that"* — correct, and I had over-applied §4. The rule bars *invented* content, not
**owner-supplied** content, and I had published nothing about volume at all. Now "Hundreds of
commercial projects across the Valley" in the statement band, corroborated by their own Procore
profile (217 total, 84 active) so the generalisation is conservative. The number 217 itself
still does not ship: self-reported, unverifiable, and a precise figure invites a precision the
site cannot defend. Recorded in `SETTLED.md` with its provenance.

**"The record, checkable" was a dare, not a statement.** Cut from the home sheet entirely. The
footer already carried a licence block, so this was the scope/projects duplication again; the
footer block absorbed the two facts it lacked (no ROC or BBB complaints, and the roc.az.gov
link) and the ROC number stays in the masthead of every page. 1,223 characters of now-dead
`.stamp` CSS removed with it.

**The daylight control is an icon.** A word that says "Light" while the page is light reads as
a label, not a control. Sun and moon SVGs, swapped by theme, with the word kept in the DOM
visually hidden so the accessible name survives. Note: `sun` and `moon` are both in the banned
class vocabulary, hence `dl-day` / `dl-night`.

**The assistant moved to the bottom right.** This contradicts KICKOFF and PLAYBOOK §5, which
both name a bottom-right chat bubble as a v1 reflex. Wyatt asked for it directly. Worth
recording *why* the ban existed: the old widget contributed **16 of the 41 duplicated class
names** on its own. That vocabulary is `cw-*`; this one is `ask-*` and authored here, so the
uniqueness gate is unaffected. Overlap stayed 0.

**The work sheet was 12,574px tall.** *"a lot of those could be combined on the same lines."*
The scope index goes three across at 900px and four at 1200px, and each project record now puts
its label BESIDE its photographs rather than stacked above, removing a heading block of vertical
space across twenty-one records. **12,574px to 8,566px, no photographs lost.**

Also fixed: the CTA band centred each child independently, so the paragraph sat indented away
from the heading and the button above and below it. The section is padded now instead.

`gate.py` green, `visual_qa.py` **54/54**, overlap **0** against all five, 145 classes.

## The GC marks become a ribbon (2026-07-31)

Wyatt: "make this a gliding from right to left." Twenty-three marks in an auto-fill grid
left a ragged two-item last row on the wide breakpoint, which is what he was looking at.

A logo marquee is on the seven-item banned-reflex list in KICKOFF and PLAYBOOK §5. It is the
third rule he has overruled deliberately, after the bottom-right assistant and the icon
toggle. Noted rather than argued: the ban exists to stop a marquee being reached for as
decoration, and here it fixes a real layout fault.

The run is emitted twice, the second copy `aria-hidden`, and the track travels exactly -50%
so the loop closes on itself. A screen reader reads twenty-three marks, not forty-six, and
`alt` stays on every image because `test_seo` requires it.

Three things measured rather than assumed:

- **Phantom h-scroll.** PLAYBOOK §10 warns an unpinned marquee expands the page to its
  max-content track. Measured `scrollWidth - clientWidth` = 0 at 1440 and 390 with a
  7728px track.
- **Reduced motion.** The base a11y block only clamps `animation-duration` to `.01ms`,
  which would have spun this marquee at seizure speed rather than stopping it. The track
  gets `animation: none !important` and the band becomes a plain horizontal scroller.
  Measured `animationName: none` under `reduced_motion: reduce`.
- **Clipping.** First attempt used `max-height: 100%` on the marks; two of the taller
  logos overflowed the tile and were cut by the band's `overflow: hidden`. Caught by
  measuring every mark's rect against the band's, not by looking at it. Back to the fixed
  `max-height` the grid it replaces used.

The band also dropped the measure and runs the full width of the window. A ribbon that
stops short of both edges reads as a widget sitting on the page; one that runs off reads as
a list that continues. The soft mask fade went with it: this site's language is hard mullion
lines, and a gradient scrim is a different vocabulary.

`gate.py` green, `visual_qa.py` **70/70**, overlap **0** against all five, 146 classes.

### Wyatt's §12.8 verdict — still open, and now gates the LIVE ship only

The row below is the one thing in this run I must not fill in myself. Replace `PENDING`
with the single word ACCEPT or REJECT before the cutover. `ship.py` refuses a LIVE ship on a
missing token, on both tokens, and on REJECT.

| Judgement | Nav | Rhythm | Type | Light | Verdict |
|---|---|---|---|---|---|
| §12.8 would a stranger file these under one designer | distinct | distinct | distinct | distinct | PENDING |
