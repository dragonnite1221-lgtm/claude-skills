# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from conversion_audit_base import *  # noqa: F403,E402
# fmt: off
from conversion_audit_p1 import CROParser  # noqa: E402,E501
from conversion_audit_p2 import scan_text_signals, score_category  # noqa: E402,E501
# fmt: on


def audit(html: str) -> dict:
    parser = CROParser()
    parser.feed(html)

    full_text = " ".join(parser.full_text)
    text_signals = scan_text_signals(full_text)

    all_ctas = parser.buttons + parser.links_as_cta
    total_cta_count = len(all_ctas) + text_signals["cta_text_count"]

    # --- CTA ---
    cta_score = score_category(total_cta_count, [(0, 0), (1, 50), (2, 75), (3, 90), (5, 100)])
    cta_above_fold = len([c for c in all_ctas if c["position"] <= 5])
    if cta_above_fold >= 1:
        cta_score = min(100, cta_score + 10)

    # --- Forms ---
    if parser.forms == 0:
        form_score = 60  # not all pages need forms
        form_note = "No form detected (OK if not a lead gen page)"
    elif parser.form_fields <= 3:
        form_score = 100
        form_note = f"{parser.form_fields} field(s) — minimal friction"
    elif parser.form_fields <= 5:
        form_score = 70
        form_note = f"{parser.form_fields} field(s) — consider trimming"
    else:
        form_score = max(10, 100 - (parser.form_fields - 3) * 10)
        form_note = f"{parser.form_fields} field(s) — too many, high friction"

    # --- Social proof ---
    social_signals = text_signals["testimonial_signals"] + parser.logo_images
    social_score = score_category(social_signals, [(0, 0), (1, 40), (2, 65), (4, 85), (6, 100)])

    # --- Trust signals ---
    trust = text_signals["trust"]
    trust_total = sum(min(1, v) for v in trust.values())  # 0-3
    trust_score = score_category(trust_total, [(0, 20), (1, 60), (2, 80), (3, 100)])

    # --- Viewport meta ---
    viewport_score = 100 if parser.viewport_meta else 0

    # --- Overall ---
    weights = {
        "cta": 0.30,
        "social_proof": 0.25,
        "trust_signals": 0.20,
        "forms": 0.15,
        "viewport_mobile": 0.10,
    }
    scores = {
        "cta": cta_score,
        "social_proof": social_score,
        "trust_signals": trust_score,
        "forms": form_score,
        "viewport_mobile": viewport_score,
    }
    overall = round(sum(scores[k] * weights[k] for k in weights))

    return {
        "overall_score": overall,
        "categories": {
            "cta_buttons": {
                "score": cta_score,
                "button_count": len(parser.buttons),
                "cta_link_count": len(parser.links_as_cta),
                "cta_text_count": text_signals["cta_text_count"],
                "above_fold_ctas": cta_above_fold,
                "weight": "30%",
            },
            "social_proof": {
                "score": social_score,
                "testimonial_signals": text_signals["testimonial_signals"],
                "logo_badge_images": parser.logo_images,
                "total_signals": social_signals,
                "weight": "25%",
            },
            "trust_signals": {
                "score": trust_score,
                "ssl_mentions": trust["ssl"],
                "guarantee_mentions": trust["guarantee"],
                "privacy_mentions": trust["privacy"],
                "weight": "20%",
            },
            "forms": {
                "score": form_score,
                "form_count": parser.forms,
                "field_count": parser.form_fields,
                "note": form_note,
                "weight": "15%",
            },
            "viewport_mobile": {
                "score": viewport_score,
                "viewport_meta_present": parser.viewport_meta,
                "weight": "10%",
            },
        },
    }
