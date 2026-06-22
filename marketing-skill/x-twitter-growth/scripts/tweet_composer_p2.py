# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from tweet_composer_base import *  # noqa: F403,E402
# fmt: off
from tweet_composer_p1 import HOOK_PATTERNS  # noqa: E402,E501
# fmt: on


def generate_hooks(topic: str, count: int = 10) -> list:
    """Generate hook variations for a topic."""
    hooks = []
    for pattern_type, patterns in HOOK_PATTERNS.items():
        for p in patterns:
            hook = p.replace("{topic}", topic).replace("{n}", "7").replace(
                "{time}", "6 months").replace("{timeframe}", "month").replace(
                "{claim}", f"{topic} is overrated").replace(
                "{common_belief}", f"{topic} is simple").replace(
                "{common_action}", f"overthinking {topic}").replace(
                "{outcome}", "approach").replace("{verb}", "think").replace(
                "{name}", "3-Step").replace("{did_thing}", f"changed my {topic} strategy").replace(
                "{before_state}", "stuck").replace("{after_state}", "thriving").replace(
                "{near_miss}", f"gave up on {topic}").replace(
                "{unexpected_source}", "a complete beginner").replace(
                "{thing_a}", "theory").replace("{thing_b}", "execution").replace(
                "{mistake}", "overcomplicating it").replace(
                "{common_mistake}", f"ignore {topic}").replace(
                "{do_one_thing}", "change one thing").replace(
                "{common_action}", f"overthinking {topic}")
            hooks.append({"type": pattern_type, "hook": hook, "chars": len(hook)})
            if len(hooks) >= count:
                return hooks
    return hooks[:count]
def generate_thread_outline(topic: str, num_tweets: int = 8) -> str:
    """Generate a thread structure outline."""
    hooks = generate_hooks(topic, 3)
    best_hook = hooks[0]["hook"] if hooks else f"Everything I know about {topic}:"

    body = []
    suggestions = [
        "Key insight or surprising fact",
        "Common mistake people make",
        "The counterintuitive truth",
        "A practical example or case study",
        "The framework or system",
        "Implementation steps",
        "Results or evidence",
        "The nuance most people miss",
    ]

    for i, s in enumerate(suggestions[:num_tweets - 3], 3):
        body.append(f"  Tweet {i}: [{s}]")

    body_text = "\n".join(body)

    return f"""
{'='*60}
  THREAD OUTLINE: {topic}
{'='*60}

  Tweet 1 (HOOK):
    "{best_hook}"
    Chars: {len(best_hook)}/280

  Tweet 2 (CONTEXT):
    "Here's what most people get wrong about {topic}:"

{body_text}

  Tweet {num_tweets - 1} (CLOSE):
    "TL;DR:

    • [Key takeaway 1]
    • [Key takeaway 2]
    • [Key takeaway 3]

    Follow for more on {topic}"

  Reply to Tweet 1 (BOOST):
    "What's your biggest challenge with {topic}? 👇"

{'='*60}
  RULES:
  - Each tweet must stand alone (people read out of order)
  - Max 3-4 lines per tweet (mobile readability)
  - No filler tweets — cut anything that doesn't add value
  - Hook tweet determines 90%% of thread performance
{'='*60}
"""
