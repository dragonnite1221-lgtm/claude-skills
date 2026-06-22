# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from contrast_checker_base import *  # noqa: F403,E402


NAMED_COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (0, 128, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "navy": (0, 0, 128),
    "teal": (0, 128, 128),
    "olive": (128, 128, 0),
    "maroon": (128, 0, 0),
    "lime": (0, 255, 0),
    "aqua": (0, 255, 255),
    "silver": (192, 192, 192),
    "gold": (255, 215, 0),
    "coral": (255, 127, 80),
    "salmon": (250, 128, 114),
    "tomato": (255, 99, 71),
}
WCAG_THRESHOLDS = [
    ("AA Normal Text", 4.5),
    ("AA Large Text", 3.0),
    ("AA UI Components", 3.0),
    ("AAA Normal Text", 7.0),
    ("AAA Large Text", 4.5),
]
def parse_color(color_str: str) -> tuple:
    """Parse a color string into an (R, G, B) tuple.

    Accepts:
      - #RRGGBB or #RGB hex
      - rgb(r, g, b)  with values 0-255
      - Named CSS colors
    """
    s = color_str.strip().lower()

    # Named color
    if s in NAMED_COLORS:
        return NAMED_COLORS[s]

    # Hex: #RGB or #RRGGBB
    hex_match = re.match(r"^#([0-9a-f]{3}|[0-9a-f]{6})$", s)
    if hex_match:
        h = hex_match.group(1)
        if len(h) == 3:
            r, g, b = int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16)
        else:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (r, g, b)

    # rgb(r, g, b)
    rgb_match = re.match(r"^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$", s)
    if rgb_match:
        r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
        if not all(0 <= c <= 255 for c in (r, g, b)):
            raise ValueError(f"RGB values must be 0-255, got rgb({r},{g},{b})")
        return (r, g, b)

    raise ValueError(
        f"Invalid color format: '{color_str}'. "
        "Use #RRGGBB, #RGB, rgb(r,g,b), or a named color."
    )
def color_to_hex(rgb: tuple) -> str:
    """Convert an (R, G, B) tuple to #RRGGBB."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
def relative_luminance(rgb: tuple) -> float:
    """Calculate relative luminance per WCAG 2.2 (sRGB).

    https://www.w3.org/TR/WCAG22/#dfn-relative-luminance
    """
    channels = []
    for c in rgb:
        s = c / 255.0
        channels.append(s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
def contrast_ratio(rgb1: tuple, rgb2: tuple) -> float:
    """Return the WCAG contrast ratio between two colors (>= 1.0)."""
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
def evaluate_contrast(ratio: float) -> list:
    """Return pass/fail results for each WCAG threshold."""
    results = []
    for label, threshold in WCAG_THRESHOLDS:
        results.append({
            "level": label,
            "required": threshold,
            "ratio": round(ratio, 2),
            "pass": ratio >= threshold,
        })
    return results
