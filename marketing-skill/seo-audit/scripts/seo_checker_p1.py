# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_checker_base import *  # noqa: F403,E402


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta_description = ""
        self.h_tags = []          # list of (level, text)
        self._current_h = None
        self._current_h_text = []
        self.images = []          # list of {"src": ..., "alt": ...}
        self._in_body = False
        self.links = []           # list of {"href": ..., "text": ...}
        self._current_link_text = []
        self._current_link_href = ""
        self._in_link = False
        self.body_text_parts = []
        self._in_script = False
        self._in_style = False
        self.viewport_meta = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        tag = tag.lower()

        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name == "description":
                self.meta_description = attrs_dict.get("content", "")
            if name == "viewport":
                self.viewport_meta = True
            if prop == "og:description" and not self.meta_description:
                self.meta_description = attrs_dict.get("content", "")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._current_h = int(tag[1])
            self._current_h_text = []
        elif tag == "img":
            self.images.append({
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt", None),
            })
        elif tag == "a":
            self._in_link = True
            self._current_link_href = attrs_dict.get("href", "")
            self._current_link_text = []
        elif tag == "body":
            self._in_body = True
        elif tag == "script":
            self._in_script = True
        elif tag == "style":
            self._in_style = True

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            if self._current_h is not None:
                self.h_tags.append((self._current_h, " ".join(self._current_h_text).strip()))
            self._current_h = None
            self._current_h_text = []
        elif tag == "a":
            if self._in_link:
                self.links.append({
                    "href": self._current_link_href,
                    "text": " ".join(self._current_link_text).strip(),
                })
            self._in_link = False
            self._current_link_text = []
            self._current_link_href = ""
        elif tag == "script":
            self._in_script = False
        elif tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._current_h is not None:
            self._current_h_text.append(data)
        if self._in_link:
            self._current_link_text.append(data)
        if self._in_body and not self._in_script and not self._in_style:
            self.body_text_parts.append(data)
def _is_external(href, base_domain=""):
    if not href:
        return False
    return href.startswith("http://") or href.startswith("https://")
