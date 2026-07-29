# J&M Glass rebuild — kickoff prompt

Open a new chat with the working directory set to `~/Documents/Claude/jm-glass`, then paste
everything below the line (or just say: *"Read KICKOFF.md and follow it exactly. Use ultracode."*).

The folder already contains `KICKOFF.md` and `docs/`. That is expected and is the only thing in
it. Everything else you build is new.

---

Rebuild the site for **J&M Glass LLC**, a commercial glazing and tenant-improvement contractor in
Phoenix, AZ. This directory becomes the site's own git repo. Use ultracode.

## ROLE

You are an autonomous site-production agent. Mission: a site the owner recognizes as theirs, that
a stranger would NOT file under the same designer as my other sites. Run to completion without
asking permission between steps, with three gates where you stop: (a) any fabricated-content risk,
(b) a QA failure you cannot fix in two attempts, (c) before `gh repo create` or making anything
public. Never ask "should I continue".

## CONTEXT YOU MUST READ FIRST

1. **Template**: `~/Documents/Claude/site-template-v2`. READ-ONLY, never modify. Read `CLAUDE.md`,
   then `PLAYBOOK.md` in full, then `engine.py` and the current `build.py`. It governs everything;
   on conflict it wins. If you cannot read it, stop.

   **v2 was refactored on 2026-07-27 and is now an engine, not a template.** This matters more
   than anything else in this prompt. Read commit `f03929e` for the reasoning. Summary:
   - `engine.py` is mechanics only: `engine.Site` config, RAW-text escaping, JSON-LD, canonical,
     `head`/`foot`/`page`, sitemap, robots, build loop. It contains no markup that constitutes a
     look and refuses to build a page without `id="main"`.
   - `build.py` **is the face and you author all of it**. The one in the template is a
     deliberately plain two-page proof. It is NOT a design to retheme. If your site resembles it,
     you have not done the work.
   - `styles.css` is 120 lines: reset, DIRECTION KNOBS, light/dark mechanism, a11y. **Zero
     component rules.** You write every component rule below the marked line.
   - `app.js` is theme + reduced-motion only, exposed as `window.site`. No menu, no lightbox, no
     filters, no reveals. Author what you need.
   - `chat.js` was **deleted**. The Worker backend (`worker/`, server-side, faceless) stays.
     Recover the quote-wizard state machine and the XSS-safe linkifier with
     `git show 60db2db:chat.js` and **port the logic, not the markup**.

2. **Research**: already in this repo. Read `docs/RESEARCH_BRIEF.md` first, then
   `docs/research/README.md` and the five modality files beside it (`own-site.md`,
   `gbp-reviews.md`, `competitors.md`, `industry-direction.md`, `social-directories.md`).
   Raw agent returns are in `docs/research/raw/` if you need to check a claim at source. This is a completed
   10-agent sweep, every claim independently re-verified against its source URL. **Do not re-run
   the research.** Treat `RESEARCH_BRIEF.md` as settled fact and the modality files as the evidence.
   Anything the brief lists under "could NOT be established" stays unestablished.

## WHY THE LAST ATTEMPT FAILED, AND THE BAR

A previous build derived the direction correctly (colour, shape, type weight, light, tempo all
changed per business) and **still read as a sibling of the old sites.** Measured: after a full
restructure that renamed the hero to `.masthead`, replaced the CTA band with `.itb`, dropped the
marquee and invented 31 new class names, it still shared **41 class names with v1** — chat widget
16, footer grid 7, nav mechanics 6, button family 5, page rhythm 4, call bar 1, a11y utils 2.
Same furniture, different paint.

**Your bar: near-zero class-name overlap with the old sites, because you author the furniture.**
Run this before you ship and put the number in the build log:

```bash
comm -12 <(grep -ho 'class="[^"]*"' *.html | tr ' "' '\n\n' | sed 's/class=//' | sort -u) \
         <(grep -ho 'class="[^"]*"' ../bwraps/*.html | tr ' "' '\n\n' | sed 's/class=//' | sort -u)
```

Specific reflexes to catch yourself on: floating pill nav, eyebrow-pill section head, logo
marquee, bottom-right chat bubble, three-across feature cards, a dark "CTA band" before the
footer, `.wrap`/`.section` rhythm. If you find yourself building one, stop and ask why.

## FACTS ALREADY SETTLED (do not re-ask)

| | |
|---|---|
| Scope | **Commercial only, stated flatly.** Their ROC class is CR-65 "Specialty Dual" which covers residential, and their Facebook once posted pool-fence work; the owner's instruction is still commercial-only |
| Reviews | **CUT.** No usable positive public review exists. Trust is carried by the verifiable ROC record instead. Never invent one |
| Tenure | **"Licensed since 2015"**, not the 2016 their own site claims. ROC first issued 2015-11-09, BBB agrees |
| NAP | 1502 N 29th Ave, Phoenix, AZ 85009 · 623-243-5538 · Mon-Fri 6am-2pm |
| Form inbox | `wyatt741@gmail.com` (FormSubmit destination, never displayed). Display `jmglassllc@gmail.com`. Stays this way until the DNS migration, which happens at the same time |
| Chat | Hybrid AI Worker. `worker/` is faceless and reusable; you author the widget markup and port the logic |
| Content rights | Cleared: project photos, 2023 team photo, GC partner logos. **NOT cleared: the four leadership headshots** |
| Pages | Keep it tight. Derive the page set from what this business needs, not from a default five |
| Repo | `jm-glass`, CNAME `jmglassllc.com`. **Pages on `main`** (`git init -b main`). DNS still points at their WordPress host, so do not add CNAME until cutover or the github.io URL 301s to a dead domain |

## ASSETS YOU MUST RE-PULL

The 63 project photos and the team photo are **gone** and must be re-acquired. `jmglassllc.com`
returns 403 to curl and every non-browser client, including full browser header sets. The route
that works, documented in `docs/RESEARCH_BRIEF.md` §10: drive a real browser session and call their own
WordPress API from inside the page context.

```
/wp-json/wp/v2/media?per_page=100&page=N   -> every image, with its parent post id
/wp-json/wp/v2/project?per_page=100        -> the 22 projects, id -> title/slug
```

The `post` field maps each photo to its project. Downscale in-page via `OffscreenCanvas`, then
POST to a throwaway `127.0.0.1` receiver (localhost is a trustworthy origin, so mixed-content
rules do not block it). Exclude the three Unsplash files by filename. Their logo PNG has an
**opaque white background** — knock it out, and generate a reversed variant for dark surfaces.

## LOOP

1. Read the template `CLAUDE.md`, `PLAYBOOK.md`, `engine.py`, `build.py`. Then `docs/RESEARCH_BRIEF.md` and `docs/research/`.
2. Derive the DIRECTION KNOBS per PLAYBOOK §9 from the brief. State one line of reasoning per knob
   before setting it. Note `--accent` is the token name now, not `--pink`; `test_knobs.py` fails on
   legacy names. Glass reflects rather than emits, so justify any `--glow-a` above 0.
3. **Decide the page set and the component set from scratch.** What does a GC estimator making a
   bid/no-bid call actually need? The research §8 argues this is a credential document, not a
   marketing funnel. That is an input, not a layout you must copy.
4. Re-pull the assets. Inspect every image at full size before use.
5. Author `build.py`, and the CSS below the marked line in `styles.css`. Load the §11 design skills
   (`emil-design-eng`, `design-taste-frontend`) BEFORE styling; Impeccable audit after.
6. Gates: `python3 build.py`, `python3 test_seo.py`, `python3 test_knobs.py`, all exit 0. Every page
   has `id="main"`.
7. Playwright QA (PLAYBOOK §11 and §12): every page at 1440x900 and 430x932, both themes,
   `scrollWidth <= 430`, tap targets >= 44px, contrast >= 4.5:1, every control you invented works by
   keyboard with visible focus. Verify knobs by **computed style** on a loaded page, never by
   runtime mutation. Serve over HTTP with keep-alive (`protocol_version = "HTTP/1.1"`), or a large
   gallery will reset connections and look like broken images.
8. Run the class-overlap check above. Then §12's judgement check: open bwraps and anderson-it beside
   it and ask whether a stranger would file them under one designer. If yes, the direction is not done.
9. Deploy only after gate (c).

## OUTPUT

`docs/BUILD_LOG.md` as you go: one row per work-list item with status (built / cut / SAMPLE /
failed), the fact or intake answer that justifies it, and for anything unverified what would verify
it. Include the class-overlap number. Then this project's own `CLAUDE.md`. Report at the end what
shipped SAMPLE-marked and what I still owe you.

House style: no em dashes, no fabricated content. Every claim, stat and credential has a source or
ships SAMPLE-marked.

**File output:** everything you produce stays inside this project folder. Research, build log,
state docs, generated assets, screenshots worth keeping. Nothing goes to OneDrive; this repo is
the single home for the project, so `git` is the backup.
