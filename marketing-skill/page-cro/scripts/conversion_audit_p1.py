# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from conversion_audit_base import *  # noqa: F403,E402


class CROParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._depth = 0
        self._above_fold_depth = 3  # approximate first screenful
        self._above_fold_elements = 0
        self._total_elements = 0

        self.buttons = []          # {"text": str, "position": int}
        self.links_as_cta = []     # a tags with CTA-like classes/text
        self.form_fields = 0
        self.forms = 0

        # Social proof
        self.testimonial_markers = 0
        self.logo_images = 0
        self.social_numbers = []   # "X customers", "X reviews", etc.

        # Trust signals
        self.ssl_mentions = 0
        self.guarantee_mentions = 0
        self.privacy_mentions = 0

        # Viewport meta
        self.viewport_meta = False

        # Tracking state
        self._in_body = False
        self._above_fold_done = False
        self._body_element_count = 0
        self._in_script = False
        self._in_style = False
        self._current_tag = None
        self._current_text = []
        self._element_position = 0  # rough position counter

        # Full text (for regex scans)
        self.full_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag_lower = tag.lower()

        if tag_lower == "script":
            self._in_script = True
            return
        if tag_lower == "style":
            self._in_style = True
            return

        if tag_lower == "body":
            self._in_body = True
            return

        if tag_lower == "meta":
            if attrs_dict.get("name", "").lower() == "viewport":
                self.viewport_meta = True

        if not self._in_body:
            return

        self._element_position += 1

        # Buttons
        if tag_lower == "button":
            self._current_tag = "button"
            self._current_text = []
        elif tag_lower == "input":
            input_type = attrs_dict.get("type", "text").lower()
            if input_type == "submit":
                val = attrs_dict.get("value", "Submit")
                self.buttons.append({"text": val, "position": self._element_position})
            elif input_type not in ("hidden", "submit"):
                self.form_fields += 1
        elif tag_lower == "textarea" or tag_lower == "select":
            self.form_fields += 1
        elif tag_lower == "form":
            self.forms += 1
        elif tag_lower == "a":
            cls = attrs_dict.get("class", "").lower()
            href = attrs_dict.get("href", "")
            cta_classes = {"btn", "button", "cta", "call-to-action", "signup", "register"}
            if any(c in cls for c in cta_classes):
                self._current_tag = "a_cta"
                self._current_text = []
        elif tag_lower == "img":
            src = attrs_dict.get("src", "").lower()
            alt = attrs_dict.get("alt", "").lower()
            cls = attrs_dict.get("class", "").lower()
            if any(kw in src or kw in alt or kw in cls
                   for kw in ("logo", "partner", "client", "badge", "seal", "award", "cert")):
                self.logo_images += 1

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == "script":
            self._in_script = False
        elif tag_lower == "style":
            self._in_style = False
        elif tag_lower == "button" and self._current_tag == "button":
            text = " ".join(self._current_text).strip()
            self.buttons.append({"text": text, "position": self._element_position})
            self._current_tag = None
            self._current_text = []
        elif tag_lower == "a" and self._current_tag == "a_cta":
            text = " ".join(self._current_text).strip()
            self.links_as_cta.append({"text": text, "position": self._element_position})
            self._current_tag = None
            self._current_text = []

    def handle_data(self, data):
        if self._in_script or self._in_style:
            return
        text = data.strip()
        if not text:
            return
        if self._current_tag in ("button", "a_cta"):
            self._current_text.append(text)
        if self._in_body:
            self.full_text.append(text)
TESTIMONIAL_PATTERNS = [
    r'\b(testimonial|review|quote|said|says|told us|customer story)\b',
    r'[""][^""]{20,}[""]',  # quoted text
    r'\b\d[\d,]+ (reviews?|customers?|users?|clients?|companies)\b',
    r'\bstar[s]?\b.{0,10}\b(rating|review)\b',
    r'\b(trustpilot|g2|capterra|clutch)\b',
]
