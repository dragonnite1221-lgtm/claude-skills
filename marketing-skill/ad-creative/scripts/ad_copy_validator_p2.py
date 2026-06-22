# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from ad_copy_validator_base import *  # noqa: F403,E402
# fmt: off
from ad_copy_validator_p1 import PLATFORM_SPECS, check_all_caps, check_excessive_punctuation, check_prohibited_phrases, check_suspicious_claims, check_trademark_mentions, count_chars  # noqa: E402,E501
# fmt: on


def validate_google_rsa(ad):
    spec = PLATFORM_SPECS["google_rsa"]
    issues = defaultdict(list)
    report = []

    headlines = ad.get("headlines", [])
    descriptions = ad.get("descriptions", [])

    # Count checks
    if len(headlines) < spec["headline_count_min"]:
        issues["count_too_few"].append(f"Need ≥{spec['headline_count_min']} headlines, got {len(headlines)}")
    if len(headlines) > spec["headline_count_max"]:
        issues["count_too_many"].append(f"Max {spec['headline_count_max']} headlines, got {len(headlines)}")
    if len(descriptions) < spec["description_count_min"]:
        issues["count_too_few"].append(f"Need ≥{spec['description_count_min']} descriptions, got {len(descriptions)}")

    # Character checks per headline
    for i, h in enumerate(headlines):
        length = count_chars(h)
        status = "✅" if length <= spec["headline_max"] else "❌"
        if length > spec["headline_max"]:
            issues["char_over_limit"].append(f"Headline {i+1}: {length} chars (max {spec['headline_max']})")
        report.append(f"  Headline {i+1}: {status} '{h}' ({length}/{spec['headline_max']} chars)")

        # Rejection trigger checks on each headline
        caps = check_all_caps(h)
        if caps:
            issues["all_caps"].extend(caps)
        punct = check_excessive_punctuation(h)
        if punct:
            issues["excessive_punctuation"].extend(punct)
        trademarks = check_trademark_mentions(h)
        if trademarks:
            issues["trademark_mention"].extend(trademarks)
        prohibited = check_prohibited_phrases(h)
        if prohibited:
            issues["prohibited_phrase"].extend(prohibited)

    for i, d in enumerate(descriptions):
        length = count_chars(d)
        status = "✅" if length <= spec["description_max"] else "❌"
        if length > spec["description_max"]:
            issues["char_over_limit"].append(f"Description {i+1}: {length} chars (max {spec['description_max']})")
        report.append(f"  Description {i+1}: {status} '{d}' ({length}/{spec['description_max']} chars)")

        suspicious = check_suspicious_claims(d)
        if suspicious:
            issues["suspicious_claim"].extend(suspicious)

    return report, dict(issues)
def validate_meta_feed(ad):
    spec = PLATFORM_SPECS["meta_feed"]
    issues = defaultdict(list)
    report = []

    primary = ad.get("primary_text", "")
    headline = ad.get("headline", "")

    if primary:
        length = count_chars(primary)
        status = "✅" if length <= spec["primary_text_max"] else "⚠️ (preview truncated)"
        report.append(f"  Primary text: {status} ({length}/{spec['primary_text_max']} preview chars)")
        if length > spec["primary_text_max"]:
            issues["char_over_limit"].append(f"Primary text {length} chars exceeds {spec['primary_text_max']}-char preview")

        for check_fn, key in [
            (check_all_caps, "all_caps"),
            (check_excessive_punctuation, "excessive_punctuation"),
            (check_trademark_mentions, "trademark_mention"),
            (check_prohibited_phrases, "prohibited_phrase"),
            (check_suspicious_claims, "suspicious_claim"),
        ]:
            result = check_fn(primary)
            if result:
                issues[key].extend(result if isinstance(result, list) else [str(result)])

    if headline:
        length = count_chars(headline)
        status = "✅" if length <= spec["headline_max"] else "❌"
        if length > spec["headline_max"]:
            issues["char_over_limit"].append(f"Headline {length} chars (max {spec['headline_max']})")
        report.append(f"  Headline: {status} '{headline}' ({length}/{spec['headline_max']} chars)")

    return report, dict(issues)
def validate_linkedin(ad):
    spec = PLATFORM_SPECS["linkedin"]
    issues = defaultdict(list)
    report = []

    intro = ad.get("intro_text", ad.get("primary_text", ""))
    headline = ad.get("headline", "")

    if intro:
        length = count_chars(intro)
        status = "✅" if length <= spec["intro_text_max"] else "⚠️ (preview truncated)"
        report.append(f"  Intro text: {status} ({length}/{spec['intro_text_max']} preview chars)")
        if length > spec["intro_text_max"]:
            issues["char_over_limit"].append(f"Intro text {length} chars exceeds {spec['intro_text_max']}-char preview")

        for check_fn, key in [
            (check_all_caps, "all_caps"),
            (check_excessive_punctuation, "excessive_punctuation"),
            (check_trademark_mentions, "trademark_mention"),
        ]:
            result = check_fn(intro)
            if result:
                issues[key].extend(result if isinstance(result, list) else [str(result)])

    if headline:
        length = count_chars(headline)
        status = "✅" if length <= spec["headline_max"] else "❌"
        if length > spec["headline_max"]:
            issues["char_over_limit"].append(f"Headline {length} chars (max {spec['headline_max']})")
        report.append(f"  Headline: {status} '{headline}' ({length}/{spec['headline_max']} chars)")

    return report, dict(issues)
