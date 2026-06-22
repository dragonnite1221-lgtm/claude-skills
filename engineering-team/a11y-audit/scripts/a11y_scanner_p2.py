# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from a11y_scanner_base import *  # noqa: F403,E402
# fmt: off
from a11y_scanner_p1 import VALID_ARIA_ATTRS, _find, _snippet  # noqa: E402,E501
# fmt: on


def check_headings(lines, fp):
    findings = []
    heading_levels = []
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r"<[hH]([1-6])\b", line):
            heading_levels.append((int(m.group(1)), ln, line))
    if not heading_levels:
        return findings
    # Missing h1
    levels_seen = {h[0] for h in heading_levels}
    if 1 not in levels_seen and any(l <= 3 for l in levels_seen):
        findings.append(_find("heading-missing-h1", "headings", "serious",
                              "Page has headings but no <h1>",
                              fp, heading_levels[0][1], _snippet(heading_levels[0][2]),
                              "1.3.1 Info and Relationships",
                              "Add a single <h1> as the main page heading."))
    # Multiple h1s
    h1_lines = [(ln, line) for lvl, ln, line in heading_levels if lvl == 1]
    if len(h1_lines) > 1:
        findings.append(_find("heading-multiple-h1", "headings", "moderate",
                              f"Page has {len(h1_lines)} <h1> elements",
                              fp, h1_lines[1][0], _snippet(h1_lines[1][1]),
                              "1.3.1 Info and Relationships",
                              "Use a single <h1> per page. Demote others to <h2>+."))
    # Skipped levels
    prev_level = 0
    for lvl, ln, line in heading_levels:
        if prev_level > 0 and lvl > prev_level + 1:
            findings.append(_find("heading-skipped", "headings", "moderate",
                                  f"Heading level skips from h{prev_level} to h{lvl}",
                                  fp, ln, _snippet(line),
                                  "1.3.1 Info and Relationships",
                                  f"Use <h{prev_level + 1}> instead of <h{lvl}>."))
        prev_level = lvl
    return findings
def check_landmarks(lines, fp):
    findings = []
    content = "\n".join(lines)
    # Missing main landmark
    if not re.search(r'<main\b|role\s*=\s*["\']main["\']', content, re.I):
        findings.append(_find("landmark-no-main", "landmarks", "serious",
                              "Page missing <main> landmark",
                              fp, 1, "", "1.3.1 Info and Relationships",
                              "Add a <main> element to wrap primary content."))
    # Missing nav
    if not re.search(r'<nav\b|role\s*=\s*["\']navigation["\']', content, re.I):
        findings.append(_find("landmark-no-nav", "landmarks", "moderate",
                              "Page missing <nav> landmark",
                              fp, 1, "", "1.3.1 Info and Relationships",
                              "Add <nav> for primary navigation blocks."))
    # Missing skip link
    if not re.search(r'skip.{0,10}(nav|main|content)', content, re.I):
        findings.append(_find("landmark-no-skip-link", "landmarks", "serious",
                              "Page missing skip navigation link",
                              fp, 1, "", "2.4.1 Bypass Blocks",
                              "Add <a href=\"#main\">Skip to main content</a> as first focusable element."))
    return findings
def check_tabindex_positive(tag, attrs, fp, ln, snip):
    ti = attrs.get("tabindex", "")
    if isinstance(ti, str) and ti.lstrip("-").isdigit() and int(ti) > 0:
        return _find("keyboard-tabindex-positive", "keyboard", "serious",
                      f"tabindex={ti} creates unexpected tab order",
                      fp, ln, snip, "2.4.3 Focus Order",
                      "Use tabindex=\"0\" or tabindex=\"-1\" instead of positive values.")
def check_click_no_keyboard(tag, attrs, fp, ln, snip):
    has_click = "onClick" in attrs or "onclick" in attrs or "@click" in attrs or "on:click" in attrs
    has_key = any(k for k in attrs if "keydown" in k.lower() or "keyup" in k.lower() or "keypress" in k.lower())
    if tag in ("div", "span", "td", "li", "p", "section") and has_click and not has_key:
        if attrs.get("role") not in ("button", "link", "tab", "menuitem"):
            return _find("keyboard-click-no-key", "keyboard", "critical",
                          f"<{tag}> has click handler but no keyboard handler",
                          fp, ln, snip, "2.1.1 Keyboard",
                          f"Add onKeyDown handler or use <button> instead of <{tag}>.")
def check_autofocus_misuse(tag, attrs, fp, ln, snip):
    if "autofocus" in attrs or "autoFocus" in attrs:
        if tag not in ("input", "textarea", "select"):
            return _find("keyboard-autofocus", "keyboard", "moderate",
                          f"autofocus on <{tag}> can disorient screen reader users",
                          fp, ln, snip, "3.2.1 On Focus",
                          "Avoid autofocus on non-input elements. Use focus management instead.")
def check_invalid_aria(tag, attrs, fp, ln, snip):
    findings = []
    for key in attrs:
        if key.startswith("aria-") and key.lower() not in VALID_ARIA_ATTRS:
            findings.append(_find("aria-invalid-attr", "aria", "serious",
                                  f"Invalid ARIA attribute: {key}",
                                  fp, ln, snip, "4.1.2 Name, Role, Value",
                                  f"Remove or replace \"{key}\" with a valid ARIA attribute."))
    return findings
def check_aria_hidden_focusable(tag, attrs, fp, ln, snip):
    if attrs.get("aria-hidden") in ("true", True):
        focusable_tags = {"a", "button", "input", "select", "textarea"}
        if tag in focusable_tags or (isinstance(attrs.get("tabindex", ""), str) and
                                     attrs.get("tabindex", "-1") != "-1"):
            return _find("aria-hidden-focusable", "aria", "critical",
                          f"aria-hidden=\"true\" on focusable <{tag}>",
                          fp, ln, snip, "4.1.2 Name, Role, Value",
                          "Remove aria-hidden or make element non-focusable (tabindex=\"-1\").")
def check_aria_live_missing(lines, fp):
    """Alert/status roles or live regions without aria-live."""
    findings = []
    for ln, line in enumerate(lines, 1):
        if re.search(r'role\s*=\s*["\'](?:alert|status)["\']', line, re.I):
            if "aria-live" not in line:
                findings.append(_find("aria-live-missing", "aria", "serious",
                                      "role=alert/status without explicit aria-live",
                                      fp, ln, _snippet(line),
                                      "4.1.3 Status Messages",
                                      "Add aria-live=\"assertive\" (alert) or aria-live=\"polite\" (status)."))
    return findings
def check_inline_color(tag, attrs, fp, ln, snip):
    style = attrs.get("style", "")
    if isinstance(style, str) and re.search(r"\bcolor\s*:", style, re.I):
        if not re.search(r"background", style, re.I):
            return _find("color-inline-no-bg", "color", "moderate",
                          "Inline color set without background — contrast may be insufficient",
                          fp, ln, snip, "1.4.3 Contrast (Minimum)",
                          "Ensure foreground and background colors meet 4.5:1 contrast ratio.")
def check_text_over_image(lines, fp):
    """Detects patterns where text is positioned over background images without overlay."""
    findings = []
    for ln, line in enumerate(lines, 1):
        if re.search(r"background-image\s*:", line, re.I):
            if not re.search(r"(overlay|rgba|linear-gradient)", line, re.I):
                findings.append(_find("color-text-over-image", "color", "serious",
                                      "Background image without contrast overlay for text",
                                      fp, ln, _snippet(line),
                                      "1.4.3 Contrast (Minimum)",
                                      "Add a semi-transparent overlay or ensure text contrast."))
    return findings
