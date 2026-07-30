#!/usr/bin/env python3
"""Ship — the ONLY sanctioned outward path.  python3 ship.py [--dry-run | --verify-hash]

Runs inside a SITE repo (preflight copies it there with the engine set — gate.py
always rides along, and ship.py IMPORTS it, so the stamp logic exists exactly
once and can never drift into a forgeable mirror). Decision 1
(docs/AUDIT_SYNTHESIS_2026-07-28.md) made shipping FULLY AUTO after a green
gate, which makes THIS file the last checkpoint before anything goes public —
so every precondition refuses with a precise message, and nothing outward
happens until all of them hold:

1. `.gate/HASH` verifies — delegated to gate.verify_hash (fixplan ruling 3).
   Line 1 is HMAC-SHA256, keyed by `.git/gate.key` (32 random bytes, created at
   preflight --start or lazily by gate.py --ship, never committed), over
   gate.compute_tree_digest(): the digest of EVERY file in the shippable tree —
   subdirectory pages, docs/SETTLED.md, docs/BUILD_LOG.md and CNAME included;
   only .git/, .gate/, __pycache__/, .preflight-backup/, .claude/ and the
   untracked bulk of docs/qa/ (the tracked side-by-side/ composites stay in)
   are outside it. One stamp pins the whole tree, so nothing can mutate between
   the green gate and the push. Threat model (ruling 1): a sloppy agent that
   would faithfully mirror a documented digest algorithm — not a hostile human
   with repo access, who could read the key; the key only has to live outside
   the files an agent pattern-matches, which .git/ does.
2. `git status --porcelain -uall` shows nothing outside the SHIP SET (ruling
   7). Ship stages that explicit set — never `git add -A` — and a stray path
   refuses BY NAME instead of publishing unreviewed.
3. docs/BUILD_LOG.md carries a §12.8 row with an explicit ACCEPT verdict
   (ruling 5); REJECT refuses with "back to phase 3/4", no token refuses too.
   At least one composite docs/qa/side-by-side/*.png must exist — the evidence
   the verdict was recorded against.
4. docs/SETTLED.md settles domain + repo, fail-closed (ruling 6): a domain
   value containing an unsettled/none marker (none, n/a, no, tbd, not decided,
   pending, for now, ?) or a *.github.io / *.pages.dev value means NO CNAME
   EVER, and shipping without a custom domain is legal ONLY for the user-site
   repo wyatt741.github.io — anything else refuses (project-page canonicals
   are unbuildable honestly until the engine grows a base-path mode).
   A settled custom domain requires the CNAME file to ALREADY carry it:
   the tree digest pins CNAME, so ship VERIFIES it instead of writing it
   post-stamp. (Deviation, logged: the interface contract sequenced the CNAME
   write after the push, but any post-stamp write now trips the guard itself.)

Then WITHOUT further prompting: stage the ship set + commit, ensure `origin`
(gh repo create when the settled hosting is GitHub Pages), `git push -u origin
main`, `wrangler deploy` ONLY if the settled chatbot tier is hybrid, print the
live URL(s). On ANY precondition failure: exit 1, print the fix, push nothing —
every other publish route (manual push, wrangler, repo visibility flips) stops
and hands to Wyatt.

Side-door guard: preflight --start installs a git pre-push hook at repo
creation (ruling 8) and every ship.py run (including --dry-run) idempotently
reinstalls it. The hook resolves its interpreter portably (python3 → python →
py -3 — the Windows box commonly has no `python3`) and has this file's
directory baked in at install time, so a manual `git push` from any cwd meets
the same stamp check. A pre-existing foreign hook is preserved as
pre-push.local and chained after the guard.

parse_settled() is the ONE parser of docs/SETTLED.md (ruling 11) — preflight
--gate direction imports it to validate the grill's output early. The
none/unsettled test runs BEFORE any hostname regex, so a parenthetical
hostname ("none (github.io only for now)") can never override a non-answer.

Registry append (`registry.py add`) happens post-ship via RUN.md, never here.
Exit 0 shipped (or dry-run all-green) / 1 refused.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HASH_FILE = ROOT / ".gate" / "HASH"
GH_OWNER = "wyatt741"
USER_SITE_REPO = f"{GH_OWNER}.github.io"

try:
    # ruling 3: the stamp is computed and verified in gate.py ONLY; ship imports
    # it (compute_tree_digest is re-exported here for preflight/tests to reuse).
    from gate import compute_tree_digest, verify_hash  # noqa: F401
except ImportError as e:
    sys.exit(f"ship: cannot import gate.py from the site root ({e}) — preflight "
             f"copies gate.py and ship.py together (engine-set completeness); "
             f"restore the CURRENT gate.py beside ship.py, then re-run")

DOMAIN = re.compile(r"\b((?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,})\b", re.I)
REPO_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9._-]+)?")
# ruling 6: any of these in the domain VALUE ⇒ no CNAME ever (checked BEFORE
# any hostname regex — ruling 11). "?" anywhere in the value counts.
UNSETTLED = re.compile(r"\b(none|no|n/?a|tbd|not\s+decided|pending|for\s+now)\b|\?", re.I)
CNAME_BLOCKLIST = ("github.io", "pages.dev")  # never CNAME values (ruling 6)
VERDICT_ROW = re.compile(r"§12\.8")
VERDICT_TOKEN = re.compile(r"\b(ACCEPT|REJECT)\b", re.I)

# the SHIP SET (ruling 7) — the ONLY paths ship stages; anything else in
# `git status --porcelain -uall` is a stray and refuses the ship by name.
SHIP_SET_FILES = {
    "styles.css", "app.js", "build.py", "engine.py", "sitemap.xml", "robots.txt",
    "_config.yml",
    "CNAME", ".gitignore", "gate.py", "qa.py", "ship.py", "preflight.py",
    "test_seo.py", "test_knobs.py", "test_content.py", "test_unique.py",
    # the rest of what preflight --start lands in every site repo:
    ".mcp.json", "setup-design-tools.sh",
    # the docs the RUNNER itself mandates. RUN.md phase 7 requires this repo's own
    # CLAUDE.md, and §4 requires LICENSES.md, so refusing to stage them made the
    # ship refuse the very artifacts it asked for (caught on the jm-glass ship).
    "CLAUDE.md", "LICENSES.md", "KICKOFF.md",
}
# tools/ holds the per-site asset and QA scripts a future session needs to rebuild
# anything; _config.yml keeps them off the served origin.
SHIP_SET_DIRS = ("worker/", "assets/", "docs/", ".claude/", "tools/")
SIDE_BY_SIDE = ROOT / "docs" / "qa" / "side-by-side"

HOOK_MARKER = "ship.py pre-push guard"

# Paths that must never be served from the client's own domain. engine.build()
# writes _config.yml to exclude them; this is the assertion that it actually did.
# The jm-glass shakedown would otherwise have published the competitor research,
# the GBP review notes and the raw research JSON to jmglassllc.com.
MUST_NOT_SERVE = ("docs/", "tools/", "worker/", "assets/src/")

FAILURES = []


def ok(msg):
    print(f"ok — {msg}", flush=True)


def bad(msg):
    FAILURES.append(msg)
    print(f"FAIL — {msg}", file=sys.stderr, flush=True)


def run(cmd, cwd=ROOT):
    """An outward action, its own output shown; any failure kills the ship."""
    print(f"$ {' '.join(cmd)}", flush=True)
    code = subprocess.run(cmd, cwd=cwd).returncode
    if code != 0:
        sys.exit(f"ship: `{' '.join(cmd)}` exited {code} — resolve and re-run ship.py")


def quiet(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


# ---- the stamp (preconditions 1-3 of the old numbering, now ONE check) -----

def stamp_check():
    """The stamp precondition, delegated to gate.verify_hash (ruling 3): the
    HMAC over the whole shippable tree recomputes identically, so NOTHING in
    the tree — pages in any subdirectory, docs/SETTLED.md, docs/BUILD_LOG.md,
    CNAME — has been touched since the green `gate.py --ship`. This replaces
    the old mtime backstop (deleted, ruling 2: mtimes are forgeable with
    `touch`; content hashing over the whole tree is not). gate.verify_hash is
    pure and returns (ok, detail) — ship prints the verdict either way."""
    try:
        verified, detail = verify_hash()
    except SystemExit:  # a gate-style hard fail still refuses cleanly here
        verified, detail = False, ("gate.verify_hash exited instead of "
                                   "returning — see its message above")
    if not verified:
        bad(detail)
        return False
    ok(detail)
    return True


# ---- the ship set (ruling 7) -----------------------------------------------

def in_ship_set(relpath):
    p = relpath.strip().strip('"').replace("\\", "/")
    return (p in SHIP_SET_FILES or p.endswith(".html")
            or p.startswith(SHIP_SET_DIRS))


def ship_set_check():
    """Refuse when the working tree carries anything outside the ship set —
    the replacement for `git add -A` (ruling 7): nothing rides a push
    unreviewed, and the refusal names the stray paths."""
    r = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=ROOT,
                       capture_output=True, text=True)  # raw — a leading space
    if r.returncode != 0:                               # in ' M' is load-bearing
        bad("`git status` failed — the site is not a git repo? preflight "
            "--start runs `git init -b main`; re-create the repo before shipping")
        return
    strays = set()
    for line in r.stdout.splitlines():
        for p in line[3:].split(" -> "):  # rename lines carry two paths
            p = p.strip().strip('"')
            if p and not in_ship_set(p):
                strays.add(p)
    if strays:
        bad("path(s) outside the ship set: " + ", ".join(sorted(strays))
            + " — ship stages the explicit ship set only (never `git add -A`); "
            "delete or relocate the stray(s), or hand this publish to Wyatt")
    else:
        ok("working tree carries nothing outside the ship set")


def stage_paths():
    """The explicit ship set, as existing paths for `git add --` (ruling 7):
    *.html recursive, the named root files, and the shipped directories."""
    paths = [n for n in sorted(SHIP_SET_FILES) if (ROOT / n).exists()]
    paths += [d.rstrip("/") for d in SHIP_SET_DIRS if (ROOT / d.rstrip("/")).is_dir()]
    already = {".git", ".gate", "__pycache__", ".preflight-backup",
               "worker", "assets", "docs", ".claude"}
    for page in ROOT.rglob("*.html"):
        parts = page.relative_to(ROOT).parts
        if parts[0] not in already:  # subdirectory pages ship too (ruling 2)
            paths.append(page.relative_to(ROOT).as_posix())
    return paths


# ---- §12.8 verdict (ruling 5) ----------------------------------------------

def verdict_check(preview=False):
    """Wyatt's §12.8 accept/reject — the one human checkpoint before a FULLY
    AUTO ship — must be an explicit ACCEPT, with the side-by-side composite
    evidence it was recorded against.

    NOT required for a PREVIEW ship (Wyatt, 2026-07-30). The verdict exists to
    protect the CLIENT'S public face, and a preview is noindex, on a URL that is
    not the client's domain, and exists precisely so humans can look at the thing
    before judging it. Gating the preview on the judgement was backwards: it made
    the artifact you need in order to decide unreachable until you had decided.
    Every mechanical gate still applies to a preview; only the human call defers."""
    if preview:
        ok("§12.8 verdict not required for a PREVIEW ship — it gates the LIVE "
           "ship to the client's own domain, where the public face is at stake")
        return None
    log = ROOT / "docs" / "BUILD_LOG.md"
    verdict = None
    if not log.exists():
        bad("docs/BUILD_LOG.md missing — RUN.md phase 6 records the §12.8 "
            "side-by-side verdict row there; run phase 6 first")
    else:
        for line in log.read_text(errors="replace").splitlines():
            if not VERDICT_ROW.search(line):
                continue
            tokens = {t.upper() for t in VERDICT_TOKEN.findall(line)}
            if len(tokens) == 1:
                verdict = tokens.pop()  # the LAST verdict row wins
            elif len(tokens) > 1:
                verdict = "AMBIGUOUS"
        if verdict == "ACCEPT":
            ok("§12.8 verdict row: ACCEPT (docs/BUILD_LOG.md)")
        elif verdict == "REJECT":
            bad("§12.8 verdict is REJECT — back to phase 3/4; re-derive or "
                "re-author, re-gate, and get a fresh verdict before shipping")
        elif verdict == "AMBIGUOUS":
            bad("a §12.8 row carries BOTH ACCEPT and REJECT — record ONE "
                "explicit verdict token per row (last row wins)")
        else:
            bad("docs/BUILD_LOG.md has no §12.8 row with an explicit ACCEPT or "
                "REJECT token — a mention of §12.8 is not a verdict; record "
                "Wyatt's call (RUN.md phase 6)")
    composites = sorted(SIDE_BY_SIDE.glob("*.png")) if SIDE_BY_SIDE.is_dir() else []
    if composites:
        ok(f"§12.8 evidence: {len(composites)} composite(s) in docs/qa/side-by-side/")
    else:
        bad("no docs/qa/side-by-side/*.png — the §12.8 verdict needs its "
            "composite screenshot evidence (qa.py --compose, RUN.md phase 6)")
    return verdict


# ---- docs/SETTLED.md (ruling 6 + 11) ---------------------------------------

def keyed_value(line, *keys):
    low = line.lower()
    for key in keys:
        i = low.find(key)
        if i < 0:
            continue
        sep = re.search(r"[:|]", line[i + len(key):])
        if sep:
            return line[i + len(key) + sep.end():].strip(" |")
    return None


def blocklisted(host):
    return any(host == b or host.endswith("." + b) for b in CNAME_BLOCKLIST)


def parse_settled(root=ROOT):
    """THE parser of the grill's answers (ruling 11 — preflight --gate
    direction imports this, so the format contract lives once). Line shapes
    per RUN.md phase 2: `- domain: <value>` / `- repo: <value>` /
    `- chatbot: none|free|hybrid` / `- rights: <value>` (+ optional
    `- hosting: github`). First match wins.

    Domain branch, fail-closed (ruling 6), in THIS order:
      1. unsettled/none marker anywhere in the value ⇒ answered, NO custom
         domain, no CNAME ever — a hostname later in the line never overrides;
      2. hostname ⇒ blocklist *.github.io / *.pages.dev (never CNAME values —
         those are hosting platforms, not custom domains) else it IS the domain;
      3. neither ⇒ not answered."""
    path = Path(root) / "docs" / "SETTLED.md"
    info = {"exists": path.exists(), "domain": None, "domain_answered": False,
            "domain_raw": None, "repo": None, "tier": None, "pages": None,
            "rights": None, "preview": None}
    if not info["exists"]:
        return info
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.replace("**", "").replace("`", "").strip().lstrip("-*#> ").strip()
        if not line:
            continue
        value = keyed_value(line, "domain", "cname")
        if value is not None and not info["domain_answered"]:
            info["domain_raw"] = value
            if UNSETTLED.search(value):
                info["domain_answered"] = True  # settled: no CNAME ever
            else:
                m = DOMAIN.search(value)
                if m:
                    info["domain_answered"] = True
                    host = m.group(1).lower()
                    if not blocklisted(host):
                        info["domain"] = host
        value = keyed_value(line, "repo")
        if value is not None and info["repo"] is None:
            for token in REPO_TOKEN.findall(value):
                name = token.rsplit("/", 1)[-1]
                if name.lower() == USER_SITE_REPO:
                    info["repo"] = USER_SITE_REPO  # the one legal dotted repo
                    break
                if not DOMAIN.fullmatch(name):  # skip a domain riding the line
                    info["repo"] = name
                    break
        value = keyed_value(line, "chatbot", "chat tier")
        if value is not None and info["tier"] is None:
            low = value.lower()
            info["tier"] = ("hybrid" if "hybrid" in low
                            else "free" if "free" in low
                            else "none" if "none" in low or "no chat" in low else None)
        value = keyed_value(line, "rights")
        if value is not None and info["rights"] is None:
            info["rights"] = value
        # A PRE-CUTOVER CLIENT PREVIEW on GitHub Pages. Legal third state beside
        # "custom domain" and "the user site": a project repo may ship to
        # https://<user>.github.io/<repo>/ with no CNAME, so the client can be sent
        # a URL before their DNS moves. engine.Site(preview=True) makes those pages
        # noindex, and ship never writes a CNAME in this state.
        value = keyed_value(line, "preview")
        if value is not None and info["preview"] is None:
            m = DOMAIN.search(value)
            if m and not UNSETTLED.search(value):
                info["preview"] = value.strip()

        value = keyed_value(line, "hosting", "host")
        if value is not None and info["pages"] is None:
            # only an explicit github answer counts — "Cloudflare Pages" must
            # not read as GitHub Pages; ambiguity fails closed (hands to Wyatt)
            info["pages"] = "github" in value.lower()
    return info


def preview_noindex_check():
    """A public preview that is NOT the client's domain must not be crawlable, or a
    staging copy competes with the real site in search."""
    pages = sorted(ROOT.glob("*.html"))
    indexable = [p.name for p in pages
                 if 'content="noindex' not in p.read_text(errors="replace")]
    if indexable:
        bad("preview ship but these pages are still indexable: "
            + ", ".join(indexable)
            + " — build with engine.Site(preview=True) and re-gate")
    else:
        ok(f"all {len(pages)} preview page(s) carry noindex")
    rb = ROOT / "robots.txt"
    if rb.exists() and "Disallow: /" not in rb.read_text():
        bad("preview ship but robots.txt does not Disallow: / — "
            "engine.robots() does this when preview=True")


def publish_scope_check():
    """The repo must not serve its own working papers.

    A Pages repo is public, so this cannot hide anything from GitHub. What it does
    is stop the CLIENT'S DOMAIN from serving research, tooling and source. The
    exclusion is a real Pages mechanism, so it is checked rather than assumed."""
    cfg = ROOT / "_config.yml"
    if not cfg.exists():
        bad("_config.yml missing — GitHub Pages runs Jekyll and would copy the WHOLE "
            "repo to the live origin, including docs/ (research, review notes, raw "
            "JSON). engine.build() writes it; run `python3 build.py` and re-gate")
        return
    text = cfg.read_text(errors="replace")
    absent = [d for d in MUST_NOT_SERVE
              if d not in text and d.rstrip("/") not in text]
    if absent:
        bad("_config.yml does not exclude " + ", ".join(absent)
            + " — those would be served from the client's own domain. Restore the "
              "engine's NOT_THE_SITE list (or add them via engine.Site(no_publish=...))")
        return
    ok(f"_config.yml excludes {len(MUST_NOT_SERVE)} non-site path(s) from the live "
       f"origin (docs/, tools/, worker/, assets/src/)")
    served = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
              if p.is_file() and p.suffix.lower() in (".html", ".css", ".js")
              and not any(part in ("docs", "tools", "worker", ".claude", ".git",
                                   "__pycache__", "src")
                          for part in p.relative_to(ROOT).parts[:-1])]
    print(f"   the live origin will serve {len(served)} html/css/js file(s) plus "
          f"assets/; everything else stays in the repo unserved", flush=True)
    if (ROOT / "docs" / "research").is_dir():
        print("   note — docs/research/ is in the PUBLIC repo (Pages requires public) "
              "but is not served from the domain. Move it out if the repo itself "
              "should not carry it.", flush=True)


def cname_check(info):
    """CNAME is INSIDE the gate-pinned tree (ruling 2), so ship verifies it
    against the settled domain instead of writing it post-stamp — a post-stamp
    write would trip the very guard that protects the push."""
    cname = ROOT / "CNAME"
    current = cname.read_text().strip() if cname.exists() else None
    if info["domain"]:
        if current == info["domain"]:
            ok(f"CNAME carries settled domain '{info['domain']}' (pinned by the gate)")
        else:
            state = ("it is missing" if current is None
                     else f"it carries {current!r} instead")
            bad(f"CNAME must already carry the settled domain '{info['domain']}' "
                f"— {state}. Fix: printf '{info['domain']}\\n' > CNAME && "
                f"python3 gate.py --ship (the tree digest pins CNAME), then ship again")
    elif current is not None:
        bad(f"no custom domain settled but CNAME exists (carrying {current!r}) — "
            f"no CNAME ever without a settled custom domain (ruling 6). "
            f"Fix: rm CNAME && python3 gate.py --ship, then ship again")
    else:
        ok("no custom domain settled — no CNAME, correctly")


def settled_check():
    info = parse_settled()
    if not info["exists"]:
        bad("docs/SETTLED.md missing — the grill (RUN.md phase 2) settles domain, repo, "
            "chatbot tier and content rights before anything ships; ship never guesses")
        return info
    if not info["domain_answered"]:
        bad("docs/SETTLED.md carries no domain answer — need a line like "
            f"`domain: example.com` (or `domain: none`, legal only for the "
            f"{USER_SITE_REPO} user site)")
    if not info["repo"]:
        bad("docs/SETTLED.md carries no repo name — need a line like `repo: jm-glass`")
    if info["domain_answered"] and info["repo"]:
        if info["domain"] is None and info["repo"] != USER_SITE_REPO \
                and not info["preview"]:
            bad(f"domain settled as {info['domain_raw']!r} (no custom domain) but "
                f"repo '{info['repo']}' is not {USER_SITE_REPO} — either settle a "
                f"custom domain, or declare a pre-cutover preview with "
                f"`- preview: https://{GH_OWNER}.github.io/<repo>/` and build with "
                f"engine.Site(preview=True)")
        elif info["domain"] is None and info["preview"]:
            ok(f"PREVIEW ship: {info['preview']} — no custom domain, no CNAME, and "
               f"the pages must be noindex (engine.Site(preview=True))")
            preview_noindex_check()
        else:
            ok(f"SETTLED: domain {info['domain'] or f'none (user site {USER_SITE_REPO})'}, "
               f"repo {info['repo']}, chatbot tier {info['tier'] or 'not stated'}, "
               f"hosting {'GitHub Pages' if info['pages'] is not False else 'NOT GitHub Pages'}"
               + (" (assumed — no hosting line)" if info["pages"] is None else ""))
        cname_check(info)
    if info["tier"] == "hybrid" and not (ROOT / "worker" / "wrangler.jsonc").exists():
        bad("settled chatbot tier is hybrid but worker/wrangler.jsonc is missing — "
            "nothing to `wrangler deploy`; restore worker/ and re-run `gate.py --ship`")
    rc, _ = quiet(["git", "remote", "get-url", "origin"])
    if rc != 0 and info["pages"] is False:
        bad("hosting is settled away from GitHub Pages and no `origin` remote exists — "
            "ship.py only auto-creates GitHub Pages repos; hand this publish to Wyatt")
    return info


# ---- the pre-push side-door guard ------------------------------------------

def hook_body(root=ROOT):
    """Ruling 8: interpreter resolved portably at run time (python3 → python →
    py -3 — Git-for-Windows sh commonly has no `python3`), this directory
    baked in at install time so the guard works from any cwd on both machines."""
    site = Path(root).resolve().as_posix()
    return f"""#!/bin/sh
# {HOOK_MARKER} — re-verifies .gate/HASH before ANY push leaves this repo
# (contract §ship.py: the side-door guard — a manual push meets the same gate).
# Installed by preflight --start; reinstalled idempotently by every ship.py run.
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else PY="py -3"
fi
$PY "{site}/ship.py" --verify-hash || {{
  echo "pre-push BLOCKED — .gate/HASH did not verify. Run: python3 gate.py --ship" >&2
  exit 1
}}
if [ -x "$(dirname "$0")/pre-push.local" ]; then
  exec "$(dirname "$0")/pre-push.local" "$@"
fi
exit 0
"""


def install_hook(root=ROOT):
    root = Path(root).resolve()
    if not (root / ".git").is_dir():
        print("warn — not a git repo, pre-push guard not installed "
              "(preflight --start should have run `git init -b main`)")
        return
    hooks = root / ".git" / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "pre-push"
    body = hook_body(root)
    if hook.exists() and HOOK_MARKER not in hook.read_text(errors="replace"):
        hook.rename(hooks / "pre-push.local")
        print("warn — foreign pre-push hook preserved as pre-push.local, "
              "chained after the guard")
    if hook.exists() and hook.read_text() == body:
        ok("pre-push guard already installed (idempotent)")
        return
    hook.write_text(body)
    hook.chmod(0o755)
    ok("pre-push guard installed at .git/hooks/pre-push — a manual push now "
       "meets the same .gate/HASH check")


# ---- the outward actions ----------------------------------------------------

def build_plan(info, hash_line, stamp_line):
    """(description, action) pairs — action None means informational only.
    One list serves both --dry-run (print) and the real run (execute)."""
    domain, repo, tier = info["domain"], info["repo"] or "<repo>", info["tier"]
    plan = []

    if domain:
        plan.append((f"CNAME carries '{domain}' — verified precondition, "
                     f"pinned by the gate; ship never writes it", None))
    else:
        plan.append(("no custom domain settled — no CNAME ever (ruling 6)", None))

    if hash_line and stamp_line:
        msg = f"ship: gate green {stamp_line} ({hash_line[:12]})"
    else:  # dry-run on an unstamped repo still renders a real plan
        msg = "ship: gate green <pending .gate/HASH>"

    def commit():
        run(["git", "add", "--"] + stage_paths())
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode:
            run(["git", "commit", "-m", msg])
        else:
            print("nothing to commit — the gated tree is already committed")
    plan.append((f"git add <ship set> && git commit -m {msg!r} "
                 f"(never `git add -A`; skipped if the tree is clean)", commit))

    rc, url = quiet(["git", "remote", "get-url", "origin"])
    if rc == 0:
        plan.append((f"origin exists ({url}) — leave it", None))
    else:
        plan.append((f"gh repo create {GH_OWNER}/{repo} --public --source=. --remote=origin",
                     lambda: run(["gh", "repo", "create", f"{GH_OWNER}/{repo}",
                                  "--public", "--source=.", "--remote=origin"])))

    plan.append(("git push -u origin main (the pre-push guard re-verifies .gate/HASH)",
                 lambda: run(["git", "push", "-u", "origin", "main"])))

    if tier == "hybrid" and not domain and info.get("preview"):
        plan.append(("no worker deploy — PREVIEW ship. The widget points at "
                     "chat.<domain>, which does not resolve until the DNS cutover, so "
                     "deploying now would leave an orphan Worker on a workers.dev URL "
                     "that PLAYBOOK §6 forbids serving the bot from. The canned "
                     "answers carry the preview.", None))
    elif tier == "hybrid":
        plan.append(("wrangler deploy (cwd worker/ — settled chatbot tier is hybrid)",
                     lambda: run(["wrangler", "deploy"], cwd=ROOT / "worker")))
    else:
        plan.append((f"no worker deploy — settled chatbot tier is "
                     f"'{tier or 'not stated'}', only hybrid deploys", None))

    urls = []
    if not domain and info.get("preview"):
        urls.append(f"{info['preview']} (PREVIEW, noindex, not the client's domain)")
    if domain:
        urls.append(f"https://{domain}/")
        if tier == "hybrid":
            urls.append(f"https://chat.{domain}/ (worker)")
    elif info["pages"] is not False and repo == USER_SITE_REPO:
        urls.append(f"https://{USER_SITE_REPO}/")
    plan.append(("live URL(s): " + (", ".join(urls) or "unknown — hosting unsettled"), None))
    return plan


def main():
    args = sys.argv[1:]
    if args == ["--verify-hash"]:  # the pre-push hook's entry point
        sys.exit(0 if stamp_check() else 1)
    dry = args == ["--dry-run"]
    if args and not dry:
        print("usage: python3 ship.py [--dry-run | --verify-hash]", file=sys.stderr)
        sys.exit(1)

    install_hook()
    stamp_check()      # the tree HMAC (rulings 1-3)
    ship_set_check()   # no strays, no `git add -A` (ruling 7)
    # SETTLED first, because whether this is a preview decides whether the §12.8
    # human verdict is required at all.
    info = settled_check()  # domain/repo fail-closed + CNAME pinning (ruling 6)
    is_preview = bool(info.get("preview")) and not info.get("domain")
    verdict_check(preview=is_preview)  # §12.8 ACCEPT + composite, live ships only
    publish_scope_check()   # the domain must not serve the working papers

    lines = HASH_FILE.read_text().splitlines() if HASH_FILE.exists() else []
    plan = build_plan(info, lines[0].strip() if lines else "",
                      lines[1].strip() if len(lines) > 1 else "")

    if dry:
        print("\nplanned actions (--dry-run — nothing below was executed):")
        for i, (desc, _) in enumerate(plan, 1):
            print(f"  {i}. {desc}")
        if FAILURES:
            print(f"\ndry-run: the real run would REFUSE ({len(FAILURES)} precondition "
                  f"failure(s) above) and push nothing", file=sys.stderr)
            sys.exit(1)
        print("dry-run complete — all preconditions hold; nothing was executed")
        sys.exit(0)

    if FAILURES:
        print(f"\nREFUSED ({len(FAILURES)} precondition failure(s)) — nothing was pushed. "
              f"ship.py is the only outward path (Decision 1); fix the above, re-run "
              f"`python3 gate.py --ship`, then ship again", file=sys.stderr)
        sys.exit(1)

    print("\nshipping — FULLY AUTO after green gates (Decision 1), no further prompting:")
    for desc, action in plan:
        print(f"-- {desc}", flush=True)
        if action:
            action()
    print("shipped. Next (RUN.md, post-ship): registry append via `registry.py add`")
    sys.exit(0)


if __name__ == "__main__":
    main()
