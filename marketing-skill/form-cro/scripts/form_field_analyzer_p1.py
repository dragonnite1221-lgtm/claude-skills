# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from form_field_analyzer_base import *  # noqa: F403,E402


class FormAnalyzer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current_form = None
        self.in_label = False
        self.current_label = ""
        self.in_button = False
        self.current_button = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == "form":
            self.current_form = {
                "action": attrs_dict.get("action", ""),
                "method": attrs_dict.get("method", "GET").upper(),
                "fields": [],
                "buttons": [],
                "has_autocomplete": "autocomplete" in attrs_dict
            }

        elif tag == "input" and self.current_form is not None:
            input_type = attrs_dict.get("type", "text").lower()
            if input_type not in ("hidden", "submit"):
                self.current_form["fields"].append({
                    "type": input_type,
                    "name": attrs_dict.get("name", ""),
                    "placeholder": attrs_dict.get("placeholder", ""),
                    "required": "required" in attrs_dict,
                    "autocomplete": attrs_dict.get("autocomplete", ""),
                    "has_label": False
                })
            elif input_type == "submit":
                self.current_form["buttons"].append(attrs_dict.get("value", "Submit"))

        elif tag == "textarea" and self.current_form is not None:
            self.current_form["fields"].append({
                "type": "textarea",
                "name": attrs_dict.get("name", ""),
                "placeholder": attrs_dict.get("placeholder", ""),
                "required": "required" in attrs_dict,
                "autocomplete": "",
                "has_label": False
            })

        elif tag == "select" and self.current_form is not None:
            self.current_form["fields"].append({
                "type": "select",
                "name": attrs_dict.get("name", ""),
                "placeholder": "",
                "required": "required" in attrs_dict,
                "autocomplete": "",
                "has_label": False
            })

        elif tag == "label":
            self.in_label = True
            self.current_label = ""
            for_attr = attrs_dict.get("for", "")
            if for_attr and self.current_form:
                for field in self.current_form["fields"]:
                    if field["name"] == for_attr:
                        field["has_label"] = True

        elif tag == "button":
            self.in_button = True
            self.current_button = ""

    def handle_data(self, data):
        if self.in_label:
            self.current_label += data.strip()
        if self.in_button:
            self.current_button += data.strip()

    def handle_endtag(self, tag):
        if tag == "form" and self.current_form:
            self.forms.append(self.current_form)
            self.current_form = None
        elif tag == "label":
            self.in_label = False
        elif tag == "button":
            self.in_button = False
            if self.current_button and self.current_form:
                self.current_form["buttons"].append(self.current_button)
