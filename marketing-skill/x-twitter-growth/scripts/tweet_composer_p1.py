# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tweet_composer_base import *  # noqa: F403,E402


MAX_TWEET_CHARS = 280
HOOK_PATTERNS = {
    "listicle": [
        "{n} {topic} that changed how I {verb}:",
        "The {n} biggest mistakes in {topic}:",
        "{n} {topic} most people don't know about:",
        "I spent {time} studying {topic}. Here are {n} lessons:",
        "{n} signs your {topic} needs work:",
    ],
    "contrarian": [
        "Unpopular opinion: {claim}",
        "Hot take: {claim}",
        "Everyone says {common_belief}. They're wrong.",
        "Stop {common_action}. Here's what to do instead:",
        "The {topic} advice you keep hearing is backwards.",
    ],
    "story": [
        "I {did_thing} and it completely changed my {outcome}.",
        "Last {timeframe}, I made a mistake with {topic}. Here's what happened:",
        "3 years ago I was {before_state}. Now I'm {after_state}. Here's the playbook:",
        "I almost {near_miss}. Then I discovered {topic}.",
        "The best {topic} advice I ever got came from {unexpected_source}.",
    ],
    "observation": [
        "{topic} is underrated. Here's why:",
        "Nobody talks about this part of {topic}:",
        "The gap between {thing_a} and {thing_b} is where the money is.",
        "If you're struggling with {topic}, you're probably {mistake}.",
        "The secret to {topic} isn't what you think.",
    ],
    "framework": [
        "The {name} framework for {topic} (save this):",
        "How to {outcome} in {timeframe} (step by step):",
        "{topic} explained in 60 seconds:",
        "The only {n} things that matter for {topic}:",
        "A simple system for {topic} that actually works:",
    ],
    "question": [
        "What's the most underrated {topic}?",
        "If you could only {do_one_thing} for {topic}, what would it be?",
        "What {topic} advice would you give your younger self?",
        "Real question: why do most people {common_mistake}?",
        "What's one {topic} that completely changed your perspective?",
    ],
}
THREAD_STRUCTURE = """
Thread Outline: {topic}
{'='*50}

Tweet 1 (HOOK — most important):
  Pattern: {hook_pattern}
  Draft: {hook_draft}
  Chars: {hook_chars}/280

Tweet 2 (CONTEXT):
  Purpose: Set up why this matters
  Suggestion: "Here's what most people get wrong about {topic}:"
  OR: "I spent [time] learning this. Here's the breakdown:"

Tweets 3-{n} (BODY — one idea per tweet):
{body_suggestions}

Tweet {n_plus_1} (CLOSE):
  Purpose: Summarize + CTA
  Suggestion: "TL;DR:\\n\\n[3 bullet summary]\\n\\nFollow @handle for more on {topic}"

Reply to Tweet 1 (ENGAGEMENT BAIT):
  Purpose: Resurface the thread
  Suggestion: "What's your experience with {topic}? Drop it below 👇"
"""
@dataclass
class TweetDraft:
    text: str
    char_count: int
    over_limit: bool
    warnings: list = field(default_factory=list)
def validate_tweet(text: str) -> TweetDraft:
    """Validate a tweet and return analysis."""
    char_count = len(text)
    over_limit = char_count > MAX_TWEET_CHARS
    warnings = []

    if over_limit:
        warnings.append(f"Over limit by {char_count - MAX_TWEET_CHARS} characters")

    # Check for links in body
    import re
    if re.search(r'https?://\S+', text):
        warnings.append("Contains URL — consider moving link to reply (hurts reach)")

    # Check for hashtags
    hashtags = re.findall(r'#\w+', text)
    if len(hashtags) > 2:
        warnings.append(f"Too many hashtags ({len(hashtags)}) — max 1-2, ideally 0")
    elif len(hashtags) > 0:
        warnings.append(f"Has {len(hashtags)} hashtag(s) — consider removing for cleaner look")

    # Check for @mentions at start
    if text.startswith('@'):
        warnings.append("Starts with @ — will be treated as reply, not shown in timeline")

    # Readability
    lines = text.strip().split('\n')
    long_lines = [l for l in lines if len(l) > 70]
    if long_lines:
        warnings.append("Long unbroken lines — add line breaks for mobile readability")

    return TweetDraft(text=text, char_count=char_count, over_limit=over_limit, warnings=warnings)
