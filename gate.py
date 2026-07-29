#!/usr/bin/env python3
"""The gate — one command between "it builds" and "it may ship".  python3 gate.py [--ship]

Runs inside a SITE repo (preflight copies it there with the engine set). This is
the spine of the v2 runner (docs/AUDIT_SYNTHESIS_2026-07-28.md, step 6): every
automated check in one ordered chain, stopping at the first failure, so "green"
means exactly one thing.

Default chain, in order, each script a subprocess showing its own output, then
two in-process checks:

    build.py -> test_seo.py -> test_knobs.py -> test_content.py
             -> test_unique.py -> stylesheet check -> direction check

The stylesheet check refuses any generated page (or any linted sheet's @import)
that references a stylesheet outside the LINT SET — every local .css in the
repo, the same set test_knobs.py lints via css_lint_set(). A second stylesheet
can no longer sit out the lint, and a remote sheet can never style a shipped
page (red-team a3).

The direction check closes audit break #3 — a pristine, direction-less checkout
used to pass every gate green. docs/direction.json must exist, carry every
required knob with non-empty reasoning, string-equal the styles.css winning
:root-level declaration, and demonstrably leave neutral. Hardened per the
2026-07-29 fix plan:
  - NEUTRAL comparison canonicalises numerics and font stacks first, so
    visually-null respellings (0.0px, 1.20, #000, 'system-ui, sans-serif')
    still read as neutral, and --accent-rgb needs a perceptual distance from
    black, not string inequality (a1);
  - EVERY selector that can match the root element (:root, html, :root:root,
    :where(:root), :root[data-theme]...) is read, most specific/last wins, so
    a trailing override cannot lie to the gate (a2a);
  - the load-bearing knobs (--accent-rgb or --accent, --font-display,
    --font-body, --r-pill, --motion) must each be CONSUMED — >= 1 var(<knob>)
    reference in styles.css, comments stripped (ruling 4). Declared-and-unused
    is not a direction (a2b).

--ship runs the default chain plus qa.py (template venv python — Playwright is
pinned there, never the system python3) and, on green, stamps .gate/HASH:

    line 1: HMAC-SHA256(.git/gate.key, tree digest), where the tree digest is
            sha256 over sorted "<relpath><TAB><sha256(bytes)>" lines for EVERY
            file in the shippable tree: everything under the site root EXCEPT
            .git/, .gate/, docs/qa/ (minus the tracked docs/qa/side-by-side/
            evidence), __pycache__/, .preflight-backup/, .claude/ (and
            .DS_Store junk files)
    line 2: ISO-8601 UTC timestamp

The key (.git/gate.key, 32 random bytes) is created by `preflight --start` and
never committed; gate.py --ship creates it lazily for pre-existing sites. The
HMAC binds the stamp to a gate RUN in this repo, not to content alone: knowing
the tree digest is no longer enough to forge a stamp (a5), and because the
digest covers the WHOLE tree, a post-gate file added anywhere — a subdirectory
page included — breaks verification (a4); there is no mtime backstop to touch.
THREAT MODEL (ruling 1): a sloppy agent skipping the gate, not a hostile human
with repo access — anyone who can read .git/gate.key could stamp, and that
person could also just push.

ship.py imports compute_tree_digest / verify_hash from THIS file (ruling 3) —
never a mirrored copy, which is how the old plain digest drifted — so gate.py
stays import-safe (no side effects at import time) AND runnable as a script.

.gate/HASH exists ONLY after a green --ship run; ANY gate failure deletes a
stale one. Exit 0 green / 1 fail. No flags beyond --ship.
"""
import hashlib
import hmac
import json
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HASH_FILE = ROOT / ".gate" / "HASH"
KEY_FILE = ROOT / ".git" / "gate.key"

HEX64 = re.compile(r"[0-9a-f]{64}")

CHAIN = ("build.py", "test_seo.py", "test_knobs.py", "test_content.py", "test_unique.py")

REQUIRED_KNOBS = (
    "--accent", "--accent-deep", "--accent-soft", "--accent-rgb",
    "--accent-soft-rgb", "--shadow-rgb", "--glow-a", "--motion",
    "--r", "--r-pill", "--h-weight", "--h-track", "--h-track-hero",
    "--h-leading", "--font-display", "--font-body")

# ruling 4: knobs that must be CONSUMED, not just declared (a2b). Each tuple
# lists the accepted spellings; >= 1 var(<knob>) reference satisfies the knob.
USAGE_REQUIRED = (("--accent-rgb", "--accent"), ("--font-display",),
                  ("--font-body",), ("--r-pill",), ("--motion",))

# the template styles.css neutral literals — the absence of a direction
NEUTRAL = {
    "--accent": "#000000", "--accent-deep": "#000000", "--accent-soft": "#000000",
    "--accent-rgb": "0, 0, 0", "--accent-soft-rgb": "0, 0, 0", "--shadow-rgb": "0, 0, 0",
    "--glow-a": "0", "--motion": "1",
    "--r": "0px", "--r-pill": "0px",
    "--h-weight": "500", "--h-track": "0", "--h-track-hero": "0", "--h-leading": "1.2",
    "--font-display": "system-ui", "--font-body": "system-ui",
}

# generic/system families — a stack made only of these is a neutral, not a choice
GENERIC_FONTS = {
    "system-ui", "sans-serif", "serif", "monospace", "cursive", "fantasy",
    "math", "emoji", "ui-sans-serif", "ui-serif", "ui-monospace", "ui-rounded",
    "-apple-system", "blinkmacsystemfont",
}

# candidate template-repo locations, both machines (macOS, Windows)
TEMPLATE_CANDIDATES = [
    Path.home() / "Documents/Claude/Website Template",
    Path("C:/Users/Admin/Projects/Website Template"),
]

# ---- the shippable tree (ruling 2) -----------------------------------------
# Exclusions are exactly the fix plan's list; .DS_Store is skipped as Finder
# junk (it is gitignored and would otherwise break the stamp on any macOS
# folder visit between gate and ship).
EXCLUDE_DIRS = {".git", ".gate", "__pycache__", ".preflight-backup", ".claude"}

# extra prunes for the CSS lint set only: template-repo working dirs that can
# never be site content but exist where the template chain runs test_knobs.
CSS_EXCLUDE_DIRS = EXCLUDE_DIRS | {".venv", ".planning", "Backups", "node_modules"}


def tree_files(root=None):
    """Every file the ship would publish, sorted: the whole tree under root
    minus EXCLUDE_DIRS, minus docs/qa/ EXCEPT the tracked docs/qa/side-by-side/
    composite evidence (rulings 2 and 9). Subdirectory pages count."""
    root = Path(root).resolve() if root else ROOT
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(root).parts
        if any(p in EXCLUDE_DIRS for p in parts[:-1]) or path.name == ".DS_Store":
            continue
        if (len(parts) > 2 and parts[0] == "docs" and parts[1] == "qa"
                and parts[2] != "side-by-side"):
            continue
        files.append(path)
    return files


def compute_tree_digest(root=None):
    """sha256 hexdigest over the sorted "<relpath><TAB><sha256(bytes)>" lines of
    tree_files(root). Path-bound, so renames and additions change it. ship.py
    imports this (ruling 3) — keep it pure: no printing, no exiting."""
    root = Path(root).resolve() if root else ROOT
    entries = [f"{p.relative_to(root).as_posix()}\t"
               f"{hashlib.sha256(p.read_bytes()).hexdigest()}" for p in tree_files(root)]
    return hashlib.sha256("\n".join(sorted(entries)).encode()).hexdigest()


def css_lint_set(root=None):
    """Every local .css this repo can serve, sorted absolute paths — the set
    test_knobs.py lints and the ONLY set pages may reference (stylesheet
    check). docs/qa/ is never a stylesheet source."""
    root = Path(root).resolve() if root else ROOT
    out = []
    for path in sorted(root.rglob("*.css")):
        parts = path.relative_to(root).parts
        if any(p in CSS_EXCLUDE_DIRS for p in parts[:-1]):
            continue
        if len(parts) > 2 and parts[0] == "docs" and parts[1] == "qa":
            continue
        out.append(path)
    return out


def _read_key(root):
    key_file = Path(root) / ".git" / "gate.key"
    try:
        return key_file.read_bytes() if key_file.exists() else None
    except OSError:
        return None


def verify_hash(root=None):
    """Recompute the tree digest and check .gate/HASH's HMAC against it under
    .git/gate.key. Returns (True, detail) or (False, reason). Pure — no
    printing, no exit — so ship.py can import and reuse it (ruling 3)."""
    root = Path(root).resolve() if root else ROOT
    hash_file = root / ".gate" / "HASH"
    if not hash_file.exists():
        return False, ("no .gate/HASH — the ship tier has not passed; run `python3 "
                       "gate.py --ship` (only a green run writes it; any failure deletes it)")
    lines = hash_file.read_text().splitlines()
    line1 = lines[0].strip() if lines else ""
    stamp = lines[1].strip() if len(lines) > 1 else ""
    if not HEX64.fullmatch(line1) or not stamp:
        return False, (".gate/HASH is malformed (need a 64-hex HMAC on line 1, an ISO "
                       "timestamp on line 2) — delete it and re-run `python3 gate.py --ship`")
    key = _read_key(root)
    if key is None:
        return False, (".git/gate.key missing — the stamp cannot be verified without this "
                       "repo's key (preflight --start creates it; gate.py --ship recreates "
                       "it for pre-existing sites); re-run `python3 gate.py --ship`")
    expected = hmac.new(key, compute_tree_digest(root).encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, line1):
        return False, ("the shippable tree does not match .gate/HASH under .git/gate.key — "
                       "content changed since the green --ship run, or the stamp was not "
                       "written by gate.py --ship with this repo's key; "
                       "re-run `python3 gate.py --ship`")
    return True, f"tree digest verified against .gate/HASH (HMAC; ship tier green at {stamp})"


def fail(msg):
    if HASH_FILE.exists():
        HASH_FILE.unlink()
        print("stale .gate/HASH deleted — the previous green no longer stands", flush=True)
    print(f"FAIL gate — {msg}", file=sys.stderr)
    sys.exit(1)


def banner(label):
    print(f"\n=== gate: {label} " + "=" * max(3, 58 - len(label)), flush=True)


def run_step(script, python=None):
    path = ROOT / script
    if not path.exists():
        if script == "build.py":
            fail("build.py missing — author THE FACE (RUN.md phase 4); the engine set "
                 "never ships one, so rerunning preflight cannot create it")
        fail(f"{script} missing — preflight copies the full engine set; rerun it")
    banner(script if python is None else f"{script} (venv)")
    code = subprocess.run([str(python or sys.executable), str(path)], cwd=ROOT).returncode
    if code != 0:
        fail(f"{script} exited {code} — nothing downstream matters until it is green")


# ---- stylesheet check (in-process, a3) --------------------------------------

LINK_TAG = re.compile(r"<link\b[^>]*>", re.I | re.S)
REL_STYLESHEET = re.compile(r"""rel\s*=\s*["']?[^"'>]*stylesheet""", re.I)
HREF_ATTR = re.compile(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
CSS_IMPORT = re.compile(r"""@import\s+(?:url\(\s*)?["']?([^"'()\s;]+)""", re.I)
URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:")


def _resolve_local(base_dir, href, root):
    """(path, None) for an href that resolves inside root; (None, why) else."""
    href = href.split("#", 1)[0].split("?", 1)[0].strip()
    if not href:
        return None, "empty href"
    if href.startswith("//") or URL_SCHEME.match(href):
        return None, "remote/non-local URL"
    candidate = (root / href.lstrip("/")) if href.startswith("/") else (base_dir / href)
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root)
    except (ValueError, OSError):
        return None, "resolves outside the repo"
    return resolved, None


def stylesheet_check():
    """Every stylesheet a shipped page can load must be in the lint set —
    the local .css files test_knobs.py lints and the tree digest pins. A sheet
    outside that set (remote, generated elsewhere, hidden in an excluded dir)
    is a lint-free zone that wins the cascade: refuse it (a3)."""
    banner("stylesheet check")
    lint_set = set(css_lint_set(ROOT))
    pages = [p for p in tree_files(ROOT) if p.suffix.lower() == ".html"]
    problems = []
    for page in pages:
        text = page.read_text(errors="replace")
        for tag in LINK_TAG.finditer(text):
            if not REL_STYLESHEET.search(tag.group(0)):
                continue
            m = HREF_ATTR.search(tag.group(0))
            if not m:
                continue
            href = next(g for g in m.groups() if g is not None)
            target, why = _resolve_local(page.parent, href, ROOT)
            if target is None or target not in lint_set:
                problems.append(f"{page.relative_to(ROOT)} links un-linted stylesheet "
                                f"{href!r}" + (f" ({why})" if why else ""))
    for sheet in sorted(lint_set):
        text = re.sub(r"/\*.*?\*/", "", sheet.read_text(errors="replace"), flags=re.S)
        for m in CSS_IMPORT.finditer(text):
            target, why = _resolve_local(sheet.parent, m.group(1), ROOT)
            if target is None or target not in lint_set:
                problems.append(f"{sheet.relative_to(ROOT)} @imports un-linted stylesheet "
                                f"{m.group(1)!r}" + (f" ({why})" if why else ""))
    if problems:
        fail("un-linted stylesheet reference(s) (a3 — every sheet that can win the "
             "cascade must be a local .css that test_knobs.py lints and the tree digest "
             "pins):\n  " + "\n  ".join(problems))
    print(f"ok — every referenced stylesheet is local and linted "
          f"({len(pages)} page(s), {len(lint_set)} stylesheet(s))")


# ---- direction check (in-process) ------------------------------------------

def canon(value):
    """Canonical form for the NEUTRAL comparison only: case/whitespace/comma
    folded, numbers normalised (0.0 == 0, 1.20 == 1.2, .9 == 0.9), zero
    lengths unit-stripped (0px == 0), 3-hex expanded, 'black' mapped to
    #000000 — so a visually-null respelling cannot read as a change (a1).
    Never used for the drift check (that stays string-equal) and never for
    font stacks (font_neutral handles those)."""
    text = re.sub(r"\s*,\s*", ", ", re.sub(r"\s+", " ", str(value).strip())).lower()
    text = re.sub(r"#([0-9a-f])([0-9a-f])([0-9a-f])(?![0-9a-f])", r"#\1\1\2\2\3\3", text)
    text = re.sub(r"\bblack\b", "#000000", text)
    text = re.sub(r"(?<![\w.])[-+]?(?:\d+\.?\d*|\.\d+)",
                  lambda m: format(float(m.group(0)) + 0.0, "g"), text)
    return re.sub(r"(?<![\w.])0(?:px|em|rem|pt|pc|%|vh|vw|ch|ex)\b", "0", text)


def font_neutral(value):
    """True when a font stack contains no actual typeface choice — only
    generic/system families ('system-ui, sans-serif' is still neutral)."""
    families = [f.strip().strip("'\"").strip() for f in str(value).lower().split(",")]
    return all(not f or f in GENERIC_FONTS for f in families)


def knob_changed(name, value):
    if name in ("--font-display", "--font-body"):
        return not font_neutral(value)
    return canon(value) != canon(NEUTRAL[name])


def rgb_triple(value):
    nums = re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)", str(value))
    return tuple(float(n) for n in nums[:3]) if len(nums) >= 3 else None


def _root_spec(selector):
    """None when this selector cannot be targeting the root element; else its
    approximate (class-tier, type-tier) specificity. Any compound naming :root
    or html — however wrapped or qualified (:root:root, html:root,
    :where(:root), :root[data-theme=...]) — counts (a2a). Reading a lying
    override is fail-closed: it must then disagree with docs/direction.json."""
    s = selector.strip().lower()
    if not s:
        return None
    m = re.fullmatch(r":where\(\s*([^()]+)\s*\)", s)
    if m:  # :where() matches its argument but contributes zero specificity
        inner = m.group(1).strip()
        return (0, 0) if (":root" in inner or re.match(r"html(?![\w-])", inner)) else None
    m = re.fullmatch(r":is\(\s*([^()]+)\s*\)", s)
    if m:  # :is() takes its argument's specificity
        s = m.group(1).strip()
    if re.search(r"[\s>+~]", s):  # a combinator — the subject is not the root
        return None
    if ":root" not in s and re.match(r"html(?![\w-])", s) is None:
        return None
    b = (len(re.findall(r":root", s)) + len(re.findall(r"\[[^\]]*\]", s))
         + len(re.findall(r":(?!root\b)[\w-]+", s)))
    c = 1 if re.match(r"html(?![\w-])", s) else 0
    return (b, c)


def root_declarations(css_path):
    """Winning custom-property declarations across EVERY block whose selector
    can match the root element — :root, html, :root:root, :where(:root),
    attribute-qualified variants, media-wrapped copies — most specific/last
    wins (a2a; the old reader took only bare `:root` blocks, so a trailing
    higher-specificity override could lie to the gate)."""
    css = re.sub(r"/\*.*?\*/", "", css_path.read_text(errors="replace"), flags=re.S)
    winners = {}  # name -> ((specificity, order), value)
    for order, block in enumerate(re.finditer(r"([^{}]+)\{([^{}]*)\}", css)):
        specs = [_root_spec(s) for s in block.group(1).split(",")]
        specs = [s for s in specs if s is not None]
        if not specs:
            continue
        rank = (max(specs), order)
        for decl in block.group(2).split(";"):
            if ":" not in decl:
                continue
            name, value = decl.split(":", 1)
            name = name.strip()
            if name.startswith("--") and (name not in winners or rank >= winners[name][0]):
                winners[name] = (rank, value.strip())
    return {name: value for name, (_, value) in winners.items()}


def direction_check():
    banner("direction check")
    path = ROOT / "docs" / "direction.json"
    if not path.exists():
        fail("docs/direction.json missing — no derivation, no ship. Phase 3 "
             "(PLAYBOOK §9) derives the direction and records every knob, with "
             "reasoning, in that file")
    try:
        direction = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        fail(f"docs/direction.json does not parse: {e}")

    for field in ("derived", "business"):
        if not str(direction.get(field, "")).strip():
            fail(f"direction.json '{field}' missing — the derivation record carries "
                 f"its date and business name (interface contract §direction.json)")
    knobs = direction.get("knobs") or {}
    reasoning = direction.get("reasoning") or {}
    missing = [k for k in REQUIRED_KNOBS if k not in knobs]
    if missing:
        fail("direction.json knobs incomplete: " + ", ".join(missing))
    unreasoned = [k for k in REQUIRED_KNOBS if not str(reasoning.get(k, "")).strip()]
    if unreasoned:
        fail("knobs with no reasoning (every value must say WHY, from the business): "
             + ", ".join(unreasoned))

    css_path = ROOT / "styles.css"
    if not css_path.exists():
        fail("styles.css missing — the direction has nowhere to live")
    declared = root_declarations(css_path)
    drifted = [k for k in sorted(knobs) if str(knobs[k]).strip() != declared.get(k, "")]
    if drifted:
        for k in drifted:
            print(f"  {k}: direction.json={str(knobs[k]).strip()!r} "
                  f"styles.css={declared.get(k, '(not declared)')!r}", file=sys.stderr)
        fail("direction.json and styles.css disagree on: " + ", ".join(drifted)
             + " — the json records the derivation; keep them identical. The gate "
             "reads the WINNING root-level declaration (most specific/last), so a "
             "trailing :root override reads as drift, not as invisible (a2a)")

    problems = []

    # ruling 4 (a2b): a declared direction must be consumed — >= 1 var(<knob>)
    # reference per load-bearing knob, comments stripped (the template's own
    # footer comment shows var() examples and must not satisfy this).
    stripped = re.sub(r"/\*.*?\*/", "", css_path.read_text(errors="replace"), flags=re.S)
    unused = [alts[0] for alts in USAGE_REQUIRED
              if not any(re.search(rf"var\(\s*{re.escape(k)}\s*[,)]", stripped)
                         for k in alts)]
    if unused:
        problems.append("knob(s) declared but never consumed — a direction that styles "
                        "nothing is no direction (a2b): " + ", ".join(unused)
                        + " — reference each via var(...) in styles.css")

    changed = [k for k in REQUIRED_KNOBS if knob_changed(k, knobs[k])]
    accent = rgb_triple(knobs["--accent-rgb"])
    if accent is None or (sum(c * c for c in accent) ** 0.5) < 16:
        problems.append("--accent-rgb reads as neutral black (within distance 16 of "
                        "0,0,0 — '0, 0, 1' is a respelling, not a palette); no palette "
                        "was derived")
    if font_neutral(knobs["--font-display"]) and font_neutral(knobs["--font-body"]):
        problems.append("both fonts are system-ui/generic — typography is one of the two "
                        "beauty levers; derive it (PLAYBOOK §9)")
    if len(changed) < 4:
        problems.append(f"only {len(changed)} knob(s) genuinely differ from neutral "
                        "(need >= 4; 0.0px, 1.20 and 'system-ui, sans-serif' are "
                        "respellings of neutral, a1) — neutral is not a style; it is "
                        "the absence of one")
    if problems:
        fail("direction not real (audit break #3 / a1 / a2b):\n  " + "\n  ".join(problems))
    print(f"ok — direction derived: {len(changed)}/{len(REQUIRED_KNOBS)} knobs off "
          f"neutral, all string-equal the winning styles.css declarations, all "
          f"reasoned, all load-bearing knobs consumed")


# ---- ship tier -------------------------------------------------------------

def venv_python():
    for template in TEMPLATE_CANDIDATES:
        for rel in ("bin/python", "Scripts/python.exe"):
            candidate = template / ".venv" / rel
            if candidate.exists():
                return candidate
    fail("template .venv python not found in any candidate location — qa.py needs "
         "the Playwright pinned there (never `pip install` outside the venv)")


def write_hash():
    key = _read_key(ROOT)
    if key is None:
        if not (ROOT / ".git").is_dir():
            fail("no .git/ to hold gate.key — preflight --start runs `git init -b main`; "
                 "the stamp is keyed per repo and cannot be written without it")
        key = secrets.token_bytes(32)
        KEY_FILE.write_bytes(key)
        try:
            KEY_FILE.chmod(0o600)
        except OSError:
            pass
        print(".git/gate.key created (32 random bytes, never committed) — preflight "
              "--start normally creates it; this is the lazy path for pre-existing sites",
              flush=True)
    digest = compute_tree_digest(ROOT)
    line1 = hmac.new(key, digest.encode(), hashlib.sha256).hexdigest()
    HASH_FILE.parent.mkdir(exist_ok=True)
    HASH_FILE.write_text(f"{line1}\n{datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")
    print(f"\ngate green (--ship) — .gate/HASH stamped: HMAC-SHA256(.git/gate.key, "
          f"tree digest over {len(tree_files(ROOT))} files) = {line1[:16]}…")


def main():
    args = sys.argv[1:]
    ship = args == ["--ship"]
    if args and not ship:
        print("usage: python3 gate.py [--ship]   (no other flags exist)", file=sys.stderr)
        sys.exit(1)
    for script in CHAIN:
        run_step(script)
    stylesheet_check()
    direction_check()
    if ship:
        run_step("qa.py", python=venv_python())
        write_hash()
    else:
        print("\ngate green — default chain + stylesheet + direction checks. "
              "--ship adds qa.py and stamps .gate/HASH")
    sys.exit(0)


if __name__ == "__main__":
    main()
