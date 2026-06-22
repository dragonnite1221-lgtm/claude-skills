# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from contrast_checker_base import *  # noqa: F403,E402
# fmt: off
from contrast_checker_p1 import NAMED_COLORS, color_to_hex, contrast_ratio  # noqa: E402,E501
# fmt: on


def suggest_backgrounds(fg_rgb: tuple, target_ratio: float = 4.5, count: int = 8) -> list:
    """Given a foreground color, suggest background colors passing AA normal text.

    Strategy: walk luminance in both directions (lighter / darker) from the
    foreground and collect the first colors that meet the target ratio.
    """
    suggestions = []

    # Try a spread of grays and tinted variants
    candidates = []
    for v in range(0, 256, 1):
        candidates.append((v, v, v))  # grays

    # Also try tinted versions toward the complement
    fr, fg, fb = fg_rgb
    for v in range(0, 256, 2):
        candidates.append((v, min(255, v + 20), min(255, v + 40)))
        candidates.append((min(255, v + 40), v, min(255, v + 20)))
        candidates.append((min(255, v + 20), min(255, v + 40), v))

    seen = set()
    scored = []
    for c in candidates:
        cr = contrast_ratio(fg_rgb, c)
        if cr >= target_ratio and c not in seen:
            seen.add(c)
            scored.append((cr, c))

    # Sort by ratio closest to target (prefer minimal-change backgrounds)
    scored.sort(key=lambda x: x[0])
    for cr, c in scored[:count]:
        suggestions.append({"hex": color_to_hex(c), "rgb": list(c), "ratio": round(cr, 2)})
    return suggestions
_COLOR_RE = re.compile(
    r"(#[0-9a-fA-F]{3,6}|rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\))"
)
def extract_css_pairs(css_text: str) -> list:
    """Extract color / background-color pairs from CSS declarations.

    Returns a list of dicts with selector, foreground, and background strings.
    """
    pairs = []
    # Split into rule blocks
    block_re = re.compile(r"([^{}]+)\{([^}]+)\}", re.DOTALL)
    for m in block_re.finditer(css_text):
        selector = m.group(1).strip()
        body = m.group(2)

        fg = bg = None
        # Match color: ... (but not background-color)
        fg_match = re.search(
            r"(?<![-])color\s*:\s*([^;]+);", body, re.IGNORECASE
        )
        bg_match = re.search(
            r"background(?:-color)?\s*:\s*([^;]+);", body, re.IGNORECASE
        )

        if fg_match:
            val = fg_match.group(1).strip()
            c = _COLOR_RE.search(val)
            if c:
                fg = c.group(1)
            elif val.lower() in NAMED_COLORS:
                fg = val.lower()

        if bg_match:
            val = bg_match.group(1).strip()
            c = _COLOR_RE.search(val)
            if c:
                bg = c.group(1)
            elif val.lower() in NAMED_COLORS:
                bg = val.lower()

        if fg and bg:
            pairs.append({"selector": selector, "foreground": fg, "background": bg})

    return pairs
def format_result_human(fg_str: str, bg_str: str, ratio: float, results: list) -> str:
    """Format a contrast check result for the terminal."""
    lines = [
        f"Foreground : {fg_str}",
        f"Background : {bg_str}",
        f"Contrast   : {ratio:.2f}:1",
        "",
    ]
    for r in results:
        status = "PASS" if r["pass"] else "FAIL"
        lines.append(f"  [{status}] {r['level']:20s}  (requires {r['required']}:1)")
    return "\n".join(lines)
def format_suggestions_human(fg_str: str, suggestions: list) -> str:
    """Format suggested backgrounds for the terminal."""
    lines = [f"Foreground: {fg_str}", "Suggested accessible backgrounds (AA Normal Text):"]
    if not suggestions:
        lines.append("  No suggestions found.")
    for s in suggestions:
        lines.append(f"  {s['hex']}  ratio={s['ratio']}:1")
    return "\n".join(lines)
DEMO_PAIRS = [
    ("#ffffff", "#000000"),
    ("#336699", "#ffffff"),
    ("#ff6600", "#ffffff"),
    ("navy", "white"),
    ("rgb(100,100,100)", "#eeeeee"),
]
