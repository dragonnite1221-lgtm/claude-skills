# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from landing_page_scaffolder_base import *  # noqa: F403,E402


def tsx_testimonials(testimonials: Dict[str, Any], style: Dict[str, str]) -> str:
    title = testimonials.get("title", "What Our Customers Say")
    items = testimonials.get("items", [])
    if not items:
        return ""
    cards_jsx = "\n        ".join(
        f'''<div className="rounded-xl border {style["border"]} p-8">
          <p className="mb-6 text-lg italic {style["muted"]}">"{t.get("quote", "")}"</p>
          <div>
            <p className="font-semibold {style["text"]}">{t.get("name", "")}</p>
            <p className="text-sm {style["muted"]}">{t.get("title", "")}, {t.get("company", "")}</p>
          </div>
        </div>'''
        for t in items
    )
    return f'''function Testimonials() {{
  return (
    <section className="px-6 py-24 {style["bg"]}">
      <div className="mx-auto max-w-7xl">
        <h2 className="mb-16 text-center text-4xl font-bold {style["text"]}">{title}</h2>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {cards_jsx}
        </div>
      </div>
    </section>
  );
}}'''
def tsx_pricing(pricing: Dict[str, Any], style: Dict[str, str]) -> str:
    title = pricing.get("title", "Pricing")
    plans = pricing.get("plans", [])
    if not plans:
        return ""
    accent = style["accent"]
    cards = []
    for p in plans:
        featured = p.get("featured", False)
        border_cls = f"border-2 border-{accent}-500 ring-4 ring-{accent}-500/20" if featured else f"border {style['border']}"
        badge = f'\n            <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-{accent}-600 px-4 py-1 text-xs font-semibold text-white">Most Popular</div>' if featured else ""
        features_jsx = "\n              ".join(
            f'<li className="flex items-center gap-2 py-2"><span className="text-{accent}-500 font-bold">&#10003;</span> {feat}</li>'
            for feat in p.get("features", [])
        )
        cards.append(f'''<div className="relative rounded-2xl {border_cls} {style["card_bg"]} p-8 text-center">{badge}
            <h3 className="mb-2 text-xl font-semibold {style["text"]}">{p.get("name", "")}</h3>
            <div className="my-6 text-5xl font-extrabold {style["text"]}">${p.get("price", "0")}<span className="text-base font-normal {style["muted"]}">/mo</span></div>
            <p className="{style["muted"]} mb-6">{p.get("description", "")}</p>
            <ul className="mb-8 space-y-1 text-left {style["muted"]}">
              {features_jsx}
            </ul>
            <a href="{p.get("cta_url", "#")}" className="block w-full rounded-lg {style["btn"]} py-3 text-center font-semibold transition-colors">
              {p.get("cta_text", "Choose Plan")}
            </a>
          </div>''')
    cards_jsx = "\n        ".join(cards)
    return f'''function Pricing() {{
  return (
    <section className="{style["section_alt"]} px-6 py-24">
      <div className="mx-auto max-w-5xl">
        <h2 className="mb-16 text-center text-4xl font-bold {style["text"]}">{title}</h2>
        <div className="grid gap-8 lg:grid-cols-{min(len(plans), 3)}">
        {cards_jsx}
        </div>
      </div>
    </section>
  );
}}'''
def tsx_cta(cta: Dict[str, Any], style: Dict[str, str]) -> str:
    accent = style["accent"]
    return f'''function CTASection() {{
  return (
    <section className="bg-{accent}-600 px-6 py-24 text-center text-white">
      <div className="mx-auto max-w-3xl">
        <h2 className="mb-4 text-4xl font-bold">{cta.get("headline", "Ready to get started?")}</h2>
        <p className="mb-10 text-xl opacity-90">{cta.get("subheadline", "")}</p>
        <a href="{cta.get("url", "#")}" className="rounded-lg bg-white px-8 py-3 text-lg font-semibold text-{accent}-600 transition-colors hover:bg-gray-100">
          {cta.get("text", "Start Free Trial")}
        </a>
      </div>
    </section>
  );
}}'''
def tsx_footer(config: Dict[str, Any], style: Dict[str, str]) -> str:
    brand = config.get("brand", "Company")
    year = datetime.now().year
    footer_text = config.get("footer_text", f"{year} {brand}. All rights reserved.")
    return f'''function Footer() {{
  return (
    <footer className="border-t {style["border"]} {style["bg"]} px-6 py-10 text-center {style["muted"]}">
      <p>&copy; {footer_text}</p>
    </footer>
  );
}}'''
