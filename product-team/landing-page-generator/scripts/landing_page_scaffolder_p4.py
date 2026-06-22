# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from landing_page_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from landing_page_scaffolder_p1 import escape  # noqa: E402,E501
from landing_page_scaffolder_p3 import generate_css  # noqa: E402,E501
# fmt: on


def render_nav(config: Dict[str, Any]) -> str:
    brand = escape(config.get("brand", "Brand"))
    nav_links = config.get("nav_links", [])
    cta = config.get("nav_cta", {"text": "Get Started", "url": "#"})
    links = "\n".join(
        f'<li><a href="{escape(l.get("url", "#"))}">{escape(l.get("text", ""))}</a></li>'
        for l in nav_links
    )
    return f"""
    <nav><div class="container">
        <a href="#" class="nav-logo">{brand}</a>
        <ul class="nav-links">{links}</ul>
        <a href="{escape(cta.get('url', '#'))}" class="nav-cta">{escape(cta.get('text', 'Get Started'))}</a>
    </div></nav>"""
def render_hero(hero: Dict[str, Any]) -> str:
    h1 = escape(hero.get("headline", "Your Headline Here"))
    sub = escape(hero.get("subheadline", ""))
    primary_cta = hero.get("primary_cta", {"text": "Get Started", "url": "#"})
    secondary_cta = hero.get("secondary_cta", None)
    cta_html = f'<a href="{escape(primary_cta.get("url", "#"))}" class="btn-primary">{escape(primary_cta.get("text", "Get Started"))}</a>'
    if secondary_cta:
        cta_html += f'\n<a href="{escape(secondary_cta.get("url", "#"))}" class="btn-secondary">{escape(secondary_cta.get("text", "Learn More"))}</a>'
    return f"""
    <section class="hero"><div class="container">
        <h1>{h1}</h1>
        <p>{sub}</p>
        <div class="hero-cta">{cta_html}</div>
    </div></section>"""
def render_features(features: Dict[str, Any]) -> str:
    title = escape(features.get("title", "Features"))
    subtitle = escape(features.get("subtitle", ""))
    items = features.get("items", [])
    cards = "\n".join(f"""
        <div class="feature-card">
            <div class="feature-icon">{escape(f.get('icon', ''))}</div>
            <h3>{escape(f.get('title', ''))}</h3>
            <p>{escape(f.get('description', ''))}</p>
        </div>""" for f in items)
    return f"""
    <section class="features"><div class="container">
        <h2 class="section-title">{title}</h2>
        <p class="section-subtitle">{subtitle}</p>
        <div class="features-grid">{cards}</div>
    </div></section>"""
def render_testimonials(testimonials: Dict[str, Any]) -> str:
    title = escape(testimonials.get("title", "What Our Customers Say"))
    items = testimonials.get("items", [])
    if not items:
        return ""
    cards = "\n".join(f"""
        <div class="testimonial-card">
            <p class="testimonial-text">"{escape(t.get('quote', ''))}"</p>
            <div class="testimonial-author">
                <div class="author-info">
                    <strong>{escape(t.get('name', ''))}</strong>
                    <span>{escape(t.get('title', ''))}, {escape(t.get('company', ''))}</span>
                </div>
            </div>
        </div>""" for t in items)
    return f"""
    <section class="testimonials"><div class="container">
        <h2 class="section-title">{title}</h2>
        <div class="testimonials-grid">{cards}</div>
    </div></section>"""
def render_pricing(pricing: Dict[str, Any]) -> str:
    title = escape(pricing.get("title", "Pricing"))
    plans = pricing.get("plans", [])
    if not plans:
        return ""
    cards = "\n".join(f"""
        <div class="pricing-card {'featured' if p.get('featured') else ''}">
            <div class="pricing-name">{escape(p.get('name', ''))}</div>
            <div class="pricing-price">${escape(str(p.get('price', '0')))}<span>/mo</span></div>
            <p>{escape(p.get('description', ''))}</p>
            <ul class="pricing-features">
                {"".join(f'<li>{escape(f)}</li>' for f in p.get('features', []))}
            </ul>
            <a href="{escape(p.get('cta_url', '#'))}" class="btn-primary">{escape(p.get('cta_text', 'Choose Plan'))}</a>
        </div>""" for p in plans)
    return f"""
    <section class="pricing"><div class="container">
        <h2 class="section-title">{title}</h2>
        <div class="pricing-grid">{cards}</div>
    </div></section>"""
def render_cta(cta: Dict[str, Any]) -> str:
    return f"""
    <section class="cta-section"><div class="container">
        <h2>{escape(cta.get('headline', 'Ready to get started?'))}</h2>
        <p>{escape(cta.get('subheadline', ''))}</p>
        <a href="{escape(cta.get('url', '#'))}" class="btn-white">{escape(cta.get('text', 'Start Free Trial'))}</a>
    </div></section>"""
def generate_html(config: Dict[str, Any]) -> str:
    """Generate complete HTML landing page."""
    title = escape(config.get("title", "Landing Page"))
    css = generate_css(config)
    sections = []
    sections.append(render_nav(config))
    if config.get("hero"):
        sections.append(render_hero(config["hero"]))
    if config.get("features"):
        sections.append(render_features(config["features"]))
    if config.get("testimonials"):
        sections.append(render_testimonials(config["testimonials"]))
    if config.get("pricing"):
        sections.append(render_pricing(config["pricing"]))
    if config.get("cta"):
        sections.append(render_cta(config["cta"]))
    sections.append(f"""
    <footer><div class="container">
        <p>{escape(config.get('footer_text', f'{datetime.now().year} {config.get("brand", "Company")}. All rights reserved.'))}</p>
    </div></footer>""")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{escape(config.get('meta_description', ''))}">
    <style>{css}</style>
</head>
<body>
{"".join(sections)}
</body>
</html>"""
