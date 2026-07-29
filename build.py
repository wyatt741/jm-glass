#!/usr/bin/env python3
"""THE FACE — J&M Glass LLC. Authored 2026-07-29 for this business only.

    python3 build.py && python3 gate.py

The read (docs/DESIGN_READ.md): this is a bid document for general contractor
estimators, not a marketing funnel. Research §8 measured the job as surviving the
ten seconds between a GC pulling J&M off a bid list and deciding whether to send
the invitation. So evidence outranks claims on every screen, the structure answers
the four questions an estimator actually asks, and density is a feature.

The layout language is taken from the trade rather than a layout family: glazing is
a grid of lites set into aluminium, so the page is a hairline grid with photographs
set flush into its cells, and the masthead and footer are a drawing-sheet TITLE
BLOCK carrying the checkable record.

Content rules that are not negotiable here (docs/SETTLED.md):
  - every photograph is J&M's own, inspected at full size, alt text written from
    what is actually in the frame
  - the four unattributed curtain wall frames get generic captions and are never
    captioned as a named project
  - no reviews, no employee count, no years-of-experience claim, no superlative,
    no prequalification block, no leadership headshots
  - "licensed since 2015", never their own site's wrong "since 2016"
"""
import json
import pathlib

import engine

HERE = pathlib.Path(__file__).parent
MANIFEST = json.loads((HERE / "assets" / "work" / "manifest.json").read_text())

CSSV, JSV = 1, 1

# ============================ CONFIG ============================
# RAW text. Never HTML entities — the engine escapes for HTML and keeps the raw
# value for JSON-LD, and refuses to build on a pre-escaped value (§2, §4).
SITE = engine.Site(
    biz="J&M Glass LLC",
    tag="Commercial glazing and tenant improvement",
    city="Phoenix, AZ",
    domain="jmglassllc.com",
    addr="1502 N 29th Ave, Phoenix, AZ 85009",
    phone="623-243-5538",
    phone_tel="+16232435538",
    # FormSubmit destination. Lowercase, and NOT the address shown on the page —
    # it stays this way until the DNS migration (docs/SETTLED.md).
    email="wyatt741@gmail.com",
    hours="Mon-Fri 6am-2pm",
    theme_color="#db1e22",
    # Empty on purpose. The type is self-hosted from assets/fonts via @font-face in
    # styles.css: gate.py refuses any remote stylesheet, because a sheet the linter
    # never sees can still win the cascade. Both families are OFL (LICENSES.md).
    fonts_href="",
    css=f"styles.css?v={CSSV}",
    js=f"app.js?v={JSV}",
    socials=("https://www.instagram.com/jmglassllc/",
             "https://www.facebook.com/Jmglassllc/"),
    extra_head=('<link rel="icon" href="assets/favicon.ico" sizes="any">'
                '<link rel="icon" href="assets/icon-512.png" type="image/png">'
                '<link rel="apple-touch-icon" href="assets/icon-180.png">'),
)

DISPLAY_EMAIL = "jmglassllc@gmail.com"          # shown to visitors
MAPS = "https://maps.google.com/?q=1502+N+29th+Ave,+Phoenix,+AZ+85009"

# ============================ CONTENT ============================
# The licence record. Every row is checkable on a .gov or BBB page, which is the
# whole reason this block exists: their current site claims "fully licensed glass
# experts" with no number, while ROC 302375 is real and public.
RECORD = [
    ("AZ ROC licence", "302375", "Specialty Dual CR-65, Glazing"),
    ("Status", "Active", "renewed through 2027-11-30"),
    ("First issued", "2015-11-09", "licensed in Arizona for over ten years"),
    ("Qualifying party", "William P Fain", "member and qualifying party"),
    ("Surety bond", "27806", "Western National Mutual, active, no claim ever paid"),
    ("ROC complaints", "None", "no open, resolved or disciplinary cases"),
    ("BBB complaints", "None", "no complaints on file"),
]

# The 12 scopes. Every one is evidenced by a photograph in assets/work — that is
# the rule that let this list exist at all, since their current site describes the
# entire offering in two words (research Part 2 §11).
SCOPES = [
    ("Aluminium storefront", "family-dollar-3.jpg",
     "Framed storefront systems in clear or tinted insulated glass, set with "
     "entrance doors, sidelites and transoms."),
    ("Curtain wall", "cfc-4.jpg",
     "Multi-storey aluminium curtain wall glazed with reflective insulated units, "
     "set from lifts and swing stages."),
    ("Window wall", "chop-shop-4.jpg",
     "Full-height gridded window wall between slabs, where the framing carries "
     "the glass rather than the building skin."),
    ("Aluminium entrances", "medical-3.jpg",
     "Narrow-stile and medium-stile door pairs with closers, panic hardware and "
     "matching sidelite framing."),
    ("Automatic sliding entrances", "family-dollar-4.jpg",
     "Sliding entrance assemblies with transoms, set into the storefront line and "
     "flashed to the opening."),
    ("Frameless office fronts", "call-center-4.jpg",
     "Interior glass office fronts and partition runs in tempered glass, with "
     "minimal or no vertical framing."),
    ("Sliding glass doors", "call-center-1.jpg",
     "Top-hung sliding glass doors on exposed stainless barn track, used across "
     "office and conference fronts."),
    ("All-glass doors", "credit-union-3.jpg",
     "Tempered all-glass door pairs on pivot hardware with patch fittings and "
     "overhead closers."),
    ("Blinds-between-glass", "credit-union-1.jpg",
     "Sealed partition units with integral blinds, for interior spaces that need "
     "switchable privacy without a curtain."),
    ("Mirror", "ktnn-2.jpg",
     "Wall mirror set and trimmed on site, including large single-piece runs in "
     "finished interiors."),
    ("Glass guard and windbreak panels", "lake-3.jpg",
     "Tempered panels set into steel or galvanised posts as guards and wind "
     "screens, including exterior dock work."),
    ("Sunshades over storefront", "bath-body-works-1.jpg",
     "Metal sunshade and trellis assemblies mounted above the storefront line and "
     "tied into the framing."),
]

CAPABILITY_CAPTION = "Commercial curtain wall installation"

# 23 GC and developer marks recovered from their own server. Rights confirmed by the
# owner (docs/SETTLED.md). Their current site ships all 23 with EMPTY alt text; every
# name here was read off the mark itself during the full-size inspection pass
# (docs/research/asset-inventory.json), not guessed from the filename, because an
# alt attribute that names the wrong company is fabricated content.
PARTNERS = [
    ("wt-logo.png", "Whiting-Turner"),
    ("jokake-logo.png", "Jokake Construction"),
    ("wespac-logo.png", "WESPAC Construction Inc."),
    ("johnson-logo.png", "Johnson Carlier, a Big-D company"),
    ("ar-mays-logo.png", "A.R. Mays Construction"),
    ("alexander-logo.png", "Alexander Building Company"),
    ("cr-logo.png", "CR Commercial"),
    ("forefront-logo.png", "Forefront Development LLC"),
    ("hadfield-logo.png", "Hadfield Building Corporation"),
    ("renaissance-logo.png", "Renaissance Companies"),
    ("princeton-logo.png", "Princeton Construction LLC"),
    ("sharp-logo.png", "Sharp Construction"),
    ("venn-logo.png", "Venn Construction"),
    ("pegasus-logo.png", "Pegasus Construction"),
    ("nfc-logo.png", "NFC Contracting Group"),
    ("maco-logo.png", "MACO Construction"),
    ("zdi-logo.png", "ZDI, LLC"),
    ("pcg-logo.png", "Pacific Construction Group"),
    ("bmc-logo.png", "Bailey Marshall Construction"),
    ("dcbg-logo.png", "DC Building Group"),
    ("formthird-logo.png", "FormThird Design-Build"),
    ("pride-logo.png", "Pride Contracting"),
    ("lifetime-logo.png", "Life Time Construction"),
]

PAGE_TITLES = {
    "index.html": "Home",
    "scope.html": "Scope",
    "projects.html": "Projects",
    "contact.html": "Bid invitations",
}

BY_FILE = {p["src"].split("/")[-1]: p
           for proj in MANIFEST["projects"] for p in proj["photos"]}
BY_FILE.update({p["src"].split("/")[-1]: p for p in MANIFEST["capability"]})


# ============================ COMPONENTS ============================

def plate(photo, *, eager=False, caption=None, sizes="(min-width:900px) 46vw, 100vw"):
    """A photograph set flush into the grid, the way glass sets into a frame."""
    cap = f'<figcaption class="plate-cap">{caption}</figcaption>' if caption else ""
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    return (f'<figure class="plate">'
            f'<img src="{photo["src"]}" alt="{photo["alt"]}" width="{photo["w"]}" '
            f'height="{photo["h"]}" loading="{loading}"{priority} decoding="async" '
            f'sizes="{sizes}">{cap}</figure>')


def titleblock(here):
    """The masthead, built as a drawing-sheet title block: the mark, the checkable
    licence line, and the sheet index. Deliberately not a floating pill nav."""
    links = "".join(
        f'<li><a class="jump-a{" jump-a--here" if page == here else ""}" '
        f'href="{page}"{" aria-current=\"page\"" if page == here else ""}>{label}</a></li>'
        for page, label in PAGE_TITLES.items())
    return f'''<header class="tblock">
  <div class="tblock-in">
    <a class="tblock-mark" href="index.html" aria-label="{SITE.biz}, home">
      <img class="tb-logo" src="assets/logo.png" alt="{SITE.biz}" width="1567" height="187" loading="eager" decoding="async">
      <img class="tb-logo tb-logo--rev" src="assets/logo-reversed.png" alt="{SITE.biz}" width="1567" height="187" loading="eager" decoding="async">
    </a>
    <dl class="tblock-data">
      <div class="tb-field"><dt class="tb-key">ROC</dt><dd class="tb-val">302375</dd></div>
      <div class="tb-field"><dt class="tb-key">Scope</dt><dd class="tb-val">Commercial only</dd></div>
      <div class="tb-field"><dt class="tb-key">Call</dt><dd class="tb-val"><a href="tel:{SITE.phone_tel}">{SITE.phone}</a></dd></div>
    </dl>
    <nav class="jump" aria-label="Sheets">
      <ul class="jump-list">{links}</ul>
    </nav>
    <button class="daylight" type="button" data-theme-toggle aria-pressed="false">
      <span class="daylight-txt" data-daylight-label>Dark</span>
    </button>
  </div>
</header>'''


def sheetfoot():
    """The footer repeats the title block, because that is what a drawing sheet
    does, and it is where the flat commercial-only statement belongs."""
    jumps = "".join(f'<li><a href="{p}">{t}</a></li>' for p, t in PAGE_TITLES.items())
    return f'''<footer class="sheetfoot">
  <div class="sf-in">
    <div class="sf-data">
      <p class="sf-name">{SITE.biz}</p>
      <p class="sf-line"><a href="{MAPS}" target="_blank" rel="noopener">{SITE.addr}</a></p>
      <p class="sf-line"><a href="tel:{SITE.phone_tel}">{SITE.phone}</a></p>
      <p class="sf-line"><a href="mailto:{DISPLAY_EMAIL}">{DISPLAY_EMAIL}</a></p>
      <p class="sf-line">{SITE.hours}</p>
    </div>
    <div class="sf-data">
      <p class="sf-name">Licence</p>
      <p class="sf-line">AZ ROC 302375</p>
      <p class="sf-line">Specialty Dual CR-65, Glazing</p>
      <p class="sf-line">Active, first issued 2015-11-09</p>
      <p class="sf-line">Bonded and insured</p>
    </div>
    <nav class="sf-jump" aria-label="Sheets">
      <p class="sf-name">Sheets</p>
      <ul>{jumps}</ul>
    </nav>
  </div>
  <p class="sf-fine">Commercial work only. We do not take residential glass.
    Serving {SITE.city} and Arizona.</p>
</footer>'''


def askwidget():
    """The chat affordance. The quote-wizard state machine and the XSS-safe
    linkifier are ported from the retired chat.js (git show 60db2db:chat.js) but
    NONE of its markup is: no bottom-right bubble, no cw-* ids. This opens from the
    title block, which is where help lives in a document."""
    return '''<div class="ask" id="ask" data-ask>
  <button class="ask-open" type="button" data-ask-open aria-expanded="false" aria-controls="ask-panel">
    <span class="ask-open-txt">Ask about a bid</span>
  </button>
  <section class="ask-panel" id="ask-panel" data-ask-panel hidden aria-label="Bid assistant">
    <div class="ask-head">
      <p class="ask-title">Bid assistant</p>
      <button class="ask-shut" type="button" data-ask-shut aria-label="Close the assistant">Close</button>
    </div>
    <div class="ask-log" data-ask-log role="log" aria-live="polite"></div>
    <form class="ask-form" data-ask-form>
      <label class="ask-lbl" for="ask-input">Message</label>
      <input class="ask-input" id="ask-input" data-ask-input autocomplete="off"
             placeholder="Ask about scope or a bid">
      <button class="ask-send" type="submit" data-ask-send>Send</button>
    </form>
  </section>
</div>'''


# ============================ PAGES ============================

def home():
    hero = BY_FILE["storage-co-3.jpg"]
    scope_rows = "".join(
        f'<li class="scope-item"><h3 class="scope-name">{name}</h3>'
        f'<p class="scope-note">{note}</p></li>'
        for name, _, note in SCOPES)

    record_rows = "".join(
        f'<div class="stamp-row"><dt class="stamp-key">{k}</dt>'
        f'<dd class="stamp-val">{v}<span class="stamp-note">{note}</span></dd></div>'
        for k, v, note in RECORD)

    # a mullion grid of six frames spanning building types, not one project
    preview = [BY_FILE[f] for f in ("johnny-was.jpg", "cfc-1.jpg", "esplanade-1.jpg",
                                    "medical-2.jpg", "chop-shop-1.jpg", "credit-union-3.jpg")]
    tiles = "".join(f'<div class="lite">{plate(p, sizes="(min-width:900px) 31vw, 100vw")}</div>'
                    for p in preview)

    marks = "".join(
        f'<li class="gc"><img class="gc-img" src="assets/gc/{f}" alt="{name}" '
        f'width="250" height="200" loading="lazy" decoding="async"></li>'
        for f, name in PARTNERS)

    team = MANIFEST["team"]
    body = f'''{titleblock("index.html")}
<main id="main">
  <section class="opening">
    <div class="opening-copy">
      <h1 class="opening-claim">Commercial glass and glazing for Arizona general contractors.</h1>
      <p class="opening-sub">Storefront, curtain wall, window wall and interior glass.
        Commercial only. Licensed in Arizona since 2015.</p>
      <p class="opening-acts">
        <a class="act" href="contact.html">Send a bid invitation</a>
        <a class="act act--quiet" href="scope.html">See the scope list</a>
      </p>
    </div>
    <div class="opening-plate">{plate(hero, eager=True, sizes="(min-width:900px) 52vw, 100vw")}</div>
  </section>

  <section class="stamp" aria-labelledby="stamp-h">
    <h2 class="stamp-h" id="stamp-h">The record, checkable</h2>
    <p class="stamp-lede">Every line below can be verified without asking us.
      The licence is public at <a href="https://roc.az.gov/" target="_blank" rel="noopener">roc.az.gov</a>.</p>
    <dl class="stamp-grid">{record_rows}</dl>
  </section>

  <section class="scope" aria-labelledby="scope-h">
    <h2 class="scope-h" id="scope-h">What we self-perform</h2>
    <ul class="scope-list">{scope_rows}</ul>
    <p class="scope-more"><a class="act act--quiet" href="scope.html">Each scope, with the work behind it</a></p>
  </section>

  <section class="shots" aria-labelledby="shots-h">
    <h2 class="shots-h" id="shots-h">Work in Arizona</h2>
    <div class="glazing">{tiles}</div>
    <p class="shots-more"><a class="act act--quiet" href="projects.html">All 22 projects</a></p>
  </section>

  <section class="gcs" aria-labelledby="gcs-h">
    <h2 class="gcs-h" id="gcs-h">General contractors and developers we have glazed for</h2>
    <ul class="gc-list">{marks}</ul>
  </section>

  <section class="crew" aria-labelledby="crew-h">
    <div class="crew-copy">
      <h2 class="crew-h" id="crew-h">The company</h2>
      <p>J&amp;M Glass was founded in 2015 by Mike Cook and Bill Fain, and has been a
        licensed Arizona glazing contractor since 9 November that year. Mike estimates,
        Bill runs the projects.</p>
      <p>The crew self-performs the scopes on this site. Commercial work only, from
        shell storefront and curtain wall through tenant improvement interiors.</p>
    </div>
    <div class="crew-plate">
      <figure class="plate">
        <img src="{team["src"]}" alt="The J&amp;M Glass crew photographed together in 2023"
             width="{team["w"]}" height="{team["h"]}" loading="lazy" decoding="async"
             sizes="(min-width:900px) 46vw, 100vw">
        <figcaption class="plate-cap">The crew, 2023</figcaption>
      </figure>
    </div>
  </section>
</main>
{askwidget()}
{sheetfoot()}'''
    return SITE.page(
        f"{SITE.biz} | Commercial Glazing Phoenix",
        "Commercial glazing and tenant improvement in Phoenix. Storefront, curtain "
        "wall, window wall and interior glass. AZ ROC 302375, licensed since 2015.",
        "index.html", body, body_class="sheet")


def scope():
    cells = ""
    for name, photo_file, note in SCOPES:
        photo = BY_FILE[photo_file]
        cap = CAPABILITY_CAPTION if photo_file.startswith("cfc-") else None
        cells += (f'<li class="lite scope-cell">'
                  f'{plate(photo, caption=cap)}'
                  f'<h2 class="scope-cell-name">{name}</h2>'
                  f'<p class="scope-cell-note">{note}</p></li>')
    body = f'''{titleblock("scope.html")}
<main id="main">
  <section class="pagehead">
    <h1 class="pagehead-h">Scope of work</h1>
    <p class="pagehead-sub">Twelve scopes we self-perform. Each one is shown with a
      photograph of the work, taken on our own jobs.</p>
  </section>
  <section class="scopesheet" aria-label="Scopes">
    <ul class="glazing glazing--two">{cells}</ul>
  </section>
  <section class="askline">
    <h2 class="askline-h">Need a scope that is not listed?</h2>
    <p class="askline-p">If it is commercial glass and aluminium, ask. We do not take
      residential glass.</p>
    <p><a class="act" href="contact.html">Send a bid invitation</a></p>
  </section>
</main>
{askwidget()}
{sheetfoot()}'''
    return SITE.page(
        f"Scope of Work | {SITE.biz}",
        "The twelve commercial glazing scopes J&M Glass self-performs, each shown "
        "with a photograph of the work: storefront, curtain wall, window wall, more.",
        "scope.html", body, body_class="sheet")


def projects():
    records = ""
    for proj in MANIFEST["projects"]:
        if not proj["photos"]:
            continue
        tags = "".join(f'<li class="record-tag">{t}</li>' for t in proj["types"])
        kinds = " ".join(t.lower().replace(" ", "-") for t in proj["types"])
        plates = "".join(
            f'<div class="lite">{plate(p, sizes="(min-width:900px) 23vw, 50vw")}</div>'
            for p in proj["photos"])
        where = f'<p class="record-where">{proj["city"]}</p>' if proj["city"] else ""
        records += f'''<article class="record" data-kinds="{kinds}">
      <div class="record-head">
        <h2 class="record-name">{proj["title"]}</h2>
        {where}
        <ul class="record-tags">{tags}</ul>
      </div>
      <div class="glazing glazing--four record-plates">{plates}</div>
    </article>'''

    caps = "".join(
        f'<div class="lite">{plate(p, caption=CAPABILITY_CAPTION, sizes="(min-width:900px) 23vw, 50vw")}</div>'
        for p in MANIFEST["capability"])

    body = f'''{titleblock("projects.html")}
<main id="main">
  <section class="pagehead">
    <h1 class="pagehead-h">Project record</h1>
    <p class="pagehead-sub">Twenty-two projects across Arizona, in two categories:
      commercial shell and tenant improvement. Every photograph is our own.</p>
    <div class="filterbar" data-filterbar hidden>
      <span class="filterbar-lbl" id="filter-lbl">Show</span>
      <button class="filter" type="button" data-kind="all" aria-pressed="true">All</button>
      <button class="filter" type="button" data-kind="commercial-shell" aria-pressed="false">Commercial shell</button>
      <button class="filter" type="button" data-kind="tenant-improvements" aria-pressed="false">Tenant improvement</button>
    </div>
  </section>
  <section class="records" aria-label="Projects" data-records>
    {records}
  </section>
  <section class="capsheet" aria-labelledby="cap-h">
    <h2 class="cap-h" id="cap-h">Curtain wall</h2>
    <p class="cap-p">These frames are from our own curtain wall work. They are shown as
      capability photographs because the project they belong to is not published.</p>
    <div class="glazing glazing--four">{caps}</div>
  </section>
</main>
{askwidget()}
{sheetfoot()}'''
    return SITE.page(
        f"Project Record | {SITE.biz}",
        "Twenty-two commercial glazing projects across Arizona by J&M Glass, shown "
        "with our own job-site photographs. Commercial shell and tenant improvement.",
        "projects.html", body, body_class="sheet")


def contact():
    body = f'''{titleblock("contact.html")}
<main id="main">
  <section class="pagehead">
    <h1 class="pagehead-h">Bid invitations</h1>
    <p class="pagehead-sub">Send the invitation and we will tell you quickly whether we
      are bidding. Commercial work only.</p>
  </section>

  <section class="bidpath">
    <div class="bid-what">
      <h2 class="bid-h">What to send</h2>
      <ul class="bid-list">
        <li>Project name and address</li>
        <li>Bid date and time</li>
        <li>Architectural and glazing drawings, or a plan room link</li>
        <li>Specification sections 08 40 00 and 08 80 00 if you have them</li>
        <li>Whether you need alternates or value engineering priced</li>
      </ul>
      <h2 class="bid-h">Reach us directly</h2>
      <dl class="bid-data">
        <div class="bid-field"><dt>Phone</dt><dd><a href="tel:{SITE.phone_tel}">{SITE.phone}</a></dd></div>
        <div class="bid-field"><dt>Email</dt><dd><a href="mailto:{DISPLAY_EMAIL}">{DISPLAY_EMAIL}</a></dd></div>
        <div class="bid-field"><dt>Shop</dt><dd><a href="{MAPS}" target="_blank" rel="noopener">{SITE.addr}</a></dd></div>
        <div class="bid-field"><dt>Office hours</dt><dd>{SITE.hours}</dd></div>
        <div class="bid-field"><dt>Licence</dt><dd>AZ ROC 302375, Specialty Dual CR-65</dd></div>
      </dl>
    </div>

    <form class="bid-form" action="https://formsubmit.co/{SITE.email}" method="POST">
      <h2 class="bid-h">Send an invitation</h2>
      <input type="hidden" name="_subject" value="Bid invitation from jmglassllc.com">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_captcha" value="false">
      <p class="bid-row">
        <label class="bid-lbl" for="f-name">Your name</label>
        <input class="bid-in" id="f-name" name="name" required autocomplete="name">
      </p>
      <p class="bid-row">
        <label class="bid-lbl" for="f-co">Company</label>
        <input class="bid-in" id="f-co" name="company" required autocomplete="organization">
      </p>
      <p class="bid-row">
        <label class="bid-lbl" for="f-email">Email</label>
        <input class="bid-in" id="f-email" name="email" type="email" required autocomplete="email">
      </p>
      <p class="bid-row">
        <label class="bid-lbl" for="f-phone">Phone</label>
        <input class="bid-in" id="f-phone" name="phone" type="tel" autocomplete="tel">
      </p>
      <p class="bid-row">
        <label class="bid-lbl" for="f-project">Project name and address</label>
        <input class="bid-in" id="f-project" name="project">
      </p>
      <p class="bid-row">
        <label class="bid-lbl" for="f-due">Bid date</label>
        <input class="bid-in" id="f-due" name="bid_date" type="date">
      </p>
      <p class="bid-row">
        <label class="bid-lbl" for="f-msg">Scope and notes</label>
        <textarea class="bid-in bid-in--tall" id="f-msg" name="message" rows="5" required></textarea>
      </p>
      <p class="bid-row bid-row--send">
        <button class="act" type="submit">Send invitation</button>
      </p>
      <p class="bid-fine">Goes straight to the office. If it is urgent, call
        <a href="tel:{SITE.phone_tel}">{SITE.phone}</a>.</p>
    </form>
  </section>
</main>
{askwidget()}
{sheetfoot()}'''
    return SITE.page(
        f"Bid Invitations | {SITE.biz}",
        "Send a commercial glazing bid invitation to J&M Glass in Phoenix. What to "
        "include, direct phone and email, office hours, and AZ ROC 302375.",
        "contact.html", body, body_class="sheet")


PAGES = {
    "index.html": home,
    "scope.html": scope,
    "projects.html": projects,
    "contact.html": contact,
}

if __name__ == "__main__":
    engine.build(SITE, PAGES)
