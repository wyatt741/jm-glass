#!/usr/bin/env python3
"""Capture the prior-art panels for the §12.8 side-by-side judgement.

RUN.md phase 6 wants the TWO nearest registry sites, read off test_unique.py's
`overlap <name>: N` lines with ties broken by registry order. This run scores 0
against all five, so the tie-break decides: anderson-it, then andersontech-site.
bwraps is captured as a third panel because KICKOFF names it explicitly as the
site to hold this one against.

anderson-it is live and is captured from its real URL. The other two have no live
URL in the registry, so they are served from their own repos on a local port,
which is the same HTML.

Run with the template venv python (Playwright lives there):
  "$HOME/Documents/Claude/Website Template/.venv/bin/python" tools/capture_peers.py
"""
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT.parent
OUT = ROOT / "docs" / "qa" / "peers"

LIVE = [("anderson-it", "https://andersontechsupport.com/")]
LOCAL = [("andersontech-site", PROJECTS / "andersontech-site"),
         ("bwraps", PROJECTS / "bwraps")]

# consent banners, age gates and modals must be gone BEFORE the shot (RUN.md)
DISMISS_JS = """() => {
  const killers = [
    '.agegate', '#agegate', '[class*="cookie"]', '[id*="cookie"]',
    '[class*="consent"]', '[id*="consent"]', '[class*="gdpr"]',
    '[class*="age-gate"]', '[role="dialog"]', '.modal', '.overlay',
  ];
  let removed = 0;
  killers.forEach((s) => document.querySelectorAll(s).forEach((el) => {
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed' || cs.position === 'absolute'
        || parseInt(cs.zIndex || '0', 10) > 50) { el.remove(); removed += 1; }
  }));
  document.documentElement.style.overflow = 'auto';
  document.body.style.overflow = 'auto';
  return removed;
}"""

SETTLE_JS = """async () => {
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise((r) => setTimeout(r, 500));
  window.scrollTo(0, 0);
  await new Promise((r) => setTimeout(r, 200));
  await Promise.all([...document.images].map((i) => i.complete ? null
    : new Promise((res) => {
        i.addEventListener('load', res, { once: true });
        i.addEventListener('error', res, { once: true });
      })));
  return document.images.length;
}"""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(directory):
    class Handler(SimpleHTTPRequestHandler):
        protocol_version = "HTTP/1.1"      # keep-alive, or a gallery resets

        def log_message(self, *a):
            pass

    port = free_port()
    srv = ThreadingHTTPServer(("127.0.0.1", port),
                              partial(Handler, directory=str(directory)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{port}/index.html"


def main():
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    shots = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  device_scale_factor=1)
        tab = ctx.new_page()

        for name, url in LIVE:
            try:
                tab.goto(url, wait_until="load", timeout=45000)
                tab.wait_for_timeout(700)
                gone = tab.evaluate(DISMISS_JS)
                tab.evaluate(SETTLE_JS)
                path = OUT / f"{name}-1440-light.png"
                tab.screenshot(path=str(path), full_page=False)
                shots.append(path)
                print(f"ok — {name} captured from {url} ({gone} overlay(s) dismissed)")
            except Exception as e:
                print(f"FAIL — {name} at {url}: {e}", file=sys.stderr)

        for name, directory in LOCAL:
            if not (directory / "index.html").exists():
                print(f"FAIL — {name}: no index.html at {directory}", file=sys.stderr)
                continue
            srv, url = serve(directory)
            try:
                tab.goto(url, wait_until="load", timeout=30000)
                tab.wait_for_timeout(500)
                gone = tab.evaluate(DISMISS_JS)
                tab.evaluate(SETTLE_JS)
                path = OUT / f"{name}-1440-light.png"
                tab.screenshot(path=str(path), full_page=False)
                shots.append(path)
                print(f"ok — {name} captured from its own repo "
                      f"({gone} overlay(s) dismissed)")
            finally:
                srv.shutdown()
        browser.close()
    print(f"\n{len(shots)} peer panel(s) in {OUT.relative_to(ROOT)}")
    for s in shots:
        print(f"  {s.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
