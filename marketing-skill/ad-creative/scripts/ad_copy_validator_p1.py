# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ad_copy_validator_base import *  # noqa: F403,E402


PLATFORM_SPECS = {
    "google_rsa": {
        "name": "Google RSA",
        "headline_max": 30,
        "headline_count_max": 15,
        "headline_count_min": 3,
        "description_max": 90,
        "description_count_max": 4,
        "description_count_min": 2,
    },
    "google_display": {
        "name": "Google Display",
        "headline_max": 30,
        "description_max": 90,
    },
    "meta_feed": {
        "name": "Meta (Facebook/Instagram) Feed",
        "primary_text_max": 125,   # preview limit; 2200 absolute max
        "headline_max": 40,
        "description_max": 30,
    },
    "linkedin": {
        "name": "LinkedIn Sponsored Content",
        "intro_text_max": 150,     # preview limit; 600 absolute max
        "headline_max": 70,
        "description_max": 100,
    },
    "twitter": {
        "name": "Twitter/X Promoted",
        "primary_text_max": 257,   # 280 - 23 chars for URL
    },
    "tiktok": {
        "name": "TikTok In-Feed",
        "primary_text_max": 100,
    },
}
TRADEMARKED_TERMS = [
    "facebook", "instagram", "google", "youtube", "tiktok", "twitter",
    "linkedin", "snapchat", "whatsapp", "amazon", "apple", "microsoft",
]
PROHIBITED_PHRASES = [
    "click here",
    "limited time offer",  # allowed if real — flagged for review
    "guaranteed",
    "100% free",
    "act now",
    "best in class",
    "world's best",
    "#1 rated",
    "number one",
]
SUSPICIOUS_PATTERNS = [
    r"\$\d{3,}[k+]?\s*per\s*(day|week|month)",   # "make $1,000 per day"
    r"\d{3,}%\s*(return|roi|profit|gain)",         # "300% return"
    r"(cure|treat|heal|eliminate)\s+\w+",          # health claims
    r"lose\s+\d+\s*(pound|lb|kg)",                 # weight loss claims
]
def count_chars(text):
    return len(text.strip())
def check_all_caps(text):
    """Returns True if more than 30% of alpha chars are uppercase — not counting acronyms."""
    words = text.split()
    violations = []
    for word in words:
        alpha = re.sub(r'[^a-zA-Z]', '', word)
        if len(alpha) > 3 and alpha.isupper():
            violations.append(word)
    return violations
def check_excessive_punctuation(text):
    """Flags repeated punctuation (!!!, ???, ...)."""
    return re.findall(r'[!?\.]{2,}', text)
def check_trademark_mentions(text):
    lowered = text.lower()
    return [term for term in TRADEMARKED_TERMS if re.search(r'\b' + term + r'\b', lowered)]
def check_prohibited_phrases(text):
    lowered = text.lower()
    return [phrase for phrase in PROHIBITED_PHRASES if phrase in lowered]
def check_suspicious_claims(text):
    hits = []
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(pattern)
    return hits
def score_ad(issues):
    """
    Score 0-100. Start at 100, deduct per issue category.
    """
    score = 100
    deductions = {
        "char_over_limit": 20,
        "all_caps": 15,
        "excessive_punctuation": 10,
        "trademark_mention": 25,
        "prohibited_phrase": 15,
        "suspicious_claim": 30,
        "count_too_few": 10,
        "count_too_many": 5,
    }
    for category, items in issues.items():
        if items:
            score -= deductions.get(category, 5) * (1 if isinstance(items, bool) else min(len(items), 3))
    return max(0, score)
