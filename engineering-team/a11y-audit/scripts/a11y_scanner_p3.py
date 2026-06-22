# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from a11y_scanner_base import *  # noqa: F403,E402
# fmt: off
from a11y_scanner_p1 import BAD_LINK_TEXT, _find, _snippet, check_img_decorative_has_alt, check_img_empty_alt_informative, check_img_missing_alt, check_input_missing_label, check_input_no_aria_label  # noqa: E402,E501
from a11y_scanner_p2 import check_aria_hidden_focusable, check_autofocus_misuse, check_click_no_keyboard, check_inline_color, check_invalid_aria, check_tabindex_positive  # noqa: E402,E501
# fmt: on


def check_empty_link(tag, attrs, fp, ln, snip):
    if tag == "a" and not attrs.get("aria-label") and not attrs.get("aria-labelledby"):
        return None  # handled by line-level check below
def check_empty_links_line(lines, fp):
    findings = []
    for ln, line in enumerate(lines, 1):
        # <a ...></a> or <a ...> </a>
        if re.search(r"<a\b[^>]*>\s*</a>", line, re.I):
            if "aria-label" not in line and "aria-labelledby" not in line:
                findings.append(_find("link-empty", "links", "critical",
                                      "Empty link — no text or accessible name",
                                      fp, ln, _snippet(line), "2.4.4 Link Purpose",
                                      "Add link text or aria-label."))
        # Bad link text
        if BAD_LINK_TEXT.search(line):
            findings.append(_find("link-bad-text", "links", "serious",
                                  "Link uses vague text like 'click here'",
                                  fp, ln, _snippet(line), "2.4.4 Link Purpose",
                                  "Use descriptive link text that makes sense out of context."))
    return findings
def check_same_page_link(tag, attrs, fp, ln, snip):
    href = attrs.get("href", "")
    if tag == "a" and isinstance(href, str) and href == "#":
        return _find("link-empty-fragment", "links", "moderate",
                      "Link with href=\"#\" — use a button or valid fragment",
                      fp, ln, snip, "2.4.4 Link Purpose",
                      "Use <button> for actions or href=\"#section-id\" for anchors.")
def check_table_headers(lines, fp):
    findings = []
    in_table = False
    table_start = 0
    has_th = False
    has_caption = False
    has_aria_label = False
    for ln, line in enumerate(lines, 1):
        if re.search(r"<table\b", line, re.I):
            in_table = True
            table_start = ln
            has_th = False
            has_caption = False
            has_aria_label = "aria-label" in line
        if in_table:
            if "<th" in line.lower():
                has_th = True
            if "<caption" in line.lower():
                has_caption = True
            if re.search(r"</table>", line, re.I):
                if not has_th:
                    findings.append(_find("table-no-headers", "tables", "serious",
                                          "<table> has no <th> header cells",
                                          fp, table_start, _snippet(lines[table_start - 1]),
                                          "1.3.1 Info and Relationships",
                                          "Add <th> elements to identify column/row headers."))
                if not has_caption and not has_aria_label:
                    findings.append(_find("table-no-caption", "tables", "moderate",
                                          "<table> missing <caption> or aria-label",
                                          fp, table_start, _snippet(lines[table_start - 1]),
                                          "1.3.1 Info and Relationships",
                                          "Add <caption> or aria-label to describe the table."))
                in_table = False
    return findings
def check_media_captions(tag, attrs, fp, ln, snip):
    if tag == "video":
        return None  # handled at block level
def check_media_captions_block(lines, fp):
    findings = []
    in_video = False
    video_start = 0
    has_track = False
    has_controls = False
    has_autoplay = False
    for ln, line in enumerate(lines, 1):
        if re.search(r"<video\b", line, re.I):
            in_video = True
            video_start = ln
            has_track = False
            has_controls = "controls" in line.lower()
            has_autoplay = "autoplay" in line.lower()
        if in_video:
            if re.search(r'<track\b[^>]*kind\s*=\s*["\']captions["\']', line, re.I):
                has_track = True
            if "controls" in line.lower():
                has_controls = True
            if re.search(r"</video>", line, re.I) or (re.search(r"<video\b", line, re.I) and "/>" in line):
                if not has_track:
                    findings.append(_find("media-no-captions", "media", "critical",
                                          "<video> missing captions track",
                                          fp, video_start, _snippet(lines[video_start - 1]),
                                          "1.2.2 Captions (Prerecorded)",
                                          "Add <track kind=\"captions\" src=\"...\" srclang=\"en\">."))
                if has_autoplay and not has_controls:
                    findings.append(_find("media-autoplay-no-controls", "media", "serious",
                                          "<video> has autoplay without controls",
                                          fp, video_start, _snippet(lines[video_start - 1]),
                                          "1.4.2 Audio Control",
                                          "Add the controls attribute so users can pause/stop."))
                in_video = False
    # Single-line video tags
    for ln, line in enumerate(lines, 1):
        if re.search(r"<audio\b", line, re.I):
            if "autoplay" in line.lower() and "controls" not in line.lower():
                findings.append(_find("media-audio-autoplay", "media", "serious",
                                      "<audio> has autoplay without controls",
                                      fp, ln, _snippet(line), "1.4.2 Audio Control",
                                      "Add the controls attribute to <audio>."))
    return findings
SUPPORTED_EXTENSIONS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".css"}
TAG_LEVEL_CHECKS = [
    check_img_missing_alt,
    check_img_empty_alt_informative,
    check_img_decorative_has_alt,
    check_input_missing_label,
    check_input_no_aria_label,
    check_tabindex_positive,
    check_click_no_keyboard,
    check_autofocus_misuse,
    check_aria_hidden_focusable,
    check_inline_color,
    check_same_page_link,
]
TAG_LEVEL_MULTI_CHECKS = [
    check_invalid_aria,
]
