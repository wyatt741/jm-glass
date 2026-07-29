#!/usr/bin/env python3
"""PreToolUse guard for SITE repos — copied in by preflight --start.

Belt-and-suspenders tier ONLY (amendment 1: hooks load at session start, so
this cannot fire in the session that creates the repo — the preflight --gate
chain and gate.py are the primary enforcement). Stdlib only. Two rules:

(a) *.html at the site root is GENERATED output — deny every edit, always.
    The fix lives in build.py (PLAYBOOK §12: never hand-edit generated HTML).
(b) styles.css / build.py are direction-gated — deny until ALL of
    docs/SETTLED.md, docs/DESIGN_READ.md and docs/direction.json exist,
    listing whichever are missing. Styling before a settled, reasoned
    direction is how template sameness gets back in.

Deny = exit 2, reason on stderr (Claude Code blocks the call and feeds the
reason back). Allow = exit 0, silent. Malformed input fails OPEN — an
advisory tier must never brick the session.
"""
import json
import os
import sys
from pathlib import Path

GATED = {"styles.css", "build.py"}
DIRECTION = ["docs/SETTLED.md", "docs/DESIGN_READ.md", "docs/direction.json"]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if payload.get("tool_name") not in {"Edit", "Write", "MultiEdit"}:
        return 0
    file_path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not file_path:
        return 0

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR")
                or payload.get("cwd") or Path.cwd()).resolve()
    target = Path(file_path)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if target.parent != root:
        return 0  # only root-level files are guarded

    if target.suffix.lower() == ".html":
        print(f"{target.name} is GENERATED — edit build.py and rebuild; "
              f"never hand-edit generated HTML (PLAYBOOK §12)",
              file=sys.stderr)
        return 2

    if target.name in GATED:
        missing = [a for a in DIRECTION if not (root / a).exists()]
        if missing:
            print(f"{target.name} is direction-gated — missing: "
                  f"{', '.join(missing)}. Finish the grill/direction phases "
                  f"first (preflight --gate).", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
