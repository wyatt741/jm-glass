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
SMALL = 500     # the phone-width variant. Without a second width the `sizes`
                # attribute is inert and a 430px phone downloads the 1000px file.
QUALITY = 82

# the full-bleed hero. cfc_4 is the largest usable landscape frame (1920x1440),
# strong, no identifiable face, and it shows curtain wall, the highest-value scope.
HERO_FILE = "cfc_4.jpg"

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
    """Write the full-width file plus a phone-width sibling (-sm.jpg), so the
    markup can carry a real srcset. Returns the full-width size."""
    src = SRC / name
    WORK.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as raw:
        base = raw.convert("RGB")
    sizes = {}
    for target, suffix in ((cap, ""), (SMALL, "-sm")):
        w, h = base.size
        scale = min(1.0, target / max(w, h))
        im = base.resize((round(w * scale), round(h * scale)), Image.LANCZOS) \
            if scale < 1.0 else base.copy()
        stem = out_name[:-4] if out_name.lower().endswith(".jpg") else out_name
        im.save(WORK / f"{stem}{suffix}.jpg", "JPEG", quality=QUALITY,
                optimize=True, progressive=True)
        sizes[suffix] = im.size
    # SMALL caps the LONG edge, so a portrait file is only ~281px WIDE. Advertising
    # it as 500w made browsers upscale it on plain desktop, so the real width is
    # recorded and build.py emits that.
    return sizes[""], sizes["-sm"][0]


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


def masthead_marks():
    """The mark renders 172px wide. Shipping the 1567px original twice, eagerly,
    on every page was ~51KB of waste for ~4KB of pixels."""
    for src_name, out_name in (("logo.png", "logo-mark.png"),
                               ("logo-reversed.png", "logo-mark-reversed.png")):
        with Image.open(ROOT / "assets" / src_name) as im:
            im = im.convert("RGBA")
            scale = 344 / im.width          # 2x the 172px render box
            small = im.resize((344, max(1, round(im.height * scale))), Image.LANCZOS)
            small.save(ROOT / "assets" / out_name, optimize=True)
            print(f"masthead mark: {out_name} {small.width}x{small.height} "
                  f"({(ROOT / 'assets' / out_name).stat().st_size // 1024}KB)")


def og_image():
    """1200x630 share card. Without it every meta og:image and the JSON-LD image
    key pointed at a file that does not exist, so every share previewed blank."""
    base = Image.open(WORK / "storage-co-3.jpg").convert("RGB")
    tw, th = 1200, 630
    scale = max(tw / base.width, th / base.height)
    im = base.resize((round(base.width * scale), round(base.height * scale)), Image.LANCZOS)
    im = im.crop(((im.width - tw) // 2, (im.height - th) // 2,
                  (im.width - tw) // 2 + tw, (im.height - th) // 2 + th))
    # a legible band for the wordmark, so the card reads at Slack thumbnail size
    band = Image.new("RGB", (tw, 132), (22, 25, 29))
    im.paste(band, (0, th - 132))
    mark = Image.open(ROOT / "assets" / "logo-reversed.png").convert("RGBA")
    mscale = 420 / mark.width
    mark = mark.resize((420, max(1, round(mark.height * mscale))), Image.LANCZOS)
    im.paste(mark, (48, th - 132 + (132 - mark.height) // 2), mark)
    im.save(ROOT / "assets" / "og-image.jpg", "JPEG", quality=86, optimize=True,
            progressive=True)
    print(f"og-image.jpg 1200x630 "
          f"({(ROOT / 'assets' / 'og-image.jpg').stat().st_size // 1024}KB)")


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
        (w, h), sm_w = emit(name, out_name, cap)
        row = {"src": f"assets/work/{out_name}", "w": w, "h": h, "sm": sm_w,
               "alt": p["alt"], "q": p["quality"], "o": p["orientation"]}
        rows.append(row)
        if slug:
            by_project.setdefault(slug, []).append(row)
        else:
            capability.append(row)

    # the team photo ships on its own, at tile size
    (tw, th), team_sm = emit("TEAM-PHOTO-2023-scaled.jpg", "team-2023.jpg", TILE)
    gc_marks()
    masthead_marks()
    og_image()
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
        "team": {"src": "assets/work/team-2023.jpg", "w": tw, "h": th, "sm": team_sm},
    }
    (ROOT / "assets" / "work" / "manifest.json").write_text(json.dumps(out, indent=1))
    print("wrote assets/work/manifest.json")
    missing = [s for s in PROJECTS if not by_project.get(s)]
    if missing:
        print("projects with NO usable photo:", ", ".join(missing))


if __name__ == "__main__":
    main()
