# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from a11y_scanner_base import *  # noqa: F403,E402


@dataclass
class Finding:
    """A single accessibility finding."""
    rule_id: str
    category: str
    severity: str
    message: str
    file: str
    line: int
    snippet: str
    wcag_criterion: str
    fix: str
VALID_ARIA_ATTRS = {
    "aria-activedescendant", "aria-atomic", "aria-autocomplete", "aria-busy",
    "aria-checked", "aria-colcount", "aria-colindex", "aria-colspan",
    "aria-controls", "aria-current", "aria-describedby", "aria-details",
    "aria-disabled", "aria-dropeffect", "aria-errormessage", "aria-expanded",
    "aria-flowto", "aria-grabbed", "aria-haspopup", "aria-hidden",
    "aria-invalid", "aria-keyshortcuts", "aria-label", "aria-labelledby",
    "aria-level", "aria-live", "aria-modal", "aria-multiline",
    "aria-multiselectable", "aria-orientation", "aria-owns", "aria-placeholder",
    "aria-posinset", "aria-pressed", "aria-readonly", "aria-relevant",
    "aria-required", "aria-roledescription", "aria-rowcount", "aria-rowindex",
    "aria-rowspan", "aria-selected", "aria-setsize", "aria-sort",
    "aria-valuemax", "aria-valuemin", "aria-valuenow", "aria-valuetext",
    "aria-braillelabel", "aria-brailleroledescription", "aria-description",
}
BAD_LINK_TEXT = re.compile(
    r">\s*(click here|here|read more|more|link|this)\s*<", re.IGNORECASE
)
TAG_RE = re.compile(r"<(\w[\w-]*)\b([^>]*)(/?)>", re.DOTALL)
ATTR_RE = re.compile(r"""([\w:.-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|(\S+))""")
ATTR_BOOL_RE = re.compile(r"\b([\w:.-]+)(?=\s|/?>|$)")
INLINE_COLOR_RE = re.compile(
    r'style\s*=\s*["\'][^"\']*\bcolor\s*:', re.IGNORECASE
)
ARIA_ATTR_RE = re.compile(r"\baria-[\w-]+")
def _attrs(attr_str: str) -> dict:
    """Parse HTML/JSX attribute string into a dict."""
    result = {}
    for m in ATTR_RE.finditer(attr_str):
        result[m.group(1)] = m.group(2) or m.group(3) or m.group(4) or ""
    # boolean attrs
    cleaned = ATTR_RE.sub("", attr_str)
    for m in ATTR_BOOL_RE.finditer(cleaned):
        name = m.group(1)
        if name not in result and not name.startswith("/"):
            result[name] = True
    return result
def _snippet(line_text: str) -> str:
    """Trim a line for display as a code snippet."""
    s = line_text.rstrip("\n\r")
    return s[:120] + "..." if len(s) > 120 else s
def _find(rule_id, cat, sev, msg, fp, ln, snip, wcag, fix):
    return Finding(rule_id, cat, sev, msg, fp, ln, snip, wcag, fix)
def check_img_missing_alt(tag, attrs, fp, ln, snip):
    if tag == "img" and "alt" not in attrs:
        return _find("img-alt-missing", "images", "critical",
                      "<img> missing alt attribute",
                      fp, ln, snip, "1.1.1 Non-text Content",
                      "Add alt=\"description\" or alt=\"\" for decorative images.")
def check_img_empty_alt_informative(tag, attrs, fp, ln, snip):
    if tag == "img" and attrs.get("alt") == "" and attrs.get("src", ""):
        src = attrs.get("src", "")
        if not any(kw in src.lower() for kw in ("spacer", "border", "decorat", "bg")):
            return _find("img-alt-empty-informative", "images", "serious",
                          "<img> has empty alt but may be informative",
                          fp, ln, snip, "1.1.1 Non-text Content",
                          "If image conveys information, add descriptive alt text.")
def check_img_decorative_has_alt(tag, attrs, fp, ln, snip):
    if tag == "img" and attrs.get("role") == "presentation" and attrs.get("alt", "") != "":
        return _find("img-decorative-alt", "images", "moderate",
                      "Decorative image (role=presentation) should have alt=\"\"",
                      fp, ln, snip, "1.1.1 Non-text Content",
                      "Set alt=\"\" on decorative images with role=presentation.")
def check_input_missing_label(tag, attrs, fp, ln, snip):
    input_types = {"text", "email", "password", "search", "tel", "url", "number", "date"}
    if tag == "input" and attrs.get("type", "text") in input_types:
        if "aria-label" not in attrs and "aria-labelledby" not in attrs and "id" not in attrs:
            return _find("form-input-no-label", "forms", "critical",
                          "<input> has no id, aria-label, or aria-labelledby",
                          fp, ln, snip, "1.3.1 Info and Relationships",
                          "Add id + <label for>, or aria-label attribute.")
def check_input_no_aria_label(tag, attrs, fp, ln, snip):
    if tag in ("select", "textarea"):
        if "aria-label" not in attrs and "aria-labelledby" not in attrs and "id" not in attrs:
            return _find("form-select-no-label", "forms", "critical",
                          f"<{tag}> has no accessible name",
                          fp, ln, snip, "4.1.2 Name, Role, Value",
                          f"Add aria-label or id + <label for> to <{tag}>.")
def check_orphan_label(lines, fp):
    """Labels whose 'for' points to a non-existent id."""
    findings = []
    ids = set()
    label_fors = []
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r'\bid\s*=\s*["\']([^"\']+)["\']', line):
            ids.add(m.group(1))
        for m in re.finditer(r'<label[^>]*\bfor\s*=\s*["\']([^"\']+)["\']', line):
            label_fors.append((ln, m.group(1), line))
    for ln, for_val, line in label_fors:
        if for_val not in ids:
            findings.append(_find("form-orphan-label", "forms", "serious",
                                  f"<label for=\"{for_val}\"> references non-existent id",
                                  fp, ln, _snippet(line), "1.3.1 Info and Relationships",
                                  f"Ensure an element with id=\"{for_val}\" exists."))
    return findings
def check_fieldset_legend(lines, fp):
    """Radio/checkbox groups without fieldset."""
    findings = []
    radio_lines = []
    has_fieldset = any("fieldset" in l.lower() for l in lines)
    for ln, line in enumerate(lines, 1):
        if re.search(r'type\s*=\s*["\'](?:radio|checkbox)["\']', line, re.I):
            radio_lines.append((ln, line))
    if radio_lines and not has_fieldset:
        ln, line = radio_lines[0]
        findings.append(_find("form-missing-fieldset", "forms", "serious",
                              "Radio/checkbox group without <fieldset>/<legend>",
                              fp, ln, _snippet(line), "1.3.1 Info and Relationships",
                              "Wrap related radio/checkbox inputs in <fieldset> with <legend>."))
    return findings
