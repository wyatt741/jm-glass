#!/usr/bin/env python3
"""Validates the GENERATED pages — the SEO and mobile guarantees a site must not ship without.

Run AFTER build.py:   python3 build.py && python3 test_seo.py

Scope: everything statically checkable. Rendering-dependent checks (horizontal overflow,
tap-target size, contrast, CLS) are the Playwright gate's job — PLAYBOOK §11 — because they
need a real viewport. This file is the half you can run in a second, on every change.

ponytail: regex, not an HTML parser. These are shapes we control in build.py, not arbitrary
markup, so a parser would be weight without benefit. If build.py ever emits attributes in a
different order this gets loosened, not replaced.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).parent
PAGES = sorted(p for p in HERE.glob("*.html"))
fails, notes = [], []


def bad(page, msg):
    fails.append(f"{page}: {msg}")


def attr(html, pattern):
    m = re.search(pattern, html, re.I | re.S)
    return m.group(1).strip() if m else None


if not PAGES:
    sys.exit("no generated .html found — run python3 build.py first")

# The canonical BASE, read off the home page rather than assumed. The old rule
# counted slashes and demanded exactly two, which is only true for an apex domain
# and refused a Pages project URL like https://user.github.io/site/ — the very
# thing a pre-cutover client preview needs. Deriving the base instead checks the
# real invariant: home is the base, every other page hangs directly off it.
_home = HERE / "index.html"
BASE = None
HOME_CANON = None
if _home.exists():
    m = re.search(r'<link rel="canonical" href="(.*?)"', _home.read_text(encoding="utf-8"))
    if m:
        HOME_CANON = m.group(1)
        # A home canonical pointing at /index.html would otherwise become the base
        # and cascade a confusing failure onto every other page, so strip it here
        # and report the real fault once, below.
        BASE = re.sub(r"/index\.html/?$", "", HOME_CANON).rstrip("/")

for path in PAGES:
    n, h = path.name, path.read_text(encoding="utf-8")

    # ---- crawlability -------------------------------------------------
    if not h.lstrip().lower().startswith("<!doctype html>"):
        bad(n, "missing <!doctype html>")
    if not re.search(r"<html[^>]+lang=", h, re.I):
        bad(n, "<html> has no lang attribute (screen readers + hreflang)")
    if not re.search(r'<meta[^>]+charset=', h, re.I):
        bad(n, "no charset meta")

    titles = re.findall(r"<title>(.*?)</title>", h, re.S)
    if len(titles) != 1:
        bad(n, f"expected exactly 1 <title>, found {len(titles)}")
    elif not 10 <= len(titles[0]) <= 65:
        bad(n, f"title is {len(titles[0])} chars, want 10-65 (Google truncates ~60): {titles[0][:70]!r}")

    desc = attr(h, r'<meta name="description" content="(.*?)"')
    if not desc:
        bad(n, "no meta description")
    elif not 50 <= len(desc) <= 160:
        notes.append(f"{n}: meta description is {len(desc)} chars, want 50-160")

    canon = attr(h, r'<link rel="canonical" href="(.*?)"')
    if not canon:
        bad(n, "no canonical link")
    elif BASE is None:
        bad(n, "index.html carries no canonical, so there is no base to check against")
    elif n == "index.html":
        # home canonicalises to the base itself with a trailing slash, never to
        # /index.html, or "/" and "/index.html" split into two URLs
        if re.search(r"/index\.html/?$", canon):
            bad(n, f"home canonical points at /index.html, which splits the homepage "
                   f"into two URLs; it should be {BASE}/ — got {canon}")
        elif canon.rstrip("/") != BASE or not canon.endswith("/"):
            bad(n, f"home canonical should be the site base with a trailing slash "
                   f"({BASE}/), got {canon}")
    elif canon != f"{BASE}/{n}":
        bad(n, f"canonical {canon} is not {BASE}/{n}")

    h1s = re.findall(r"<h1[\s>]", h)
    if len(h1s) != 1:
        bad(n, f"expected exactly 1 <h1>, found {len(h1s)}")

    # ---- sharing ------------------------------------------------------
    for prop in ("og:title", "og:description", "og:type", "og:url", "og:site_name", "og:image"):
        if not re.search(rf'property="{prop}" content="[^"]+"', h):
            bad(n, f"missing or empty {prop}")
    for name in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
        if not re.search(rf'name="{name}" content="[^"]+"', h):
            bad(n, f"missing or empty {name}")

    # ---- structured data ----------------------------------------------
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            data = json.loads(block)
        except json.JSONDecodeError as e:
            bad(n, f"JSON-LD does not parse: {e}")
            continue
        # entities are NOT decoded inside <script>, so an escaped name ships to Google literally
        flat = json.dumps(data)
        if re.search(r"&(?:amp|lt|gt|quot|#\d+);", flat):
            bad(n, "JSON-LD contains an HTML entity — the value was escaped before json.dumps")
        if not data.get("name"):
            bad(n, "JSON-LD has no name")

    # ---- mobile --------------------------------------------------------
    vp = attr(h, r'<meta name="viewport" content="(.*?)"')
    if not vp:
        bad(n, "no viewport meta — the page will render at desktop width on phones")
    else:
        if "width=device-width" not in vp:
            bad(n, f"viewport lacks width=device-width: {vp}")
        # blocking zoom is an accessibility failure and a Google mobile-usability flag
        if "user-scalable=no" in vp.replace(" ", "") or re.search(r"maximum-scale=1(\.0)?\b", vp):
            bad(n, f"viewport blocks pinch-zoom: {vp}")

    # ---- images ---------------------------------------------------------
    for tag in re.findall(r"<img\b[^>]*>", h, re.I):
        if 'id="lb-img"' in tag:
            continue  # lightbox target, populated by app.js on open
        if not re.search(r'\salt="[^"]+"', tag):
            bad(n, f"<img> without a non-empty alt: {tag[:80]}")
        if 'loading=' not in tag:
            notes.append(f"{n}: <img> without loading= hint: {tag[:60]}")

# ---- site-level files --------------------------------------------------
sm = HERE / "sitemap.xml"
rb = HERE / "robots.txt"
if not sm.exists():
    fails.append("sitemap.xml missing")
else:
    locs = re.findall(r"<loc>(.*?)</loc>", sm.read_text())
    if not locs:
        fails.append("sitemap.xml lists no URLs")
    for path in PAGES:
        want = path.name
        # home appears as the base with a trailing slash, not as /index.html. Compare
        # against the derived BASE so a Pages project URL works the same as an apex.
        listed = any(l.endswith(want)
                     or (want == "index.html" and BASE and l.rstrip("/") == BASE)
                     for l in locs)
        if not listed:
            fails.append(f"sitemap.xml does not list {want}")
    # a sitemap URL the page itself disowns is worse than no sitemap
    for path in PAGES:
        canon = attr(path.read_text(encoding="utf-8"), r'<link rel="canonical" href="(.*?)"')
        if canon and canon not in locs:
            fails.append(f"sitemap/canonical disagree for {path.name}: canonical={canon}")

if not rb.exists():
    fails.append("robots.txt missing")
elif "Sitemap:" not in rb.read_text():
    fails.append("robots.txt does not point at the sitemap")

# ---- report -------------------------------------------------------------
for note in notes:
    print(f"note  {note}")
if fails:
    sys.exit("FAIL\n  " + "\n  ".join(fails))
print(f"ok — {len(PAGES)} pages: crawlable, share-ready, valid JSON-LD, mobile viewport, alts present")
print("     (overflow, tap targets and contrast still need the Playwright gate — PLAYBOOK §11)")
