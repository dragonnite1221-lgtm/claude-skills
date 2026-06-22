# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from sitemap_analyzer_base import *  # noqa: F403,E402


SITEMAP_NAMESPACES = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
    "video": "http://www.google.com/schemas/sitemap-video/1.1",
    "news": "http://www.google.com/schemas/sitemap-news/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}
SAMPLE_SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

  <!-- Homepage -->
  <url>
    <loc>https://example.com/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>

  <!-- Top-level pages -->
  <url><loc>https://example.com/pricing</loc></url>
  <url><loc>https://example.com/about</loc></url>
  <url><loc>https://example.com/contact</loc></url>
  <url><loc>https://example.com/blog</loc></url>

  <!-- Features section -->
  <url><loc>https://example.com/features</loc></url>
  <url><loc>https://example.com/features/email-automation</loc></url>
  <url><loc>https://example.com/features/crm-integration</loc></url>
  <url><loc>https://example.com/features/analytics</loc></url>

  <!-- Solutions section -->
  <url><loc>https://example.com/solutions/sales-teams</loc></url>
  <url><loc>https://example.com/solutions/marketing-teams</loc></url>

  <!-- Blog posts (various topics) -->
  <url><loc>https://example.com/blog/cold-email-guide</loc></url>
  <url><loc>https://example.com/blog/email-open-rates</loc></url>
  <url><loc>https://example.com/blog/crm-comparison</loc></url>
  <url><loc>https://example.com/blog/sales-process-optimization</loc></url>

  <!-- Deeply nested pages (potential issue) -->
  <url><loc>https://example.com/resources/guides/email/cold-outreach/advanced/templates</loc></url>
  <url><loc>https://example.com/resources/guides/email/cold-outreach/advanced/scripts</loc></url>

  <!-- Duplicate path patterns (potential issue) -->
  <url><loc>https://example.com/blog/email-tips</loc></url>
  <url><loc>https://example.com/resources/email-tips</loc></url>

  <!-- Dynamic-looking URL (potential issue) -->
  <url><loc>https://example.com/search?q=cold+email&amp;sort=recent</loc></url>

  <!-- Case studies -->
  <url><loc>https://example.com/customers/acme-corp</loc></url>
  <url><loc>https://example.com/customers/globex</loc></url>

  <!-- Legal pages (often over-linked) -->
  <url><loc>https://example.com/privacy</loc></url>
  <url><loc>https://example.com/terms</loc></url>

</urlset>
"""
def get_depth(path: str) -> int:
    """Return depth of a URL path. / = 0, /blog = 1, /blog/post = 2, etc."""
    parts = [p for p in path.strip("/").split("/") if p]
    return len(parts)
def get_path_pattern(path: str) -> str:
    """Replace variable segments with {slug} for pattern detection."""
    parts = path.strip("/").split("/")
    normalized = []
    for p in parts:
        if p:
            # Keep static segments (likely structure), replace dynamic-looking ones
            if re.match(r'^[a-z][-a-z]+$', p) and len(p) < 30:
                normalized.append(p)
            else:
                normalized.append("{slug}")
    return "/" + "/".join(normalized) if normalized else "/"
def has_query_params(url: str) -> bool:
    return "?" in url
def looks_like_dynamic_url(url: str) -> bool:
    parsed = urlparse(url)
    return bool(parsed.query)
def detect_path_siblings(urls: list) -> list:
    """Find URLs with same slug in different parent directories (potential duplicates)."""
    slug_to_paths = defaultdict(list)
    for url in urls:
        path = urlparse(url).path.strip("/")
        slug = path.split("/")[-1] if path else ""
        if slug:
            slug_to_paths[slug].append(url)

    duplicates = []
    for slug, paths in slug_to_paths.items():
        if len(paths) > 1:
            # Only flag if they're in different directories
            parents = set("/".join(urlparse(p).path.strip("/").split("/")[:-1]) for p in paths)
            if len(parents) > 1:
                duplicates.append({"slug": slug, "urls": paths})
    return duplicates
