# DESIGN_READ — J&M Glass LLC

Phase 3 of the site-v2 run. Derived 2026-07-29 with `emil-design-eng` and
`design-taste-frontend` loaded first, from `docs/RESEARCH_BRIEF.md` and `docs/SETTLED.md`.
Knob values and per-knob reasoning are in `docs/direction.json`; this file is the read behind
them.

## The read

**Reading this as: a bid document for general contractor estimators, with a technical
drawing-sheet language, leaning toward native CSS, a condensed industrial grotesque, and
near-zero motion.**

Research §8 is the whole brief in one line: the buyer's evaluation is documentary, annual and
platform-mediated, and this site's actual job is to survive the ten seconds between a GC pulling
J&M off a bid list and deciding whether to send the invitation. That is not a marketing funnel.
Nobody arrives here to be persuaded; they arrive to check whether this company is real, licensed,
and has done the scope before.

Three consequences fall straight out of that:

1. **Evidence outranks claims.** They have 55 usable photographs of their own completed work and
   a licence number checkable on a .gov page. Their current site has neither on it in any useful
   form, and instead carries five superlatives that cannot be substantiated. Every screen here
   leads with a photograph or a verifiable number.
2. **The information architecture is a document, not a story.** No scroll narrative, no reveal
   sequence, no persuasion arc. Four pages, each answering one question an estimator actually
   asks: what do you self-perform, have you done my building type, who vouches for you, how do I
   get you a bid invitation.
3. **Density is a feature.** The taste default for a trust-first brief is airy and calm. Wrong
   here. An estimator scanning on a deadline wants facts per screen, so `VISUAL_DENSITY` runs 5-6,
   not 2-3.

Dials, reasoned rather than inherited: **DESIGN_VARIANCE 6** (asymmetric enough that it cannot be
a template, disciplined enough to read as a document), **MOTION_INTENSITY 2** (glass does not
bounce; motion only ever confirms a press), **VISUAL_DENSITY 5**.

### The layout language: the mullion grid and the title block

The structural motif is taken from the trade itself rather than from a layout family. Glazing IS
a grid: lites of glass set into aluminium, separated by mullions. So the page is built as a
hairline grid with photographs set flush into its cells, the way glass sets into a frame. The
grid is load-bearing, not decorative, which is the test the taste skill sets for hairline rules.

The second device is the **title block**. Engineering and architectural drawings carry a block of
hard project data in one corner: who drew it, licence, date, sheet. The masthead and the footer
are that block. It is a device no marketing site would reach for, it is instantly legible to the
one audience that matters, and it gives the checkable facts (ROC 302375, licensed since
2015-11-09, bond, hours) a natural home that does not read as boasting.

Used **once each** at the top and bottom of the page. Deliberately not repeated as numbered
section labels, because `001 · Capabilities` style eyebrows are a named AI tell and the registry
already bans `.eyebrow` outright.

### What this direction deliberately refuses

Every item here is either a reflex the KICKOFF named, a class in the registry's banned set, or an
AI tell from the taste skill:

| Refused | Why |
|---|---|
| Floating pill nav | KICKOFF reflex list. The masthead is flush, full width, hairline-ruled |
| Bottom-right chat bubble | KICKOFF reflex list. The chat opens from the masthead as a labelled control, where a document's help lives |
| Three-across feature cards | KICKOFF reflex list, and the taste skill bans the pattern outright. The scopes are a two-column rack of rows with photographs |
| Logo marquee | KICKOFF reflex list. The GC list is a static grid, and Wyatt chose to show the marks |
| Dark CTA band before the footer | KICKOFF reflex list. The bid path is a page, not a band |
| Eyebrow-pill section heads | `.eyebrow` is banned in all five registry sites |
| `.wrap` / `.section` rhythm | Both appear in 4 of 5 registry sites |
| Centred hero | Anti-centre bias above variance 4. The opening is an asymmetric split |
| Scroll cues, status dots, version stamps, locale strips | Named AI tells, all absent |
| Any glow | `--glow-a: 0`. Glass reflects, it does not emit |
| Rounded cards | `--r: 0px`. Competitors all use them; a glazed opening is square |

## Knob decisions

Full per-knob reasoning is in `docs/direction.json` and is not duplicated here. The four that
carry the character:

- **`--accent: #db1e22`** is recovered, not chosen. It is in their own Elementor palette and it is
  the colour of the ampersand in their wordmark. Half their live site runs Elementor stock colours
  beside it, so using it exclusively is the cheapest possible win on recognition.
- **`--glow-a: 0`** because glass reflects rather than emits. The KICKOFF asked for this to be
  justified above 0, and it is not above 0. Every photograph on the site is flat Arizona daylight
  on matte aluminium; a halo would contradict the evidence.
- **`--r-pill: 2px` against `--r: 0px`** is the one shape rule on the site: a 2px machined edge
  means pressable, dead square means not. One rule, learnable in a screen, and it can never drift
  into a pill.
- **`--motion: .55`**, brisker than the trade default of .6, because the reader is on a deadline
  and `emil-design-eng` is explicit that repeated interactions must never feel slow. `--spring` is
  flattened to `--ease`: aluminium does not overshoot.

Type is one superfamily at two widths (Archivo Narrow for display, Archivo for body) rather than a
pairing, because a document wants a type system. Their real face, DINPro, is a commercial Monotype
family and is not redistributable, so this is an honest substitute and is recorded as one.

## §9a imagery prompt

Composed from the knobs just derived, in the §9a slot order (light, edge, density, grade last and
corrective):

```
A glazier setting a large insulated glass unit into an aluminium storefront frame on a Phoenix
commercial building. Flat daylight, matte surfaces, no bloom, even ambient fill. Orthogonal
composition, hard edges, straight-on perspective, everything parallel to the frame. Compressed,
filled frame, close crop, high contrast. Colour grade, overriding any cast the lighting implies:
neutral cool palette, red the only saturated element, no overall colour tint. Photographic, no
text, no logos, no watermarks. People, if any, unidentifiable, turned away or at working distance,
face not legible.
```

**No generated imagery ships.** The prompt is recorded because §9a requires the direction to be
able to drive imagery, but 55 inspected photographs of J&M's own completed work exist, and a real
photograph of the client's own project beats a generated frame on every axis that matters here:
it is evidence, it needs no identifiability clause, and it cannot invent a scope they do not
perform. §9a's own hard rules point the same way, warning that a generated facility must never be
captioned as the client's own work. Generation would only be reached for if a scope had no
photograph, and none does.

The knobs still govern the photography, which is the point of §9a. Selection followed them:
flat-daylight frames preferred over blown-out ones, orthogonal elevations preferred over loose
oblique angles, and the eleven frames rejected in the inventory were rejected on exactly those
axes.

## Token source

**No Figma file exists** for this client. The research sweep found none, and the §8 intake line is
answered "none" in the brief. The Figma MCP is also unauthorised in this session, so it could not
have been used regardless.

Tokens therefore come from the **logo-derived-palette fallback** (Decision 9), and in this case
that is stronger than usual because the palette was not eyeballed off a screenshot. It was read
out of their own stylesheets during the research sweep:

| Token | Source |
|---|---|
| `--accent: #db1e22` | their Elementor global palette, plus the wordmark ampersand |
| `--accent-deep`, `--accent-soft` | arithmetic from `--accent`, so they cannot drift into second hues |
| `--shadow-rgb: 24, 28, 33` | derived, not theirs. Their near-black `#221e1f` is faintly warm and fought the aluminium; the site's neutrals are cooled deliberately |
| `--font-display`, `--font-body` | substitute for DINPro, which is genuinely theirs but is commercial Monotype and not redistributable |
| Surfaces | derived cool neutrals, light-default, with the dark set kept in sync in both required blocks |

Light is the default. Glass reflects rather than emits, and the artefact is a document read in
daylight. The dark set is authored to full parity because an OS-dark visitor gets it before
choosing anything, and `test_knobs.py` requires that block to exist.
