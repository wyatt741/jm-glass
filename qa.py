#!/usr/bin/env python3
"""Browser QA gate — PLAYBOOK §12.5-7 scripted, plus the §9b knob verification.

Runs inside a SITE repo (copied there by preflight), after build.py. Playwright
lives in the TEMPLATE repo's venv, so run me with that python — gate.py --ship
does this for you:

    <template>/.venv/bin/python qa.py        (macOS)
    <template>/.venv/Scripts/python.exe qa.py (Windows)

Why this is a script and not "open the browser and look":

- Serves the cwd on its OWN http.server, on a free 127.0.0.1 port — never
  file:// (it hangs the browser pane, SESSION_STATE 2026-07-26-2) — and proves
  liveness with a plain HTTP GET before any browser is driven blind.
- Headless Chromium over every generated page x widths {1440, 430} x themes
  {light, dark}, the theme set the way app.js sets it (the data-theme
  attribute on <html>, which also pins color-scheme). Per combo:
    - no horizontal overflow: scrollWidth <= clientWidth + 1 on html AND body
    - the #main landmark exists (the skip link's target; the engine refuses
      to build without it, this catches anything hand-made sneaking past)
    - a screenshot to docs/qa/<UTC-stamp>/<page>-<width>-<theme>.png — the
      raw material for the §12.8 side-by-side.
- Knob verification per §9b: every knob in docs/direction.json compared
  against getComputedStyle(document.documentElement) on a freshly LOADED page.
  The values are already in :root at parse time on purpose — mutating a custom
  property at runtime reads stale on animated elements.
- Rendered-font proof (fixplan 2026-07-29 ruling 10): the computed font-family
  of <body> must start with --font-body's first family, and of the <h1> with
  --font-display's. A knob that is declared but never RENDERS is a dead
  declaration — the page ships in system-ui (or worse) while every string
  compare stays green. This is the check that catches it.

Second mode — the §12.8 composite (fixplan ruling 9):

    qa.py --compose out.png <dir-or-png> <dir-or-png> [...]

  A simple horizontal strip: one labelled panel per source (a directory gives
  its index-1440-light.png if present, else its first *.png), for the
  side-by-side judgement vs the two nearest registry sites. Needs Pillow,
  which is pinned in the template venv. That's all it does on purpose.

Exit 0 green / 1 fail. One line per assertion, so the log IS the evidence.
"""
import json, sys, threading, time, urllib.request
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VENV_HINT = ("run me with the template venv's python:\n"
             "  <template>/.venv/bin/python qa.py        (macOS)\n"
             "  <template>/.venv/Scripts/python.exe qa.py (Windows)")

VIEWPORTS = {1440: 900, 430: 932}   # §12.5 — desktop and iPhone-class
THEMES = ("light", "dark")

OVERFLOW_JS = """() => {
  const de = document.documentElement, b = document.body;
  return { html: [de.scrollWidth, de.clientWidth], body: [b.scrollWidth, b.clientWidth] };
}"""
KNOBS_JS = """(names) => {
  const cs = getComputedStyle(document.documentElement);
  return Object.fromEntries(names.map(n => [n, cs.getPropertyValue(n)]));
}"""
FONTS_JS = """() => {
  const h1 = document.querySelector('h1');
  return { body: getComputedStyle(document.body).fontFamily,
           h1: h1 ? getComputedStyle(h1).fontFamily : null };
}"""

FAILURES = []


def ok(msg):
    print(f"ok — {msg}")


def bad(msg):
    FAILURES.append(msg)
    print(f"FAIL — {msg}", file=sys.stderr)


def serve(root: Path):
    """The site on its own throwaway server; port 0 lets the OS pick a free one."""
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *_):
            pass
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(root)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def liveness(base: str, first: str):
    url = f"{base}/{first}"
    for _ in range(20):
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return url
        except OSError:
            time.sleep(0.15)
    sys.exit(f"qa: server never answered at {url} — refusing to drive the browser blind")


def norm(v: str) -> str:
    """Whitespace-insensitive compare: computed custom properties keep the authored
    token stream, but browsers disagree about the spaces around it."""
    return " ".join(str(v).split())


def first_family(stack) -> str:
    """First family of a CSS font stack, unquoted, case-folded — the family the
    browser actually tries first, however the rest of the fallbacks are spelled."""
    return str(stack).split(",")[0].strip().strip("'\"").strip().lower()


def check_combos(browser, base: str, pages, shots: Path, root: Path):
    for width, height in VIEWPORTS.items():
        ctx = browser.new_context(viewport={"width": width, "height": height})
        tab = ctx.new_page()
        for pagefile in pages:
            tab.goto(f"{base}/{pagefile.name}", wait_until="load")
            for theme in THEMES:
                # exactly app.js's mechanism: data-theme on <html>
                tab.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
                tab.wait_for_timeout(120)  # let the variable swap paint
                combo = f"{pagefile.name} {width}x{height} {theme}"

                o = tab.evaluate(OVERFLOW_JS)
                wide = [f"{el} {sw}>{cw}+1" for el, (sw, cw) in o.items() if sw > cw + 1]
                if wide:
                    bad(f"{combo}: horizontal overflow — {', '.join(wide)}")
                else:
                    ok(f"{combo}: no horizontal overflow "
                       f"(html {o['html'][0]}/{o['html'][1]}, body {o['body'][0]}/{o['body'][1]})")

                if tab.evaluate("() => !!document.getElementById('main')"):
                    ok(f"{combo}: #main landmark present")
                else:
                    bad(f"{combo}: #main landmark missing")

                shot = shots / f"{pagefile.stem}-{width}-{theme}.png"
                tab.screenshot(path=str(shot), full_page=True)
                ok(f"{combo}: screenshot {shot.relative_to(root)}")
        ctx.close()


def check_knobs(browser, base: str, pages, root: Path) -> int:
    direction = root / "docs" / "direction.json"
    if not direction.exists():
        bad("docs/direction.json missing — derive the direction (§9) before QA")
        return 0
    try:
        knobs = json.loads(direction.read_text()).get("knobs", {})
    except json.JSONDecodeError as e:
        bad(f"docs/direction.json does not parse: {e}")
        return 0
    if not knobs:
        bad("docs/direction.json has an empty knobs map — nothing to verify")
        return 0

    # A fresh load, no runtime mutation: the §9b rule. Any page carries :root.
    landing = next((p for p in pages if p.name == "index.html"), pages[0])
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    tab = ctx.new_page()
    tab.goto(f"{base}/{landing.name}", wait_until="load")
    computed = tab.evaluate(KNOBS_JS, list(knobs))
    rendered = tab.evaluate(FONTS_JS)
    ctx.close()

    for name, want in knobs.items():
        got = computed.get(name, "")
        if norm(want) == norm(got):
            ok(f"knob {name}: computed '{norm(got)}' matches direction.json")
        else:
            bad(f"knob {name}: direction.json '{want}' but computed "
                f"'{norm(got) or '<unset>'}' — styles.css :root and the "
                f"derivation disagree")

    # Ruling 10: declared is not rendered. The base consumes the font knobs, so
    # the page's COMPUTED fonts must lead with the derived families — this fails
    # a knob pair that is declared in :root and then never reaches an element.
    for knob, element in (("--font-body", "body"), ("--font-display", "h1")):
        want = knobs.get(knob)
        if want is None:
            bad(f"rendered font: {knob} missing from direction.json knobs — "
                f"the font pair is a required part of the derivation")
            continue
        got = rendered.get(element)
        if got is None:
            bad(f"rendered font: {landing.name} has no <{element}> to verify "
                f"{knob} against")
        elif first_family(got) == first_family(want):
            ok(f"rendered font: {element} computes '{first_family(got)}' — "
               f"{knob} is consumed, not just declared")
        else:
            bad(f"rendered font: {element} computes '{got}' but {knob} says "
                f"'{want}' — the knob is declared, never rendered (dead "
                f"declaration or a later override wins)")
    return len(knobs)


def compose(args):
    """qa.py --compose out.png <dir-or-png> <dir-or-png> [...] — the §12.8 strip.

    One labelled panel per source, pasted left to right at a common height.
    Deliberately nothing more: the judgement happens in Wyatt's eyes, not here."""
    if len(args) < 3:
        sys.exit("qa --compose: usage: qa.py --compose out.png <dir-or-png> <dir-or-png> [...]")
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        sys.exit(f"qa --compose: Pillow not importable — {VENV_HINT}")

    LABEL_H, GAP = 36, 12
    panels = []
    for src in args[1:]:
        p = Path(src)
        if p.is_dir():
            pngs = sorted(p.glob("*.png"))
            if not pngs:
                sys.exit(f"qa --compose: no *.png in {p}")
            pick = next((f for f in pngs if f.name == "index-1440-light.png"), pngs[0])
            label = p.name
        elif p.is_file() and p.suffix.lower() == ".png":
            pick, label = p, p.stem
        else:
            sys.exit(f"qa --compose: {p} is neither a directory nor a .png")
        panels.append((label, Image.open(pick).convert("RGB")))

    height = min(im.height for _, im in panels)
    scaled = [(label, im.resize((max(1, round(im.width * height / im.height)), height)))
              for label, im in panels]
    width = sum(im.width for _, im in scaled) + GAP * (len(scaled) - 1)
    strip = Image.new("RGB", (width, height + LABEL_H), "white")
    draw = ImageDraw.Draw(strip)
    x = 0
    for label, im in scaled:
        draw.text((x + 8, 10), label, fill="black")
        strip.paste(im, (x, LABEL_H))
        x += im.width + GAP
    out = Path(args[0])
    out.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out)
    print(f"ok — composite {out}: {len(scaled)} panels ({', '.join(l for l, _ in scaled)})")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--compose":
        compose(sys.argv[2:])
        return

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(f"qa: playwright not importable — {VENV_HINT}")

    root = Path.cwd()
    pages = sorted(root.glob("*.html"))
    if not pages:
        sys.exit("qa: no generated *.html — run build.py first")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    shots = root / "docs" / "qa" / stamp
    shots.mkdir(parents=True, exist_ok=True)

    srv, base = serve(root)
    try:
        url = liveness(base, pages[0].name)
        ok(f"server live at {base} (HTTP 200 on {url})")
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            check_combos(browser, base, pages, shots, root)
            n_knobs = check_knobs(browser, base, pages, root)
            browser.close()
    finally:
        srv.shutdown()

    if FAILURES:
        print(f"FAIL qa ({len(FAILURES)}):", file=sys.stderr)
        for f in FAILURES:
            print(f"  - {f}", file=sys.stderr)
        sys.exit(1)
    ok(f"qa green: {len(pages)} pages x {len(VIEWPORTS)} widths x {len(THEMES)} themes, "
       f"{n_knobs} knobs verified, screenshots in {shots.relative_to(root)}")


if __name__ == "__main__":
    main()
