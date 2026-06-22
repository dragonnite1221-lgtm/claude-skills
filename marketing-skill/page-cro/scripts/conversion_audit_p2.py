# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from conversion_audit_base import *  # noqa: F403,E402
# fmt: off
from conversion_audit_p1 import TESTIMONIAL_PATTERNS  # noqa: E402,E501
# fmt: on


TRUST_PATTERNS = {
    "ssl": [r'\b(ssl|https|secure|encrypted|tls|256.bit)\b'],
    "guarantee": [r'\b(guarantee|guaranteed|money.back|refund|risk.free|no.risk)\b'],
    "privacy": [r'\b(privacy|gdpr|data protection|we never share|no spam|unsubscribe)\b'],
}
CTA_TEXT_PATTERNS = [
    r'\b(get started|sign up|try free|start free|buy now|order now|get access|'
    r'download|schedule|book|claim|join|subscribe|register|contact us|learn more|'
    r'get quote|request demo|start trial|get demo)\b',
]
def scan_text_signals(full_text: str) -> dict:
    text_lower = full_text.lower()
    testimonials = sum(
        len(re.findall(p, text_lower, re.IGNORECASE))
        for p in TESTIMONIAL_PATTERNS
    )
    trust = {}
    for key, patterns in TRUST_PATTERNS.items():
        trust[key] = sum(len(re.findall(p, text_lower, re.IGNORECASE)) for p in patterns)

    cta_text_count = sum(
        len(re.findall(p, text_lower, re.IGNORECASE))
        for p in CTA_TEXT_PATTERNS
    )

    return {
        "testimonial_signals": min(testimonials, 20),
        "trust": trust,
        "cta_text_count": cta_text_count,
    }
def score_category(value, thresholds: list) -> int:
    """thresholds: [(min_value, score), ...] sorted asc. Returns score for first match."""
    for min_val, score in sorted(thresholds, reverse=True):
        if value >= min_val:
            return score
    return 0
