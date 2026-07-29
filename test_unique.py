#!/usr/bin/env python3
"""Uniqueness gate — the new site must not read as a sibling of any prior site.

Runs inside a SITE repo (copied there by preflight, registry path stamped below).

Two tiers, per the 2026-07-28 decisions (docs/AUDIT_SYNTHESIS_2026-07-28.md),
hardened 2026-07-29 (red-team fixture a6 + rulings 9/14/15):

FAIL  — class-vocabulary overlap: more than THRESHOLD shared non-allowlisted
        class names with ANY single registry entry. Threshold starts at 5 and
        gets tuned on the jm-glass shakedown before it is trusted (exactly 5
        passes — ruling 14; comparator change is an open shakedown question).
        Every run prints `overlap <name>: N` per registry entry (registry
        order), success included — RUN.md's "two nearest" cites that output,
        tie-break = registry order (ruling 9).
WARN-with-waiver — banned vocabulary (the class names shared by ALL shipped
        sites — .hero, .eyebrow, .burger …). A banned name is allowed only
        with a logged entry in docs/WAIVERS.md — `class-name: reason` per
        line, markdown bullets fine (`- hero: …`). Ruling 15: a reason must
        be >= 40 chars, carry no placeholder tokens (n/a, tbd, todo, -, x, .),
        and the file may waive at most 2 names. Waivers must be echoed into
        the §12.8 BUILD_LOG verdict row so Wyatt sees them at accept/reject.
        Unwaived banned names FAIL; waived ones print as warnings.
        Renaming .eyebrow to .kicker beats the grep but not the §12.8
        side-by-side — the composite screenshot is the real uniqueness gate.
"""
import json, re, sys
from pathlib import Path

THRESHOLD = 5  # tune on the jm-glass shakedown before trusting (Decision 2)
MAX_WAIVERS = 2       # ruling 15
MIN_WAIVER_REASON = 40  # chars, ruling 15
PLACEHOLDER_TOKENS = {"n/a", "tbd", "todo", "-", "x", "."}  # ruling 15

# candidate template-repo locations, both machines (macOS, Windows)
REGISTRY_CANDIDATES = [
    Path.home() / "Documents/Claude/Website Template/REGISTRY.json",
    Path("C:/Users/Admin/Projects/Website Template/REGISTRY.json"),
]

ALLOWLIST = {"skip-link", "sr-only"}
CLASS_ATTR = re.compile(r'class="([^"]+)"')
CSS_CLASS = re.compile(r'\.([A-Za-z_][\w-]*)')
CSS_COMMENT = re.compile(r'/\*.*?\*/', re.S)
CLASS_NAME = re.compile(r'[A-Za-z_][\w-]*')


def site_vocab(root: Path) -> set:
    vocab = set()
    pages = list(root.glob("*.html"))
    if not pages:
        sys.exit("test_unique: no generated *.html — run build.py first")
    for page in pages:
        for m in CLASS_ATTR.finditer(page.read_text(errors="replace")):
            vocab.update(m.group(1).split())
    css = root / "styles.css"
    if css.exists():
        # strip /* */ comments FIRST so prose like "test_knobs.py" cannot
        # leak fake class names into the vocabulary (red-team minor)
        text = CSS_COMMENT.sub('', css.read_text(errors="replace"))
        stripped = re.sub(r'\{[^}]*\}', '{}', text)
        vocab.update(CSS_CLASS.findall(stripped))
    return vocab - ALLOWLIST


def waivers(root: Path) -> dict:
    """Parse docs/WAIVERS.md: `class-name: reason` per line.

    Markdown bullets/blockquotes are stripped (`- hero: …` works — same
    lstrip discipline as ship.py's parse_settled). Lines whose key is not a
    plausible class name (headings, prose) are ignored. Validation of the
    reasons happens in main() so a bad waiver FAILS loudly instead of
    silently not parsing.
    """
    f = root / "docs" / "WAIVERS.md"
    out = {}
    if f.exists():
        for raw in f.read_text(errors="replace").splitlines():
            line = raw.strip().lstrip("-*#> ").strip()
            if ":" not in line:
                continue
            name, reason = line.split(":", 1)
            name = name.strip().lstrip(".")
            if CLASS_NAME.fullmatch(name) and reason.strip():
                out[name] = reason.strip()
    return out


def main() -> None:
    here = Path.cwd()
    registry_path = next((p for p in REGISTRY_CANDIDATES if p.exists()), None)
    if registry_path is None:
        sys.exit("test_unique: REGISTRY.json not found in any candidate location")
    entries = json.loads(registry_path.read_text())
    if not entries:
        sys.exit("test_unique: registry is empty — seed it before gating against it")

    vocab = site_vocab(here)
    banned = set.intersection(*(set(e["classes"]) for e in entries)) - ALLOWLIST
    parsed = waivers(here)
    if (here / "docs" / "WAIVERS.md").exists():
        # visible parse result — a mis-formatted file must not be silently empty
        print("waivers parsed: " + (", ".join(sorted(parsed)) if parsed else "(none)"))

    failures, warnings = [], []

    # ruling 15: waiver discipline — a waiver is void unless its reason holds
    valid_waivers = {}
    if len(parsed) > MAX_WAIVERS:
        failures.append(
            f"docs/WAIVERS.md waives {len(parsed)} names — max {MAX_WAIVERS} "
            f"(ruling 15); rename the rest instead of waiving them")
    for name, reason in parsed.items():
        ok = True
        if len(reason) < MIN_WAIVER_REASON:
            failures.append(
                f"waiver '.{name}': reason is {len(reason)} chars "
                f"('{reason}') — need >= {MIN_WAIVER_REASON} explaining why "
                f"this banned name must stay")
            ok = False
        if {t.lower() for t in reason.split()} & PLACEHOLDER_TOKENS:
            failures.append(
                f"waiver '.{name}': placeholder token in reason ('{reason}') — "
                f"write the real justification")
            ok = False
        if ok:
            valid_waivers[name] = reason

    for e in entries:
        if Path(e["path"]).resolve() == here.resolve():
            continue  # a registered site re-testing itself
        shared = sorted(vocab & set(e["classes"]))
        # always printed, success included (ruling 9) — RUN.md's "two nearest"
        # reads these lines; ties break by registry order
        print(f"overlap {e['name']}: {len(shared)}")
        if len(shared) > THRESHOLD:
            failures.append(
                f"overlap with {e['name']}: {len(shared)} shared classes "
                f"(threshold {THRESHOLD}): {', '.join(shared[:12])}"
                + (" …" if len(shared) > 12 else ""))

    for name in sorted(vocab & banned):
        if name in valid_waivers:
            warnings.append(f"banned name '.{name}' WAIVED: {valid_waivers[name]}")
        else:
            failures.append(
                f"banned name '.{name}' (appears in every shipped site) — "
                f"rename it, or waive it in docs/WAIVERS.md with a reason "
                f"(>= {MIN_WAIVER_REASON} chars, max {MAX_WAIVERS} waivers)")

    for w in warnings:
        print(f"warn — {w}")
    if warnings:
        print("note — echo every waiver above into the §12.8 BUILD_LOG verdict "
              "row so it is visible at accept/reject (ruling 15)")
    if failures:
        print(f"FAIL test_unique ({len(failures)}):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        sys.exit(1)
    print(f"ok — vocabulary distinct: {len(vocab)} classes, "
          f"max single-site overlap within threshold {THRESHOLD}, "
          f"{len(warnings)} waived banned name(s)")


if __name__ == "__main__":
    main()
