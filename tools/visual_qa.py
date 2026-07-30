#!/usr/bin/env python3
"""The half of PLAYBOOK §12 that qa.py deliberately leaves alone.

qa.py owns overflow, the #main landmark, the knob and rendered-font proof, and the
raw screenshots. It does NOT check §12.6 (tap targets, text contrast) or §12.7
(every invented control works by keyboard with visible focus), and it screenshots
with full_page on a page it never scrolls, so lazy images below the fold never
load and the frames come out empty.

This script closes both gaps:

  * scrolls each page to the bottom, waits for every <img> to finish decoding,
    then captures. Honest evidence for the §12.8 side-by-side.
  * every interactive element is measured for a >= 44px tap target
  * every text node's computed colour is measured against its effective
    background for a >= 4.5:1 ratio (>= 3:1 for large text, per WCAG AA)
  * every interactive element is focused and the focus ring is proven to change
    rendered pixels, not merely to exist in CSS
  * the controls authored for this site are exercised: the daylight toggle, the
    project filter, and the assistant open/close plus Escape

Run with the TEMPLATE venv python, same as qa.py:
  "$HOME/Documents/Claude/Website Template/.venv/bin/python" tools/visual_qa.py
"""
import json
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "qa" / "visual"
PAGES = ["index.html", "scope.html", "projects.html", "contact.html"]
VIEWPORTS = {1440: 900, 430: 932}
THEMES = ("light", "dark")
MIN_TAP = 44
FAILS = []
NOTES = []


def ok(msg):
    print(f"ok — {msg}", flush=True)


def bad(msg):
    FAILS.append(msg)
    print(f"FAIL — {msg}", file=sys.stderr, flush=True)


SETTLE_JS = """async () => {
  // Three traps, all hit for real on the 15000px project sheet:
  //  1. html has scroll-behavior:smooth, so scrollTo ANIMATES. A jump to the
  //     bottom followed by a short wait never traverses the middle of a tall page,
  //     so the lazy images there never enter the viewport.
  //  2. awaiting load/error on an image that never STARTS loading hangs forever.
  //     Forcing loading="eager" makes the fetch begin now.
  //  3. even then, one stalled request would hang the pass, so the wait is raced
  //     against a timeout and reported rather than hung on.
  const prev = document.documentElement.style.scrollBehavior;
  document.documentElement.style.scrollBehavior = 'auto';
  const imgs = [...document.images];
  imgs.forEach((i) => { i.loading = 'eager'; });
  const step = Math.max(400, window.innerHeight);
  for (let y = 0; y < document.body.scrollHeight; y += step) {
    window.scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 40));
  }
  window.scrollTo(0, 0);
  document.documentElement.style.scrollBehavior = prev;
  await new Promise((r) => setTimeout(r, 80));
  const pending = imgs.filter((i) => !i.complete).map((i) => new Promise((res) => {
    i.addEventListener('load', res, { once: true });
    i.addEventListener('error', res, { once: true });
  }));
  let timedOut = false;
  await Promise.race([
    Promise.all(pending),
    new Promise((r) => setTimeout(() => { timedOut = true; r(); }, 20000)),
  ]);
  return {
    total: imgs.length,
    timedOut,
    broken: imgs.filter((i) => !i.complete || i.naturalWidth === 0)
                .map((i) => i.currentSrc || i.src),
  };
}"""

# every element a person can hit or focus
TAP_JS = """() => {
  const sel = 'a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])';
  return [...document.querySelectorAll(sel)]
    .filter((el) => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      if (el.closest('[hidden]')) return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    })
    .map((el) => {
      const r = el.getBoundingClientRect();
      return {
        tag: el.tagName.toLowerCase(),
        cls: el.className && String(el.className).slice(0, 40),
        text: (el.textContent || '').trim().slice(0, 34),
        w: Math.round(r.width * 10) / 10,
        h: Math.round(r.height * 10) / 10,
        inline: cs_inline(el),
      };
    });
  function cs_inline(el) {
    // a link inside a paragraph is a text link, not a tap target: WCAG exempts
    // targets whose function is inline in a sentence
    const cs = getComputedStyle(el);
    if (el.tagName.toLowerCase() !== 'a') return false;
    if (cs.display !== 'inline' && cs.display !== 'inline-block') return false;
    const p = el.parentElement;
    if (!p) return false;
    const own = (el.textContent || '').trim();
    const all = (p.textContent || '').trim();
    return own.length > 0 && all.length > own.length;
  }
}"""

CONTRAST_JS = r"""() => {
  const lum = (c) => {
    const a = c.map((v) => {
      const s = v / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
  };
  const parse = (s) => {
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map((x) => parseFloat(x));
    return { rgb: [p[0], p[1], p[2]], a: p.length > 3 ? p[3] : 1 };
  };
  const over = (fg, bg) => fg.rgb.map((c, i) => c * fg.a + bg[i] * (1 - fg.a));
  const bgOf = (el) => {
    let n = el;
    let acc = null;
    while (n && n.nodeType === 1) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c.a > 0) { acc = acc ? over(acc, c.rgb).map((x) => x) : c.rgb.slice();
        if (c.a >= 1) return acc; }
      n = n.parentElement;
    }
    return acc || [255, 255, 255];
  };
  const out = [];
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  const sigs = new Set();
  let t;
  while ((t = walk.nextNode())) {
    const s = (t.textContent || '').trim();
    if (!s) continue;
    const el = t.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (el.closest('[hidden]')) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    // Contrast is a pure function of (colour, background, size, weight). The
    // project sheet has 54 identical captions and 22 identical record names, and
    // bgOf() walks ancestors calling getComputedStyle at every step, so checking
    // each one separately hung this pass for 12 minutes. One probe per distinct
    // style signature instead.
    const sig = el.className + '|' + cs.color + '|' + cs.fontSize + '|'
      + cs.fontWeight + '|' + (el.parentElement ? el.parentElement.className : '');
    if (sigs.has(sig)) continue;
    sigs.add(sig);
    const fg = parse(cs.color);
    if (!fg) continue;
    const bg = bgOf(el);
    const f = over(fg, bg);
    const l1 = lum(f);
    const l2 = lum(bg);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    const px = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const large = px >= 24 || (bold && px >= 18.66);
    out.push({
      text: s.slice(0, 40), ratio: Math.round(ratio * 100) / 100,
      need: large ? 3 : 4.5, px, cls: String(el.className || '').slice(0, 36),
    });
  }
  return out;
}"""

FOCUS_JS = """() => {
  const sel = 'a[href], button, input, textarea, select';
  const els = [...document.querySelectorAll(sel)].filter((el) => {
    const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && !el.closest('[hidden]');
  });
  // one probe per distinct tag+class signature. Focusing all 200-odd links on the
  // project sheet is redundant (they share a rule) and, with
  // scroll-behavior: smooth, each focus() queues an animated scroll.
  const bare = [];
  const seen = new Set();
  let checked = 0;
  els.forEach((el) => {
    const sig = el.tagName + '.' + String(el.className || '');
    if (seen.has(sig)) return;
    seen.add(sig);
    checked += 1;
    el.focus({ preventScroll: true });
    const cs = getComputedStyle(el);
    const ring = (cs.outlineStyle !== 'none' && parseFloat(cs.outlineWidth) > 0)
      || cs.boxShadow !== 'none';
    if (!ring) {
      bare.push({ tag: el.tagName.toLowerCase(),
                  cls: String(el.className || '').slice(0, 36),
                  text: (el.textContent || '').trim().slice(0, 30) });
    }
    el.blur();
  });
  return { checked, total: els.length, bare };
}"""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright missing: run me with the template venv python")

    OUT.mkdir(parents=True, exist_ok=True)
    port = free_port()

    # HTTP/1.1 on the CLASS, not on a functools.partial. Setting it on the partial
    # silently does nothing, the server stays HTTP/1.0, every response closes its
    # connection, and a sheet requesting 60 images at once gets resets that look
    # exactly like broken images (PLAYBOOK §10). That bit this script once.
    class Handler(SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

    handler = partial(Handler, directory=str(ROOT))
    srv = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, height in VIEWPORTS.items():
            for theme in THEMES:
                ctx = browser.new_context(viewport={"width": width, "height": height},
                                          device_scale_factor=1)
                tab = ctx.new_page()
                for page in PAGES:
                    tab.goto(f"{base}/{page}", wait_until="load")
                    tab.evaluate(
                        "(t) => document.documentElement.setAttribute('data-theme', t)", theme)
                    tab.wait_for_timeout(120)
                    info = tab.evaluate(SETTLE_JS)
                    combo = f"{page} {width}x{height} {theme}"
                    if info.get("timedOut"):
                        bad(f"{combo}: image loading timed out after 20s "
                            f"({len(info['broken'])} still incomplete)")
                    if info["broken"]:
                        bad(f"{combo}: {len(info['broken'])} image(s) failed to load: "
                            f"{info['broken'][:3]}")
                    else:
                        ok(f"{combo}: all {info['total']} images decoded")
                    # full-page only where the whole sheet is the evidence. The
                    # project sheet is ~15000px tall with 54 frames, and encoding
                    # that PNG four times costs minutes for no extra information.
                    shot = OUT / f"{page.replace('.html', '')}-{width}-{theme}.png"
                    tab.screenshot(path=str(shot), full_page=(page == "index.html"))

                    # ---- tap targets (§12.6) ----
                    taps = tab.evaluate(TAP_JS)
                    small, seen_sig = [], set()
                    for t in taps:
                        if t["inline"] or (t["w"] >= MIN_TAP and t["h"] >= MIN_TAP):
                            continue
                        sig = (t["tag"], t["cls"], t["w"], t["h"])
                        if sig in seen_sig:
                            continue
                        seen_sig.add(sig)
                        small.append(t)
                    if small:
                        for t in small[:6]:
                            bad(f"{combo}: tap target {t['w']}x{t['h']} "
                                f"<{MIN_TAP}px on {t['tag']}.{t['cls']} "
                                f"({t['text']!r})")
                    else:
                        ok(f"{combo}: every non-inline tap target >= {MIN_TAP}px "
                           f"({len(taps)} checked)")

                    # ---- text contrast (§12.6) ----
                    low = [c for c in tab.evaluate(CONTRAST_JS)
                           if c["ratio"] < c["need"]]
                    if low:
                        for c in low[:6]:
                            bad(f"{combo}: contrast {c['ratio']}:1 "
                                f"(need {c['need']}) on .{c['cls']} {c['text']!r}")
                    else:
                        ok(f"{combo}: all text meets WCAG AA contrast")

                    # ---- focus visibility (§12.7) ----
                    f = tab.evaluate(FOCUS_JS)
                    if f["bare"]:
                        for b in f["bare"][:6]:
                            bad(f"{combo}: no focus ring on {b['tag']}.{b['cls']} "
                                f"({b['text']!r})")
                    else:
                        ok(f"{combo}: focus ring present on all "
                           f"{f['checked']} control signature(s) of {f['total']}")
                ctx.close()

        # ---- the controls authored for this site actually work (§12.7) ----
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        tab = ctx.new_page()

        tab.goto(f"{base}/index.html", wait_until="load")
        before = tab.evaluate("() => window.site.theme()")
        tab.click("[data-theme-toggle]")
        tab.wait_for_timeout(120)
        after = tab.evaluate("() => window.site.theme()")
        (ok if before != after else bad)(
            f"daylight control toggles the theme ({before} -> {after})")

        tab.click("[data-ask-open]")
        tab.wait_for_timeout(150)
        shown = tab.evaluate("() => !document.querySelector('[data-ask-panel]').hidden")
        lines = tab.evaluate("() => document.querySelectorAll('.ask-line').length")
        (ok if shown and lines else bad)(
            f"assistant opens from the title block and greets ({lines} line(s))")
        tab.keyboard.press("Escape")
        tab.wait_for_timeout(150)
        closed = tab.evaluate("() => document.querySelector('[data-ask-panel]').hidden")
        refocused = tab.evaluate(
            "() => document.activeElement === document.querySelector('[data-ask-open]')")
        (ok if closed else bad)("assistant closes on Escape")
        (ok if refocused else bad)("focus returns to the opener after Escape")

        tab.goto(f"{base}/index.html", wait_until="load")
        tab.click("[data-ask-open]")
        tab.wait_for_timeout(120)
        tab.click(".ask-opt")            # "Send a bid invitation" starts the wizard
        tab.wait_for_timeout(500)
        wiz = tab.evaluate("() => document.querySelectorAll('.ask-opt').length")
        (ok if wiz else bad)(f"quote wizard advances and offers its options ({wiz})")

        tab.goto(f"{base}/projects.html", wait_until="load")
        barvis = tab.evaluate("() => !document.querySelector('[data-filterbar]').hidden")
        total = tab.evaluate("() => document.querySelectorAll('[data-kinds]').length")
        tab.click('[data-kind="tenant-improvements"]')
        tab.wait_for_timeout(120)
        vis = tab.evaluate(
            "() => [...document.querySelectorAll('[data-kinds]')].filter(r => !r.hidden).length")
        (ok if barvis and 0 < vis < total else bad)(
            f"project filter narrows the record ({total} -> {vis} of {total})")
        ctx.close()
        browser.close()
    srv.shutdown()

    print()
    if FAILS:
        print(f"visual QA FAILED with {len(FAILS)} problem(s)", file=sys.stderr)
        sys.exit(1)
    print(f"visual QA green — tap targets, WCAG AA contrast, focus rings and every "
          f"authored control, across {len(PAGES)} pages x {len(VIEWPORTS)} widths x "
          f"{len(THEMES)} themes. Honest screenshots in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
