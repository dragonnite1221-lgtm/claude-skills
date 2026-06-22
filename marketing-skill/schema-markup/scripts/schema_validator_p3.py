# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_validator_base import *  # noqa: F403,E402
# fmt: off
from schema_validator_p2 import grade  # noqa: E402,E501
# fmt: on


def print_report(all_results: List[Dict], html_source: str) -> None:
    print("\n" + "═" * 60)
    print("  SCHEMA MARKUP VALIDATION REPORT")
    print("═" * 60)

    if not all_results:
        print("\n❌ No JSON-LD blocks found in this HTML.")
        print("   Add structured data in <script type=\"application/ld+json\"> tags.\n")
        return

    total_score = 0
    for r in all_results:
        print(f"\n── Block {r['block']} · @type: {r['type']} ──")
        score = r.get("score", 0)
        total_score += score
        print(f"   Score: {score}/100  {grade(score)}")

        if r.get("status") == "parse_error":
            print(f"   ❌ Parse error: {r.get('error')}")
            continue

        if r.get("required_missing"):
            print(f"   Missing required: {', '.join(r['required_missing'])}")
        else:
            print(f"   Required fields: ✅ All present ({', '.join(r.get('required_present', []))})")

        if r.get("recommended_missing"):
            print(f"   Missing recommended: {', '.join(r['recommended_missing'])}")
        if r.get("recommended_present"):
            print(f"   Recommended present: {', '.join(r['recommended_present'])}")

        for note in r.get("notes", []):
            print(f"   {note}")

    avg = total_score // len(all_results) if all_results else 0
    print(f"\n{'═' * 60}")
    print(f"  OVERALL SCORE: {avg}/100  {grade(avg)}")
    print(f"  Blocks analyzed: {len(all_results)}")
    print("═" * 60)

    print("\n📋 TESTING CHECKLIST")
    print("  □ Google Rich Results Test: https://search.google.com/test/rich-results")
    print("  □ Schema.org Validator: https://validator.schema.org")
    print("  □ After deploy: Check Search Console → Enhancements\n")
SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>How to Write Cold Emails That Get Replies</title>

  <!-- Article schema — headline present, but image is relative URL -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "How to Write Cold Emails That Get Replies",
    "image": "/images/cold-email-guide.jpg",
    "datePublished": "2024-03-01",
    "dateModified": "2024-03-15",
    "author": {
      "@type": "Person",
      "name": "Reza Rezvani"
    },
    "publisher": {
      "@type": "Organization",
      "name": "Growth Lab",
      "logo": {
        "@type": "ImageObject",
        "url": "https://growthlab.com/logo.png"
      }
    }
  }
  </script>

  <!-- FAQPage schema — complete and valid -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the ideal length for a cold email?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Keep cold emails under 150 words. Busy professionals scan, not read. If your email needs scrolling, it will not get a reply."
        }
      },
      {
        "@type": "Question",
        "name": "How many follow-ups should I send?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "Send 3-5 follow-ups with increasing gaps (3 days, 5 days, 7 days, 14 days). Each follow-up must add new value — never just check in."
        }
      }
    ]
  }
  </script>

  <!-- BreadcrumbList — position gap (jumps from 1 to 3) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Home",
        "item": "https://growthlab.com"
      },
      {
        "@type": "ListItem",
        "position": 3,
        "name": "How to Write Cold Emails",
        "item": "https://growthlab.com/blog/cold-email-guide"
      }
    ]
  }
  </script>

</head>
<body>
  <h1>How to Write Cold Emails That Get Replies</h1>
  <p>Cold email works when it sounds human...</p>
</body>
</html>
"""
