# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from content_scorer_base import *  # noqa: F403,E402
# fmt: off
from content_scorer_p1 import score_readability  # noqa: E402,E501
from content_scorer_p2 import score_seo, score_structure  # noqa: E402,E501
# fmt: on


def score_engagement(text: str) -> dict:
    """Score engagement signals 0-25 (25% of total)."""
    points = 0
    signals = {}
    text_lower = text.lower()

    # Questions (engage readers, prompt thought)
    question_count = len(re.findall(r'\?', text))
    signals["question_count"] = question_count
    if question_count >= 3:
        points += 6
    elif question_count >= 1:
        points += 3

    # Specific numbers / data points
    number_count = len(re.findall(r'\b\d+(?:\.\d+)?%?\b', text))
    signals["numbers_and_stats"] = number_count
    if number_count >= 5:
        points += 7
    elif number_count >= 2:
        points += 4
    elif number_count >= 1:
        points += 2

    # Example signals
    example_phrases = ['for example', 'for instance', 'such as', 'like ', 'e.g.', 'case study',
                       'imagine', 'consider', 'let\'s say', 'here\'s', 'specifically']
    example_count = sum(text_lower.count(p) for p in example_phrases)
    signals["example_signals"] = example_count
    if example_count >= 3:
        points += 6
    elif example_count >= 1:
        points += 3

    # Lists (bulleted or numbered)
    list_items = len(re.findall(r'^\s*[-*•]\s+.+|^\s*\d+\.\s+.+', text, re.MULTILINE))
    signals["list_items"] = list_items
    if list_items >= 5:
        points += 6
    elif list_items >= 2:
        points += 3

    total = min(25, points)
    return {"score": total, "max": 25, **signals}
def score_content(text: str, title: str = "", keyword: str = "") -> dict:
    readability = score_readability(text)
    seo = score_seo(text, title, keyword)
    structure = score_structure(text)
    engagement = score_engagement(text)

    total = readability["score"] + seo["score"] + structure["score"] + engagement["score"]

    grade = "D"
    if total >= 90:
        grade = "A+"
    elif total >= 80:
        grade = "A"
    elif total >= 70:
        grade = "B"
    elif total >= 60:
        grade = "C"

    return {
        "total_score": total,
        "grade": grade,
        "sections": {
            "readability": readability,
            "seo": seo,
            "structure": structure,
            "engagement": engagement,
        }
    }
