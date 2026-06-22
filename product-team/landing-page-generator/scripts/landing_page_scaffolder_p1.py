# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from landing_page_scaffolder_base import *  # noqa: F403,E402


def escape(text: str) -> str:
    """HTML-escape text."""
    return html_module.escape(str(text))
DESIGN_STYLES = {
    "dark-saas": {
        "bg": "bg-gray-950", "text": "text-white",
        "accent": "violet", "card_bg": "bg-gray-900 border border-gray-800",
        "btn": "bg-violet-600 hover:bg-violet-500 text-white",
        "btn_secondary": "border border-gray-700 text-gray-300 hover:bg-gray-800",
        "section_alt": "bg-gray-900/50", "muted": "text-gray-400",
        "border": "border-gray-800",
    },
    "clean-minimal": {
        "bg": "bg-white", "text": "text-gray-900",
        "accent": "blue", "card_bg": "bg-gray-50 border border-gray-200 rounded-2xl",
        "btn": "bg-blue-600 hover:bg-blue-700 text-white",
        "btn_secondary": "border border-gray-300 text-gray-700 hover:bg-gray-50",
        "section_alt": "bg-gray-50", "muted": "text-gray-500",
        "border": "border-gray-200",
    },
    "bold-startup": {
        "bg": "bg-white", "text": "text-gray-900",
        "accent": "orange", "card_bg": "shadow-xl rounded-3xl bg-white",
        "btn": "bg-orange-500 hover:bg-orange-600 text-white",
        "btn_secondary": "border-2 border-orange-500 text-orange-600 hover:bg-orange-50",
        "section_alt": "bg-orange-50/30", "muted": "text-gray-500",
        "border": "border-gray-200",
    },
    "enterprise": {
        "bg": "bg-slate-50", "text": "text-slate-900",
        "accent": "slate", "card_bg": "bg-white border border-slate-200 shadow-sm",
        "btn": "bg-slate-900 hover:bg-slate-800 text-white",
        "btn_secondary": "border border-slate-300 text-slate-700 hover:bg-slate-100",
        "section_alt": "bg-white", "muted": "text-slate-500",
        "border": "border-slate-200",
    },
}
def tsx_nav(config: Dict[str, Any], style: Dict[str, str]) -> str:
    brand = config.get("brand", "Brand")
    nav_links = config.get("nav_links", [])
    cta = config.get("nav_cta", {"text": "Get Started", "url": "#"})
    links_jsx = "\n          ".join(
        f'<a href="{l.get("url", "#")}" className="{style["muted"]} hover:{style["text"]} font-medium transition-colors">{l.get("text", "")}</a>'
        for l in nav_links
    )
    return f'''function Navbar() {{
  return (
    <nav className="sticky top-0 z-50 {style["bg"]} border-b {style["border"]} backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <a href="#" className="text-xl font-bold {style["text"]}">{brand}</a>
        <div className="hidden items-center gap-8 md:flex">
          {links_jsx}
          <a href="{cta.get("url", "#")}" className="rounded-lg {style["btn"]} px-5 py-2.5 text-sm font-semibold transition-colors">
            {cta.get("text", "Get Started")}
          </a>
        </div>
      </div>
    </nav>
  );
}}'''
def tsx_hero(hero: Dict[str, Any], style: Dict[str, str]) -> str:
    h1 = hero.get("headline", "Your Headline Here")
    sub = hero.get("subheadline", "")
    primary_cta = hero.get("primary_cta", {"text": "Get Started", "url": "#"})
    secondary_cta = hero.get("secondary_cta", None)
    secondary_jsx = ""
    if secondary_cta:
        secondary_jsx = f'''
          <a href="{secondary_cta.get("url", "#")}" className="rounded-lg {style["btn_secondary"]} px-8 py-3 text-lg font-semibold transition-colors">
            {secondary_cta.get("text", "Learn More")}
          </a>'''
    return f'''function Hero() {{
  return (
    <section className="flex min-h-[80vh] flex-col items-center justify-center px-6 py-24 text-center {style["bg"]}">
      <div className="mx-auto max-w-4xl">
        <h1 className="mb-6 text-5xl font-bold tracking-tight {style["text"]} md:text-7xl">
          {h1}
        </h1>
        <p className="mx-auto mb-10 max-w-2xl text-xl {style["muted"]}">
          {sub}
        </p>
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <a href="{primary_cta.get("url", "#")}" className="rounded-lg {style["btn"]} px-8 py-3 text-lg font-semibold transition-colors">
            {primary_cta.get("text", "Get Started")}
          </a>{secondary_jsx}
        </div>
      </div>
    </section>
  );
}}'''
def tsx_features(features: Dict[str, Any], style: Dict[str, str]) -> str:
    title = features.get("title", "Features")
    subtitle = features.get("subtitle", "")
    items = features.get("items", [])
    cards_jsx = "\n        ".join(
        f'''<div className="{style["card_bg"]} rounded-xl p-8">
          <div className="mb-4 text-3xl">{f.get("icon", "")}</div>
          <h3 className="mb-3 text-xl font-semibold {style["text"]}">{f.get("title", "")}</h3>
          <p className="{style["muted"]}">{f.get("description", "")}</p>
        </div>'''
        for f in items
    )
    return f'''function Features() {{
  return (
    <section className="{style["section_alt"]} px-6 py-24">
      <div className="mx-auto max-w-7xl">
        <h2 className="mb-4 text-center text-4xl font-bold {style["text"]}">{title}</h2>
        <p className="mx-auto mb-16 max-w-2xl text-center text-lg {style["muted"]}">{subtitle}</p>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {cards_jsx}
        </div>
      </div>
    </section>
  );
}}'''
