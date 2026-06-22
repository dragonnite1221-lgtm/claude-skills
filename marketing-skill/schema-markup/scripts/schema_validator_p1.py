# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_validator_base import *  # noqa: F403,E402


SCHEMA_RULES: Dict[str, Dict[str, List[str]]] = {
    "Article": {
        "required": ["headline", "image", "datePublished", "author"],
        "recommended": ["dateModified", "publisher", "description", "url", "mainEntityOfPage"],
    },
    "BlogPosting": {
        "required": ["headline", "image", "datePublished", "author"],
        "recommended": ["dateModified", "publisher", "description", "url", "mainEntityOfPage"],
    },
    "NewsArticle": {
        "required": ["headline", "image", "datePublished", "author"],
        "recommended": ["dateModified", "publisher", "description", "url"],
    },
    "HowTo": {
        "required": ["name", "step"],
        "recommended": ["description", "image", "totalTime", "tool", "supply", "estimatedCost"],
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "recommended": [],
    },
    "Product": {
        "required": ["name", "offers"],
        "recommended": ["description", "image", "sku", "brand", "aggregateRating"],
    },
    "Organization": {
        "required": ["name", "url"],
        "recommended": ["logo", "sameAs", "contactPoint", "description", "foundingDate"],
    },
    "LocalBusiness": {
        "required": ["name", "address"],
        "recommended": ["telephone", "openingHoursSpecification", "geo", "priceRange", "image", "url"],
    },
    "BreadcrumbList": {
        "required": ["itemListElement"],
        "recommended": [],
    },
    "VideoObject": {
        "required": ["name", "description", "thumbnailUrl", "uploadDate"],
        "recommended": ["duration", "contentUrl", "embedUrl", "interactionStatistic", "hasPart"],
    },
    "WebSite": {
        "required": ["url"],
        "recommended": ["name", "potentialAction"],
    },
    "Event": {
        "required": ["name", "startDate", "location"],
        "recommended": ["endDate", "description", "image", "organizer", "offers"],
    },
    "Recipe": {
        "required": ["name", "image", "author", "datePublished"],
        "recommended": ["description", "cookTime", "prepTime", "totalTime", "recipeYield",
                        "recipeIngredient", "recipeInstructions", "aggregateRating"],
    },
}
KNOWN_TYPES = set(SCHEMA_RULES.keys())
class JSONLDExtractor(HTMLParser):
    """Extracts all <script type="application/ld+json"> blocks from HTML."""

    def __init__(self):
        super().__init__()
        self.blocks: List[str] = []
        self._in_ld_json = False
        self._current = []

    def handle_starttag(self, tag: str, attrs: list):
        if tag.lower() == "script":
            attr_dict = dict(attrs)
            if attr_dict.get("type", "").lower() == "application/ld+json":
                self._in_ld_json = True
                self._current = []

    def handle_endtag(self, tag: str):
        if tag.lower() == "script" and self._in_ld_json:
            self._in_ld_json = False
            self.blocks.append("".join(self._current).strip())

    def handle_data(self, data: str):
        if self._in_ld_json:
            self._current.append(data)
def detect_type(obj: Dict) -> Optional[str]:
    """Determine the @type of a schema object."""
    t = obj.get("@type")
    if isinstance(t, list):
        # Return first known type
        for item in t:
            if item in KNOWN_TYPES:
                return item
        return t[0] if t else None
    return t
