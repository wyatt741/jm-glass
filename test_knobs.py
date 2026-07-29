#!/usr/bin/env python3
"""Lints EVERY local stylesheet for direction discipline.  python3 test_knobs.py

Since v2 stopped shipping components, this is no longer about leaks from a previous
template — there is nothing left to inherit. It is about a site declaring its
character in ONE place instead of scattering it, which is what makes a direction
adjustable at all.

styles.css stays the knob-bearing file: the DIRECTION KNOBS block and the a11y
contract (focus ring, skip link, reduced motion, OS-dark tokens) live and are
checked there — and knobs may be declared ONLY in its opening :root block, so a
later override cannot lie to gate.py's direction check (red-team a2a).

Discipline is repo-wide (red-team a3: a second stylesheet loaded after
styles.css won the cascade and sat out every check). Every local .css — the
same set gate.py's stylesheet check pins pages to, via gate.css_lint_set — must
pass:

  - no emissive accent halo hardcodes its alpha  -> calc(x * var(--glow-a))
  - no transition/animation hardcodes a timing   -> calc(Xs * var(--motion))
  - no cubic-bezier outside styles.css's :root   -> var(--ease) / var(--spring)
  - no legacy bwraps colour vocabulary (--pink / --az / --copper)
  - no DIRECTION KNOB declared outside styles.css's opening :root

Zero component rules is a valid state (that is what the base file ships), so
there are no minimum-usage counts HERE — gate.py's direction check owns the
knob-usage assertion (a2b).

ponytail: line-level regex, not a CSS parser. Enough to fail loudly on the real mistakes.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    from gate import REQUIRED_KNOBS, css_lint_set
except ImportError:
    sys.exit("FAIL\n  gate.py not importable beside test_knobs.py — the engine set "
             "travels together (preflight copies it whole); restore gate.py")

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def strip_comments(text):
    """Blank /* */ contents but keep newlines, so line numbers survive."""
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)),
                  text, flags=re.S)


# ---- repo-wide discipline (every stylesheet — a3) ---------------------------
# borders, surface tints and outlines are function, not character: they may
# ignore the glow knob.
FUNCTIONAL = ("border:", "border-color:", "outline", "--band:", "--accent-rgb:",
              "--accent-soft-rgb:")
RAW_ALPHA = re.compile(r"rgba\(\s*var\(--accent(?:-soft)?-rgb\)\s*,\s*\.")
DUR = re.compile(r"(?<![\w.\-*(])(\.?\d+(?:\.\d+)?s)(?![\w)])")
TIMING = re.compile(r"(?:transition|animation)(?:-delay|-duration)?:[^;}]*")


def discipline(label, lines, root_end):
    """The rules every stylesheet must meet. root_end is the last line of the
    knob-bearing :root block (styles.css only); other sheets pass 0 — they have
    no sanctioned :root, so a curve or raw timing anywhere in them fails."""
    leaks = [f"{label}:{n}: {l.strip()[:88]}" for n, l in enumerate(lines, 1)
             if RAW_ALPHA.search(l) and not any(f in l for f in FUNCTIONAL)]
    check(not leaks, "accent alpha not scaled by the glow knob — wrap in "
          "calc(x*var(--glow-a)):\n    " + "\n    ".join(leaks))

    unscaled = [f"{label}:{n}: {m.group(0)[:88]}" for n, l in enumerate(lines, 1)
                if n > root_end for m in TIMING.finditer(l) if DUR.search(m.group(0))]
    check(not unscaled, "hardcoded timing — wrap in calc(Xs*var(--motion)) so the site "
          "has one tempo:\n    " + "\n    ".join(unscaled))

    stray = [f"{label}:{n}: {l.strip()[:88]}" for n, l in enumerate(lines, 1)
             if n > root_end and "cubic-bezier" in l]
    check(not stray, "cubic-bezier outside styles.css's :root — use "
          "var(--ease)/var(--spring):\n    " + "\n    ".join(stray))

    legacy = [f"{label}:{n}: {l.strip()[:88]}" for n, l in enumerate(lines, 1)
              if re.search(r"--(pink|az|copper)\b", l)]
    check(not legacy, "legacy bwraps colour names — use --accent/--accent-deep/"
          "--accent-soft:\n    " + "\n    ".join(legacy))


main_css = HERE / "styles.css"
if not main_css.exists():
    sys.exit("FAIL\n  styles.css missing — the knobs have to live somewhere")

css = main_css.read_text()
lines = css.splitlines()

# end of the :root block that opens the file
try:
    root_end = next(i for i, l in enumerate(lines, 1) if l.strip() == "}")
except StopIteration:
    sys.exit("FAIL\n  styles.css has no :root block — the knobs have to live somewhere")

# ---- styles.css: the knobs are declared ------------------------------------
KNOBS = ("--accent", "--accent-rgb", "--glow-a", "--motion", "--ease", "--spring",
         "--r-pill", "--h-weight", "--h-track", "--h-leading")
missing = [k for k in KNOBS if not re.search(rf"{re.escape(k)}\s*:", css)]
check(not missing, f"DIRECTION KNOBS not declared: {', '.join(missing)}")
check("DIRECTION KNOBS" in css, "the DIRECTION KNOBS marker comment is gone — keep the block findable")

# ---- styles.css: knobs are declared ONCE, in the opening :root (a2a) --------
KNOB_DECL = (*REQUIRED_KNOBS, "--ease", "--spring")
clean_lines = strip_comments(css).splitlines()
redeclared = [f"styles.css:{n}: {l.strip()[:88]}" for n, l in enumerate(clean_lines, 1)
              if n > root_end
              and any(re.match(rf"\s*{re.escape(k)}\s*:", l) for k in KNOB_DECL)]
check(not redeclared, "DIRECTION KNOB redeclared below the opening :root block — knobs "
      "live in ONE place (the block gate.py reads); a later override lies to the gate "
      "and to the browser (a2a):\n    " + "\n    ".join(redeclared))

discipline("styles.css", lines, root_end)

# ---- styles.css: accessibility survives every direction ---------------------
check(re.search(r"outline:[^;]*solid var\(--focus\)", css) is not None,
      "focus ring must be a solid var(--focus) outline — never --accent (brand colours are "
      "often under the 3:1 non-text contrast floor) and never dependent on --glow-a")
check(re.search(r"--focus\s*:", css) is not None, "--focus token not declared")
# an OS-dark visitor who never chose must still get dark tokens, or color-scheme and the
# palette disagree and the browser's own chrome mismatches the page
check("prefers-color-scheme: dark" in css or "light-dark(" in css,
      "no OS-dark default: color-scheme promises dark but the tokens only deliver light")
check("prefers-reduced-motion" in css, "no prefers-reduced-motion block — motion must be opt-out")
check(".skip-link" in css, "no .skip-link styling — the engine emits one on every page")

# ---- every OTHER local stylesheet (a3) -------------------------------------
others = [s for s in css_lint_set(HERE) if s != main_css]
for sheet in others:
    label = sheet.relative_to(HERE).as_posix()
    text = sheet.read_text(errors="replace")
    clean = strip_comments(text)
    declared = sorted({k for k in KNOB_DECL if re.search(rf"{re.escape(k)}\s*:", clean)})
    check(not declared, f"{label}: declares DIRECTION KNOB(s) outside styles.css "
          f"({', '.join(declared)}) — knobs live in ONE place; a second sheet may "
          "consume the direction (var(...)), never restate it")
    discipline(label, text.splitlines(), 0)

if fails:
    sys.exit("FAIL\n  " + "\n  ".join(fails))
print("ok — direction knobs declared once; no hardcoded halo, timing or curve; a11y "
      f"intact ({1 + len(others)} stylesheet(s) linted: styles.css"
      + "".join(", " + s.relative_to(HERE).as_posix() for s in others) + ")")
