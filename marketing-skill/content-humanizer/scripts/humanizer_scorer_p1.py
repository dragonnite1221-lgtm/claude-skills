# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from humanizer_scorer_base import *  # noqa: F403,E402


SAMPLE_HUMAN = """
We tried to fix our churn problem the wrong way for about a year. 

We threw money at marketing, assumed acquisition would outpace loss, and avoided looking at the actual numbers. It didn't work. Churn stayed flat at 8% monthly, which sounds manageable until you realize that's 65% annual churn. We were filling a leaky bucket with a garden hose.

The breakthrough — if you can call it that — was embarrassingly simple: we actually talked to the customers who left.

Not the ones who complained. The ones who quietly disappeared. We called 30 churned accounts over two weeks. You know what most of them said? They didn't hate the product. They just... forgot about it. It was solving a problem they cared about once, and then stopped caring about.

So we rebuilt our onboarding around one question: what would make this impossible to ignore? Not "valuable" — people know it's valuable. Impossible to ignore.

Three months later, 30-day activation was up 40%. Churn dropped to 4.5%.

The lesson wasn't about product or pricing. It was about habit formation. And we were terrible at it.
"""
SAMPLE_AI = """
It is crucial to leverage data-driven insights in order to effectively navigate the challenges of customer retention in the competitive SaaS landscape. Furthermore, by implementing robust onboarding strategies, organizations can ensure that users achieve maximum value from the product, thereby significantly reducing churn rates.

To facilitate this process, it's important to note that companies should delve into their customer behavior data to identify patterns and trends. Moreover, by fostering meaningful connections with customers and ensuring comprehensive support throughout their journey, businesses can cultivate lasting relationships that drive long-term success.

In conclusion, the implementation of these holistic strategies will empower organizations to streamline their customer success operations and achieve sustainable growth in an increasingly competitive marketplace.
"""
AI_VOCABULARY = [
    # The notorious list
    "delve", "delve into", "delves", "delving",
    "landscape",
    "crucial", "vital", "pivotal",
    "leverage", "leveraging", "leveraged",
    "robust",
    "comprehensive",
    "holistic",
    "foster", "fosters", "fostering",
    "facilitate", "facilitates", "facilitating",
    "navigate", "navigating",
    "ensure", "ensures", "ensuring",
    "utilize", "utilizing", "utilizes",
    "furthermore", "moreover",
    "innovative", "cutting-edge",
    "seamless", "seamlessly",
    "empower", "empowers", "empowering",
    "streamline", "streamlines", "streamlining",
    "cultivate", "cultivating",
    "paradigm",
    "ecosystem",
    "synergy",
    "in conclusion",
    "in summary",
    "to summarize",
]
HEDGING_PHRASES = [
    "it is important to note",
    "it's important to note",
    "it should be noted",
    "it is worth mentioning",
    "it's worth mentioning",
    "it goes without saying",
    "needless to say",
    "in many cases",
    "in most cases",
    "in certain cases",
    "in most instances",
    "in many instances",
    "generally speaking",
    "for the most part",
    "this may vary",
    "results may differ",
    "one might argue",
    "it can be argued",
    "there are various",
    "there are many",
    "it is crucial to",
    "it's crucial to",
]
PASSIVE_PATTERNS = [
    r'\b(is|are|was|were|be|been|being)\s+(being\s+)?\w+ed\b',
    r'\b(can|could|should|would|may|might|must)\s+be\s+\w+ed\b',
]
VAGUE_AUTHORITY = [
    "studies show",
    "research suggests",
    "research shows",
    "experts agree",
    "experts say",
    "many companies",
    "leading brands",
    "it has been shown",
    "according to research",
    "data suggests",
    "evidence suggests",
]
def score_ai_vocabulary(text: str) -> dict:
    """Score 0-25: fewer AI words = higher score."""
    text_lower = text.lower()
    words_total = max(1, len(re.findall(r'\b\w+\b', text)))

    hits = []
    for phrase in AI_VOCABULARY:
        count = text_lower.count(phrase)
        if count > 0:
            hits.append((phrase, count))

    total_hits = sum(c for _, c in hits)
    density = total_hits / (words_total / 100)  # per 100 words

    # Score: 0 hits = 25, scales down
    if total_hits == 0:
        score = 25
    elif total_hits <= 2:
        score = 20
    elif total_hits <= 5:
        score = 14
    elif total_hits <= 10:
        score = 8
    elif total_hits <= 15:
        score = 3
    else:
        score = 0

    return {
        "score": score,
        "max": 25,
        "ai_word_hits": total_hits,
        "density_per_100_words": round(density, 2),
        "flagged_terms": [f for f, _ in hits[:10]],  # top 10 for display
    }
