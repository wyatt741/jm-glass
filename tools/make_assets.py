#!/usr/bin/env python3
"""Build the published asset set from the inspected originals.

Reads docs/research/asset-inventory.json (the full-size inspection pass: what each
frame shows, whether it is usable, its alt text) and emits web-sized copies plus a
printable Python block for build.py. Rejected frames never reach assets/.

    python3 tools/make_assets.py

Nothing here is destructive to assets/src/, which stays as the untouched originals
(gitignored bulk).
"""
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "src"
WORK = ROOT / "assets" / "work"
INV = ROOT / "docs" / "research" / "asset-inventory.json"

TILE = 1000     # max dimension for a gallery / scope frame
HERO = 1800     # max dimension for the one hero frame
QUALITY = 82

HERO_FILE = "storage-co-3.jpg"

# verified from their own WordPress taxonomy: 37 Commercial Shell, 36 Tenant Improvements
PROJECT_TYPE = {37: "Commercial Shell", 36: "Tenant Improvements"}

PROJECTS = {
    "arizona-credit-union":     ("Arizona Credit Union", "Surprise", [37, 36]),
    "family-dollar":            ("Family Dollar", "El Mirage", [37]),
    "brusters-ice-cream":       ("Bruster's Ice Cream", "Gilbert", [36]),
    "ktnn-radio-station":       ("KTNN Radio Station", "St Michaels", [36]),
    "storage-co":               ("Storage Co.", "Maricopa", [37]),
    "chop-shop":                ("Original ChopShop", "Tempe", [37]),
    "scorpion-bay":             ("Scorpion Bay", "Peoria", [36]),
    "shopping-center-face-lift": ("Shopping Center Face Lift", "Phoenix", [37, 36]),
    "medical-building":         ("Medical Building", "Florence", [37]),
    "bath-body-works":          ("Bath & Body Works", "Tempe", [37]),
    "autozone":                 ("Autozone", "Phoenix", [37]),
    "st-thomas-building":       ("St. Thomas Building", "Avondale", [37, 36]),
    "canes":                    ("Raising Cane's", "Phoenix", [37]),
    "johnny-was":               ("Johnny Was", "Scottsdale", [37]),
    "call-center":              ("Call Center", "Phoenix", [36]),
    "gym":                      ("EOS Fitness", "Glendale", [36]),
    "pilot":                    ("Flying J Travel Center", "Phoenix", [37]),
    "storefront":               ("Storefront", "", [37]),
    "lobby":                    ("Lobby", "Peoria", [36]),
    "esplanade":                ("Esplanade", "Phoenix", [37]),
    "aps-central-ave":          ("Taylor Morrison HQ", "Scottsdale", [37]),
    "hopdoddy-test":            ("Life Time Happy Valley-Peoria", "Peoria", [37]),
}

# frames that belong to no project page on their server. They ship as capability
# photographs with generic captions, never captioned as a named project (§9a).
UNATTRIBUTED = {"cfc_1.jpg", "cfc_2.jpg", "cfc_4.jpg", "cfc_5.jpg"}


def slug_for(filename, media_by_file, projects_by_id):
    m = media_by_file.get(filename)
    if not m:
        return None
    return projects_by_id.get(m.get("post"))


def emit(name, out_name, cap):
    src = SRC / name
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        scale = min(1.0, cap / max(w, h))
        size = (round(w * scale), round(h * scale))
        if scale < 1.0:
            im = im.resize(size, Image.LANCZOS)
        WORK.mkdir(parents=True, exist_ok=True)
        im.save(WORK / out_name, "JPEG", quality=QUALITY, optimize=True,
                progressive=True)
        return im.size


def gc_marks():
    """Copy the 23 GC and developer marks out of the gitignored originals into
    assets/gc/ so they actually ship. No recolouring: a trademark renders on the
    background it was drawn for, which is why the site gives them a fixed light
    tile in both themes (17 of the 23 are not dark-safe per the inspection)."""
    dest = ROOT / "assets" / "gc"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    n = 0
    for src in sorted(SRC.glob("*-logo.png")):
        if "jmglass" in src.name:
            continue          # J&M's own wordmark variants are not partner marks
        shutil.copy2(src, dest / src.name)
        n += 1
    print(f"gc marks: {n} copied to assets/gc/")


def favicons():
    """The window-grid mark from the wordmark, squared, on the brand red."""
    logo = Image.open(ROOT / "assets" / "logo.png").convert("RGBA")
    mark = logo.crop((0, 0, 212, logo.height))          # the four-pane mark only
    for px in (16, 32, 180, 512):
        pad = max(2, px // 12)
        plate = Image.new("RGBA", (px, px), (255, 255, 255, 0))
        inner = px - pad * 2
        m = mark.copy()
        m.thumbnail((inner, inner), Image.LANCZOS)
        plate.alpha_composite(m, ((px - m.width) // 2, (px - m.height) // 2))
        plate.save(ROOT / "assets" / f"icon-{px}.png")
    ico = Image.open(ROOT / "assets" / "icon-512.png")
    ico.save(ROOT / "assets" / "favicon.ico",
             sizes=[(16, 16), (32, 32), (48, 48)])
    print("favicons: icon-16/32/180/512.png + favicon.ico")


def main():
    inv = json.loads(INV.read_text())
    media = json.loads((SRC / "media.json").read_text())
    wp_projects = json.loads((SRC / "projects.json").read_text())
    media_by_file = {(m["file"] or "").split("/")[-1]: m for m in media}
    projects_by_id = {p["id"]: p["slug"] for p in wp_projects}

    usable = [p for p in inv["photos"] if p["usable"]]
    rows, by_project, capability = [], {}, []
    if WORK.exists():
        shutil.rmtree(WORK)

    for p in sorted(usable, key=lambda x: x["file"]):
        name = p["file"]
        if name in ("TEAM-PHOTO-2023-scaled.jpg",):
            continue
        if not (SRC / name).exists():
            print("  missing source, skipped:", name)
            continue
        slug = slug_for(name, media_by_file, projects_by_id)
        if slug is None and name not in UNATTRIBUTED:
            continue                     # unattributed and not shortlisted
        out_name = name.replace("_", "-").lower()
        cap = HERO if name == HERO_FILE else TILE
        w, h = emit(name, out_name, cap)
        row = {"src": f"assets/work/{out_name}", "w": w, "h": h,
               "alt": p["alt"], "q": p["quality"], "o": p["orientation"]}
        rows.append(row)
        if slug:
            by_project.setdefault(slug, []).append(row)
        else:
            capability.append(row)

    # the team photo ships on its own, at tile size
    tw, th = emit("TEAM-PHOTO-2023-scaled.jpg", "team-2023.jpg", TILE)
    gc_marks()
    favicons()

    print(f"\npublished {len(rows)} project frames + team photo into assets/work/")
    print(f"projects with photos: {len(by_project)} / {len(PROJECTS)}")
    print(f"capability frames (no project page): {len(capability)}")

    out = {
        "projects": [
            {"slug": s, "title": PROJECTS[s][0], "city": PROJECTS[s][1],
             "types": [PROJECT_TYPE[t] for t in PROJECTS[s][2]],
             "photos": by_project.get(s, [])}
            for s in PROJECTS
        ],
        "capability": capability,
        "team": {"src": "assets/work/team-2023.jpg", "w": tw, "h": th},
    }
    (ROOT / "assets" / "work" / "manifest.json").write_text(json.dumps(out, indent=1))
    print("wrote assets/work/manifest.json")
    missing = [s for s in PROJECTS if not by_project.get(s)]
    if missing:
        print("projects with NO usable photo:", ", ".join(missing))


if __name__ == "__main__":
    main()
