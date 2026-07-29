# Licences and provenance

## Photography

**All 54 published photographs are J&M Glass's own job-site documentation**, recovered
from their WordPress media library (`docs/RESEARCH_BRIEF.md` Part 2 §11) and owner-vouched
per `docs/SETTLED.md`. No stock photography ships on this site.

Deliberately excluded during the pull and recorded here so nobody re-adds them:

| Excluded | Why |
|---|---|
| every `*unsplash*` file on their server | third-party stock, not their work |
| `phoenix-high-rise.jpg`, `mountain-sil.jpg` | stock or generic, not a J&M project |
| `lifetime_peoria.jpg` | an architectural **rendering**, not a photograph |
| `IMG_1539-scaled.jpg` | pixel-identical duplicate of the 2023 team photo |
| the four leadership headshots | publication rights NOT cleared |

No AI-generated imagery ships. `docs/DESIGN_READ.md` records the §9a prompt the direction
would drive, and why real photographs of the client's own work beat it here.

## Typefaces

Both families are self-hosted from `assets/fonts/`, subset to latin, variable, and served
by `@font-face` in `styles.css`.

| Family | Licence | Source |
|---|---|---|
| Archivo | SIL Open Font License 1.1 | Omnibus-Type, via Google Fonts |
| Archivo Narrow | SIL Open Font License 1.1 | Omnibus-Type, via Google Fonts |

The OFL permits redistribution and web embedding, including bundling the font files with a
site, so self-hosting is compliant. Full licence text:
<https://openfontlicense.org/>

**DINPro is NOT used and must not be added.** It is genuinely J&M's own face, self-hosted in
22 `@font-face` rules on their current WordPress site, but it is a commercial Monotype family
and is not redistributable on a rebuilt site. Archivo Narrow is the substitute, recorded as a
substitute in `docs/DESIGN_READ.md`.

## Third-party marks

`assets/gc/` carries 23 general contractor and developer logos recovered from J&M's own
server. The owner confirmed rights to display them (`docs/SETTLED.md`, grill answer 2). Each
mark is the property of the company it identifies and is used here only to identify that
company. Every name in the `alt` text was read off the mark itself during the full-size
inspection pass, not inferred from the filename, and the inspection corrected several
guesses in the process.

## Logo

`assets/logo.png` and `assets/logo-reversed.png` are derived from J&M's own
`jmglass-main-horz-logo_1.png`. The source has no alpha channel, so the white background was
knocked out by flood-filling inward from the border only (`tools/make_logo.py`); the reversed
variant maps the near-black wordmark to light ink and leaves the brand red untouched.
