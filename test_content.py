#!/usr/bin/env python3
"""Content gate — fabrication and copy-discipline tripwires on the GENERATED pages.

Run after build.py, in the site repo. Checks (2026-07-28 audit, steps 4 + taste
gap; hardened 2026-07-29 against red-team fixtures a8/a9/a10/a15):

- No em/en dashes in rendered text (PLAYBOOK §4 — the tell of unedited LLM
  copy). Pages are parsed with the stdlib HTMLParser, which unescapes entities,
  so &mdash; / &#8212; / &#x2014; count as dashes too.
- Zero <style> elements and zero style attributes in ANY encoding — STYLE=,
  style =, single-quoted values, <STYLE> — all styling belongs in styles.css.
- aggregateRating / review JSON-LD requires docs/REVIEWS_SOURCE.md that PARSES:
  one source line per counted review, and the source-line count must equal the
  claimed reviewCount. A missing, zero-byte, or short file is fabrication and
  FAILS.
- SAMPLE-marked content may ship; unmarked placeholder assets may not. The ONLY
  recognised markers are machine markers on the element itself: a `data-sample`
  attribute, or an `<!-- SAMPLE -->` comment immediately preceding the tag.
  Nearby copy that merely contains the word SAMPLE does not count.
- SHIPPED JS COPY (2026-07-30, jm-glass shakedown): the string literals in app.js
  and worker/worker.js are checked for the same discipline as the HTML. Copy that a
  site renders from JavaScript, or feeds to a chatbot as its system prompt, is
  never in the generated pages, so every check above used to miss it. On the
  shakedown that blind spot shipped a chat chip contradicting the page it sat on,
  a stale "travel centre", and a Worker still carrying 555-555-5555 and
  PLACEHOLDER-domain.com. Checked: em/en dashes, template placeholder residue, and
  unreplaced TODO markers.
- Hero visual (taste-critic gap): index.html's FIRST <section> must carry a
  real visual — an <img>/<video> with a declared width or height >= 480 (and,
  for img, a real alt text), or an inline <svg> with a viewBox and actual
  content. A 1x1 spacer, a 0x0 empty svg, or a page with no <section> FAILS.
"""
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path

DASHES = re.compile(r'[—–]')

# ---- shipped JS copy ----------------------------------------------------------
# Files whose string literals reach a human: rendered into the page by script, or
# handed to an LLM as its system prompt.
JS_TARGETS = ("app.js", "worker/worker.js")
# Residue from the template's own placeholders. Every one of these shipped for real
# on the shakedown because no gate looked inside a .js file.
JS_PLACEHOLDERS = re.compile(
    r'PLACEHOLDER|\bTODO\b|\bFIXME\b|lorem ipsum|555-555-5555|example\.com'
    r'|BUSINESS NAME|yourdomain|SITE-chat|\bacme\b', re.I)
JS_QUOTES = "'\"`"


def js_literals(text):
    """Every string literal in the source, comments skipped.

    A single pass, because stripping comments first is wrong: `https://` contains
    `//`, so a regex comment-stripper blanks the rest of any line holding a URL and
    the scan goes blind to placeholder domains, which is the main thing it is for.
    Not a full JS parser (no regex-literal handling), but it tracks strings,
    template literals, line comments and block comments, which is what decides
    whether a `//` opens a comment or sits inside a string.
    """
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        # comments, but only when NOT inside a string (we never are, here)
        if c == "/" and i + 1 < n:
            if text[i + 1] == "/":
                j = text.find("\n", i)
                i = n if j < 0 else j + 1
                continue
            if text[i + 1] == "*":
                j = text.find("*/", i + 2)
                i = n if j < 0 else j + 2
                continue
        if c in JS_QUOTES:
            quote = c
            i += 1
            buf = []
            while i < n:
                ch = text[i]
                if ch == "\\":            # escape: take the next char verbatim
                    buf.append(text[i:i + 2])
                    i += 2
                    continue
                if ch == quote:
                    i += 1
                    break
                if ch == "\n" and quote != "`":
                    break                 # unterminated single/double quote
                buf.append(ch)
                i += 1
            yield "".join(buf)
            continue
        i += 1


def check_js(failures):
    """The same copy discipline the pages get, applied to shipped JS."""
    checked = 0
    for rel in JS_TARGETS:
        f = Path.cwd() / rel
        if not f.exists():
            continue
        checked += 1
        text = f.read_text(errors="replace")
        for lit in js_literals(text):
            if not lit.strip():
                continue
            # a literal that is ABOUT dashes may name them: the Worker's own house
            # rule says "NEVER use em dashes (—)". Anything else may not.
            if DASHES.search(lit) and "dash" not in lit.lower():
                failures.append(f"{rel}: em/en dash in a shipped string: "
                                f"...{lit.strip()[:70]}...")
            m = JS_PLACEHOLDERS.search(lit)
            if m:
                failures.append(f"{rel}: template placeholder {m.group(0)!r} still in "
                                f"a shipped string: ...{lit.strip()[:70]}...")
    return checked
PLACEHOLDER = re.compile(r'placeholder', re.I)
MIN_VISUAL = 480   # minimum declared px on the hero img/video
MIN_ALT = 2        # rejects '', '.', and other single-char alt text


class PageScan(HTMLParser):
    """One pass over a generated page.

    Collects: inline-style offences, <style> elements, rendered text (outside
    script/style, entities already unescaped) for the dash scan, placeholder
    src/href values with their SAMPLE-marker status, JSON-LD payloads, and a
    hero-visual inventory of the page's first <section>.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inline_styles = []    # descriptions of style="…" offences
        self.style_elements = 0    # count of <style> tags
        self.text_parts = []       # rendered text for the dash scan
        self.placeholders = []     # (value, marked) for placeholder src/href
        self.ldjson = []           # raw JSON-LD script payloads
        self.saw_section = False
        self.hero_visuals = []     # img/video/svg found in the first <section>
        self._skip = []            # open script/style tags (text excluded)
        self._in_ldjson = False
        self._pending_sample = False   # an <!-- SAMPLE --> was just seen
        self._in_first = False         # inside index's first <section>
        self._first_done = False
        self._sec_depth = 0
        self._svg_depth = 0
        self._svg_children = 0
        self._svg_viewbox = False
        self._svg_in_first = False

    def handle_starttag(self, tag, attrs):
        ad = {}
        for k, v in attrs:
            ad.setdefault(k.lower(), v if v is not None else "")
        consumed_sample = self._pending_sample
        self._pending_sample = False

        if "style" in ad:
            self.inline_styles.append(f'<{tag} style="{ad["style"][:40]}">')
        if tag == "style":
            self.style_elements += 1
        if tag in ("script", "style"):
            self._skip.append(tag)
            if tag == "script" and ad.get("type", "").lower() == "application/ld+json":
                self._in_ldjson = True
                self._ld_buf = []

        for key in ("src", "href"):
            val = ad.get(key, "")
            if val and PLACEHOLDER.search(val):
                marked = "data-sample" in ad or consumed_sample
                self.placeholders.append((val, marked))

        if tag == "svg":
            if self._svg_depth == 0:
                self._svg_viewbox = "viewbox" in ad
                self._svg_children = 0
                self._svg_in_first = self._in_first
            else:
                self._svg_children += 1
            self._svg_depth += 1
        elif self._svg_depth:
            self._svg_children += 1

        if tag == "section":
            self.saw_section = True
            if not self._first_done and not self._in_first:
                self._in_first = True
                self._sec_depth = 0
            elif self._in_first:
                self._sec_depth += 1

        if self._in_first:
            if tag == "img":
                self.hero_visuals.append({
                    "tag": "img", "w": ad.get("width"), "h": ad.get("height"),
                    "alt": ad.get("alt")})
            elif tag == "video":
                self.hero_visuals.append({
                    "tag": "video", "w": ad.get("width"), "h": ad.get("height")})

    def handle_endtag(self, tag):
        self._pending_sample = False
        if self._skip and tag == self._skip[-1]:
            self._skip.pop()
        if tag == "script" and self._in_ldjson:
            self.ldjson.append("".join(self._ld_buf))
            self._in_ldjson = False
        if tag == "svg" and self._svg_depth:
            self._svg_depth -= 1
            if self._svg_depth == 0 and self._svg_in_first:
                self.hero_visuals.append({
                    "tag": "svg", "viewbox": self._svg_viewbox,
                    "children": self._svg_children})
        if tag == "section" and self._in_first:
            if self._sec_depth == 0:
                self._in_first = False
                self._first_done = True
            else:
                self._sec_depth -= 1

    def handle_data(self, data):
        if self._in_ldjson:
            self._ld_buf.append(data)
        if not self._skip:
            self.text_parts.append(data)
        if data.strip():
            self._pending_sample = False

    def handle_comment(self, data):
        # the ONLY comment marker that waives a placeholder: <!-- SAMPLE -->
        # immediately before the element (whitespace-only text in between).
        self._pending_sample = data.strip().upper() == "SAMPLE"


def _int(value):
    try:
        return int(str(value).strip().rstrip("px").strip())
    except (TypeError, ValueError):
        return 0


def hero_ok(visuals):
    for v in visuals:
        if v["tag"] == "img":
            alt = (v.get("alt") or "").strip()
            if max(_int(v["w"]), _int(v["h"])) >= MIN_VISUAL and len(alt) >= MIN_ALT:
                return True
        elif v["tag"] == "video":
            if max(_int(v["w"]), _int(v["h"])) >= MIN_VISUAL:
                return True
        elif v["tag"] == "svg":
            if v["viewbox"] and v["children"] > 0:
                return True
    return False


def _rating_claims(node, claims):
    """Walk parsed JSON-LD; collect (kind, count) for every rating claim."""
    if isinstance(node, dict):
        if "aggregateRating" in node:
            agg = node["aggregateRating"]
            if isinstance(agg, dict):
                claims.append(("aggregateRating",
                               agg.get("reviewCount", agg.get("ratingCount"))))
            else:
                claims.append(("aggregateRating", None))
        rev = node.get("review")
        if isinstance(rev, list):
            claims.append(("review-list", len(rev)))
        elif isinstance(rev, dict):
            claims.append(("review-list", 1))
        for v in node.values():
            _rating_claims(v, claims)
    elif isinstance(node, list):
        for v in node:
            _rating_claims(v, claims)


def review_sources():
    """Parse docs/REVIEWS_SOURCE.md into source lines.

    Returns None when the file does not exist; otherwise the list of source
    lines (non-blank, non-heading; markdown bullets stripped) — one line is
    expected per counted review.
    """
    f = Path.cwd() / "docs" / "REVIEWS_SOURCE.md"
    if not f.exists():
        return None
    lines = []
    for raw in f.read_text(errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.lstrip("-*> ").strip()
        if line:
            lines.append(line)
    return lines


def check_ratings(page_name, scan, failures):
    claims = []
    for payload in scan.ldjson:
        try:
            ld = json.loads(payload)
        except json.JSONDecodeError:
            continue  # test_seo owns JSON-LD validity
        _rating_claims(ld, claims)
    if not claims:
        return
    sources = review_sources()
    if sources is None:
        failures.append(
            f"{page_name}: aggregateRating/review JSON-LD without "
            f"docs/REVIEWS_SOURCE.md — fabricated stats never ship (§4)")
        return
    if not sources:
        failures.append(
            f"{page_name}: docs/REVIEWS_SOURCE.md parses to zero source lines — "
            f"one source line per counted review is required (§4)")
        return
    for kind, count in claims:
        if kind == "aggregateRating":
            n = _int(count)
            if n <= 0:
                failures.append(
                    f"{page_name}: aggregateRating without a parseable "
                    f"reviewCount/ratingCount — unverifiable stats never ship (§4)")
            elif n != len(sources):
                failures.append(
                    f"{page_name}: reviewCount {n} but docs/REVIEWS_SOURCE.md "
                    f"lists {len(sources)} source line(s) — one source line per "
                    f"counted review (§4)")
        elif kind == "review-list" and count > len(sources):
            failures.append(
                f"{page_name}: {count} review objects in JSON-LD but only "
                f"{len(sources)} source line(s) in docs/REVIEWS_SOURCE.md (§4)")


def fail_list():
    failures = []
    pages = sorted(Path.cwd().glob("*.html"))
    if not pages:
        sys.exit("test_content: no generated *.html — run build.py first")

    for page in pages:
        scan = PageScan()
        scan.feed(page.read_text(errors="replace"))
        scan.close()

        for offence in scan.inline_styles:
            failures.append(
                f"{page.name}: inline {offence}… (styling belongs in styles.css)")
        for _ in range(scan.style_elements):
            failures.append(
                f"{page.name}: <style> element (styling belongs in styles.css)")

        text = " ".join(scan.text_parts)
        m = DASHES.search(text)
        if m:  # one per page is enough to fail
            ctx = text[max(0, m.start() - 30):m.end() + 30].strip()
            failures.append(f"{page.name}: em/en dash in copy: …{ctx}…")

        for value, marked in scan.placeholders:
            if not marked:
                failures.append(
                    f"{page.name}: unmarked placeholder asset {value} — mark the "
                    f"element itself with data-sample or an immediately-preceding "
                    f"<!-- SAMPLE --> comment")

        check_ratings(page.name, scan, failures)

        if page.name == "index.html":
            if not scan.saw_section:
                failures.append(
                    "index.html: no <section> on the page — the hero must live "
                    "in an opening section, not degrade to a text tile")
            elif not hero_ok(scan.hero_visuals):
                failures.append(
                    "index.html: no qualifying visual in the opening section — "
                    "a hero needs an img/video with declared width/height >= "
                    f"{MIN_VISUAL} and a real alt, or an inline svg with a "
                    "viewBox and content; spacers do not count")

    js_checked = check_js(failures)
    return failures, len(pages), js_checked


def main():
    failures, n, js_checked = fail_list()
    if failures:
        print(f"FAIL test_content ({len(failures)}):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        sys.exit(1)
    print(f"ok — {n} pages: no inline styling (any encoding), no dash-copy "
          f"(entities included), no unmarked placeholders, rating claims match "
          f"docs/REVIEWS_SOURCE.md, hero visual real")
    print(f"     + {js_checked} shipped JS file(s): no dash-copy, no placeholder "
          f"residue in any string a visitor or a chatbot ever sees")


if __name__ == "__main__":
    main()
