#!/usr/bin/env python3
"""THE ENGINE. Mechanics only — this file contains no design.

The rule that defines v2: *a template supplies structure and mechanics, never a face.*
v2's first attempt made the face repaintable (DIRECTION KNOBS) but still shipped one —
the same glass nav, the same chat bubble, the same footer grid, the same section rhythm.
Derived sites came out siblings anyway, because recognition lives in components, not
colour. So the components are gone. What is left is here, and it is deliberately
incapable of expressing taste:

  - the <head>: title/description/canonical/OG/Twitter/JSON-LD/viewport/theme-color
  - the document envelope: doctype, lang, a skip link, <main>, closing tags
  - sitemap.xml + robots.txt, kept consistent with the canonicals
  - the build loop

Everything visible — nav, hero, cards, footer, buttons, chat affordance, the section
rhythm — is authored per site in that site's own build.py and styles.css, from the
business brief (PLAYBOOK §9). There is nothing here to inherit and nothing to copy.

Quality is enforced by contract, not by shipping components: test_seo.py gates the
generated pages no matter what markup you invent.
"""
import json
import re
from datetime import date
from html import escape

_ENTITY = re.compile(r"&(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);")


class Site:
    """Per-site configuration. Author every text field as RAW text.

    HTML-escaping happens once, here. The raw values are kept for JSON-LD because
    browsers do NOT decode entities inside <script type="application/ld+json"> — a
    pre-escaped name reaches Google as the literal "J&amp;M Glass". Pre-escaping in
    config fixes the page and silently breaks the structured data, so it is rejected.
    """

    TEXT = ("biz", "tag", "city", "addr", "hours")

    def __init__(self, biz, tag, city, domain, *, addr="", phone="", phone_tel="",
                 email="", hours="", theme_color="#000000", fonts_href="",
                 css="styles.css?v=1", js="app.js?v=1", lang="en",
                 og_image=None, socials=(), schema_type="LocalBusiness", extra_head="",
                 no_publish=()):
        for name, value in (("biz", biz), ("tag", tag), ("city", city),
                            ("addr", addr), ("hours", hours)):
            if _ENTITY.search(value or ""):
                raise SystemExit(
                    f"Site {name}={value!r} contains an HTML entity.\n"
                    f"Write raw text (e.g. 'J&M Glass'). The engine escapes it for HTML and\n"
                    f"keeps it raw for JSON-LD; pre-escaping breaks the structured data."
                )
        # raw, for JSON-LD and anything else that is not HTML
        self.raw = {"biz": biz, "tag": tag, "city": city, "addr": addr, "hours": hours}
        # escaped, for interpolation into markup
        self.biz, self.tag, self.city, self.addr, self.hours = (
            escape(self.raw[k]) for k in self.TEXT)

        self.domain, self.base = domain, f"https://{domain}"
        self.phone, self.phone_tel, self.email = phone, phone_tel, email
        self.theme_color, self.fonts_href = theme_color, fonts_href
        self.css, self.js, self.lang = css, js, lang
        self.og_image = og_image or f"{self.base}/assets/og-image.jpg"
        self.socials = [s for s in socials if s]
        self.schema_type, self.extra_head = schema_type, extra_head
        # extra paths the live origin must not serve, appended to _config.yml
        self.no_publish = tuple(no_publish)

    # ---- SEO -----------------------------------------------------------------
    def canonical(self, path):
        # home canonicalises to the bare root: visitors land on "/", not "/index.html",
        # and pointing the canonical at the latter splits the homepage into two URLs.
        return f"{self.base}/" if path == "index.html" else f"{self.base}/{path}"

    def json_ld(self):
        """LocalBusiness structured data. Deliberately omits aggregateRating — adding it
        without real reviews is fabricated content (PLAYBOOK §4)."""
        parts = [p.strip() for p in self.raw["addr"].split(",")] if self.raw["addr"] else []
        region_zip = (parts[2] if len(parts) > 2 else "").split()
        data = {
            "@context": "https://schema.org",
            "@type": [self.schema_type],
            "@id": f"{self.base}/#business",
            "name": self.raw["biz"],
            "description": f'{self.raw["tag"]} in {self.raw["city"]}.',
            "url": f"{self.base}/",
            "image": self.og_image,
            "logo": f"{self.base}/assets/logo.png",
        }
        if self.phone_tel:
            data["telephone"] = self.phone_tel
        if self.email:
            data["email"] = self.email
        if parts:
            data["address"] = {
                "@type": "PostalAddress",
                "streetAddress": parts[0],
                "addressLocality": parts[1] if len(parts) > 1 else "",
                "addressRegion": region_zip[0] if region_zip else "",
                "postalCode": region_zip[1] if len(region_zip) > 1 else "",
                "addressCountry": "US",
            }
        if self.socials:
            data["sameAs"] = list(self.socials)
        return json.dumps(data, separators=(",", ":"))

    # ---- document envelope ---------------------------------------------------
    def head(self, title, desc, path="index.html", body_class="", theme_script=True):
        """Everything above <body>'s first visible element. No layout, no components.

        `title` and `desc` must already be escaped if they contain user text — compose
        them from self.biz / self.tag, which are.
        """
        canon = self.canonical(path)
        fonts = (f'<link rel="preconnect" href="https://fonts.googleapis.com">'
                 f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                 f'<link href="{self.fonts_href}" rel="stylesheet">') if self.fonts_href else ""
        # pre-paint theme restore. The MECHANISM is engine (no flash of wrong theme);
        # whether a site has a light/dark toggle at all, and what it looks like, is the
        # site's business.
        fouc = ('<script>(function(){try{var t=localStorage.getItem("theme");'
                'if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}})();</script>'
                ) if theme_script else ""
        return f'''<!doctype html>
<html lang="{self.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index,follow">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="{self.biz}">
<meta property="og:image" content="{self.og_image}">
<meta property="og:locale" content="en_US">
<meta name="theme-color" content="{self.theme_color}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{self.og_image}">
{fonts}
<link rel="stylesheet" href="{self.css}">
<script type="application/ld+json">{self.json_ld()}</script>
{self.extra_head}{fouc}
</head>
<body{f' class="{body_class}"' if body_class else ""}>
<a class="skip-link" href="#main">Skip to content</a>
'''

    def foot(self, defer_js=True):
        """Closes the document and loads the site's JS. Nothing visible."""
        js = f'<script src="{self.js}"{" defer" if defer_js else ""}></script>' if self.js else ""
        return f"{js}\n</body>\n</html>\n"

    def page(self, title, desc, path, body, body_class=""):
        """The whole document: engine head + the site's own markup + engine close.

        `body` is authored per site. The engine never wraps it in a container, so it
        imposes no layout — but it must contain an element with id="main" for the skip
        link to land on, which build() verifies.
        """
        return self.head(title, desc, path, body_class) + body + self.foot()


# ---- site-level files ------------------------------------------------------------
def sitemap(site, pages):
    today = date.today().isoformat()
    urls = "".join(
        f"<url><loc>{site.canonical(p)}</loc><lastmod>{today}</lastmod>"
        f"<priority>{'1.0' if p == 'index.html' else '0.8'}</priority></url>"
        for p in pages)
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'{urls}</urlset>')


def robots(site):
    return f"User-agent: *\nAllow: /\nSitemap: {site.base}/sitemap.xml\n"


# Everything in the repo that is NOT the published site. GitHub Pages runs Jekyll,
# which otherwise copies the whole repo to the live origin: on the jm-glass
# shakedown that would have served docs/research/competitors.md, gbp-reviews.md and
# the raw research JSON from the client's own domain. A site repo has to be public
# for Pages, so this does not hide anything from GitHub; it stops the client's
# DOMAIN from serving the working papers.
#
# Note on safety: files without YAML front matter are static to Jekyll, so the
# generated pages, CSS, JS and assets are copied byte for byte and no Liquid runs
# over them.
NOT_THE_SITE = [
    "docs/", "tools/", "worker/", "assets/src/", ".claude/", ".gate/",
    ".preflight-backup/", "Backups/", "__pycache__/", ".venv/",
    "*.py", "*.md", "*.sh", ".mcp.json", "Gemfile", "Gemfile.lock",
]


def pages_config(extra=()):
    """_config.yml — the Pages exclusion list. Mechanics, like robots.txt: it
    decides what the origin serves, never what anything looks like."""
    lines = ["# GENERATED by engine.build(). What the live origin must NOT serve.",
             "# Everything here stays in the repo; it simply is not published.",
             "exclude:"]
    for item in list(NOT_THE_SITE) + list(extra):
        lines.append(f'  - "{item}"')
    return "\n".join(lines) + "\n"


def build(site, pages, *, quiet=False):
    """Write every page plus sitemap/robots. `pages` maps filename -> callable."""
    for filename, render in pages.items():
        html = render()
        # the skip link is the engine's one a11y guarantee; it needs a target
        if 'id="main"' not in html:
            raise SystemExit(
                f'{filename}: no element with id="main". The engine emits a skip link to '
                f'#main, so every page needs that landmark (usually <main id="main">).')
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap(site, pages))
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots(site))
    with open("_config.yml", "w", encoding="utf-8") as f:
        f.write(pages_config(getattr(site, "no_publish", ())))
    if not quiet:
        print("built:", ", ".join(pages),
              "+ sitemap.xml, robots.txt, _config.yml")
