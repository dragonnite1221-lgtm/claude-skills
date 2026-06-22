# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from form_field_analyzer_base import *  # noqa: F403,E402
# fmt: off
from form_field_analyzer_p1 import FormAnalyzer  # noqa: E402,E501
from form_field_analyzer_p2 import analyze_form, format_report  # noqa: E402,E501
# fmt: on


SAMPLE_HTML = """
<form action="/submit" method="POST">
  <label for="name">Full Name</label>
  <input type="text" name="name" id="name" required placeholder="John Smith">

  <label for="email">Work Email</label>
  <input type="email" name="email" id="email" required placeholder="you@company.com">

  <label for="company">Company</label>
  <input type="text" name="company" id="company" required>

  <label for="phone">Phone Number</label>
  <input type="tel" name="phone" id="phone" required>

  <label for="role">Job Title</label>
  <input type="text" name="role" id="role" required>

  <label for="employees">Company Size</label>
  <select name="employees" id="employees" required>
    <option value="">Select...</option>
    <option value="1-10">1-10</option>
    <option value="11-50">11-50</option>
    <option value="51-200">51-200</option>
    <option value="200+">200+</option>
  </select>

  <label for="message">How can we help?</label>
  <textarea name="message" id="message" placeholder="Tell us about your needs..."></textarea>

  <button type="submit">Submit</button>
</form>
"""
def main():
    use_json = "--json" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--json"]

    if args and os.path.isfile(args[0]):
        with open(args[0]) as f:
            html = f.read()
    else:
        if not args:
            print("[Demo mode — analyzing sample lead capture form]")
        html = SAMPLE_HTML

    parser = FormAnalyzer()
    parser.feed(html)

    if not parser.forms:
        print("No <form> elements found in the HTML.")
        sys.exit(1)

    analyses = [analyze_form(form) for form in parser.forms]

    if use_json:
        print(json.dumps(analyses, indent=2))
    else:
        print(format_report(analyses))
