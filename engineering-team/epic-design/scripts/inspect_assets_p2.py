# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from inspect_assets_base import *  # noqa: F403,E402


def analyse_image(path):
    result = {
        "path": path,
        "filename": os.path.basename(path),
        "status": None,
        "format": None,
        "mode": None,
        "size": None,
        "bg_type": None,
        "bg_colour": None,
        "likely_needs_removal": None,
        "notes": [],
    }

    try:
        img = Image.open(path)
        result["format"] = img.format or os.path.splitext(path)[1].upper().strip(".")
        result["mode"] = img.mode
        result["size"] = img.size
        w, h = img.size

    except Exception as e:
        result["status"] = "ERROR"
        result["notes"].append(f"Could not open: {e}")
        return result

    # --- Alpha / transparency check ---
    if img.mode == "RGBA":
        extrema = img.getextrema()
        alpha_min = extrema[3][0]  # 0 = has real transparency, 255 = fully opaque
        if alpha_min == 0:
            result["status"] = "CLEAN"
            result["bg_type"] = "transparent"
            result["notes"].append("Real alpha channel with transparent pixels — clean cutout")
            result["likely_needs_removal"] = False
            return result
        else:
            result["notes"].append("RGBA mode but alpha is fully opaque — background was never removed")
            img = img.convert("RGB")  # treat as solid for analysis below

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    # --- Sample corners and edges to detect background colour ---
    pixels = img.load()
    sample_points = [
        (0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),  # corners
        (w // 2, 0), (w // 2, h - 1),                       # top/bottom center
        (0, h // 2), (w - 1, h // 2),                       # left/right center
    ]

    samples = []
    for x, y in sample_points:
        try:
            px = pixels[x, y]
            if isinstance(px, int):
                px = (px, px, px)
            samples.append(px[:3])
        except Exception:
            pass

    if not samples:
        result["status"] = "UNKNOWN"
        result["notes"].append("Could not sample pixels")
        return result

    # --- Classify background ---
    avg_r = sum(s[0] for s in samples) / len(samples)
    avg_g = sum(s[1] for s in samples) / len(samples)
    avg_b = sum(s[2] for s in samples) / len(samples)
    avg_brightness = (avg_r + avg_g + avg_b) / 3

    # Check colour consistency (low variance = solid bg, high variance = scene/complex bg)
    max_r = max(s[0] for s in samples)
    max_g = max(s[1] for s in samples)
    max_b = max(s[2] for s in samples)
    min_r = min(s[0] for s in samples)
    min_g = min(s[1] for s in samples)
    min_b = min(s[2] for s in samples)
    variance = max(max_r - min_r, max_g - min_g, max_b - min_b)

    result["bg_colour"] = (int(avg_r), int(avg_g), int(avg_b))

    if variance > 80:
        result["status"] = "COMPLEX_BG"
        result["bg_type"] = "complex or scene"
        result["notes"].append(
            "Background varies significantly across edges — likely a scene, "
            "photograph, or artwork background rather than a solid colour"
        )
        result["likely_needs_removal"] = False  # complex bg = probably intentional content
        result["notes"].append(
            "JUDGMENT: Complex backgrounds usually mean this image IS the content "
            "(site screenshot, artwork, section bg). Background likely should be KEPT."
        )

    elif avg_brightness < 40:
        result["status"] = "DARK_BG"
        result["bg_type"] = "solid dark/black"
        result["notes"].append(
            f"Solid dark background detected — average edge brightness: {avg_brightness:.0f}/255"
        )
        result["likely_needs_removal"] = True
        result["notes"].append(
            "JUDGMENT: Dark studio backgrounds on product shots typically need removal. "
            "BUT if this is a screenshot, artwork, or intentionally dark composition, keep it."
        )

    elif avg_brightness > 210:
        result["status"] = "LIGHT_BG"
        result["bg_type"] = "solid white/light"
        result["notes"].append(
            f"Solid light background detected — average edge brightness: {avg_brightness:.0f}/255"
        )
        result["likely_needs_removal"] = True
        result["notes"].append(
            "JUDGMENT: White studio backgrounds on product shots typically need removal. "
            "BUT if this is a screenshot, UI mockup, or document, keep it."
        )

    else:
        result["status"] = "MIDTONE_BG"
        result["bg_type"] = "solid mid-tone colour"
        result["notes"].append(
            f"Solid mid-tone background detected — avg colour: RGB{result['bg_colour']}"
        )
        result["likely_needs_removal"] = None  # ambiguous — let AI judge
        result["notes"].append(
            "JUDGMENT: Ambiguous — could be a branded background (keep) or a "
            "studio colour backdrop (remove). AI must judge based on context."
        )

    # --- JPEG format warning ---
    if result["format"] in ("JPEG", "JPG"):
        result["notes"].append(
            "JPEG format — cannot store transparency. "
            "If bg removal is needed, user must provide a PNG version or approve CSS workaround."
        )

    # --- Size note ---
    if w > 2000 or h > 2000:
        result["notes"].append(
            f"Large image ({w}x{h}px) — resize before embedding. "
            "See references/asset-pipeline.md Step 3 for depth-appropriate targets."
        )

    return result
