# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from format_summary_base import *  # noqa: F403,E402


TEMPLATES = {
    "academic": {
        "name": "Academic Paper Summary",
        "description": "IMRAD structure for peer-reviewed papers and research studies",
        "sections": [
            ("Title", "[Full paper title]"),
            ("Author(s)", "[Author names, affiliations]"),
            ("Publication", "[Journal/Conference, Year, DOI]"),
            ("Source Type", "Academic Paper"),
            ("Key Thesis", "[1-2 sentences: the central research question and answer]"),
            ("Methodology", "[Study design, sample size, data sources, analytical approach]"),
            ("Key Findings", "1. [Finding 1 with supporting data]\n2. [Finding 2 with supporting data]\n3. [Finding 3 with supporting data]"),
            ("Statistical Significance", "[Key p-values, effect sizes, confidence intervals]"),
            ("Limitations", "- [Limitation 1: scope, sample, methodology gap]\n- [Limitation 2]"),
            ("Implications", "- [What this means for practice]\n- [What this means for future research]"),
            ("Notable Quotes", '> "[Direct quote]" (p. X)'),
            ("Quality Assessment", "Credibility: [High/Med/Low] | Evidence: [High/Med/Low] | Recency: [High/Med/Low] | Objectivity: [High/Med/Low]"),
        ],
    },
    "article": {
        "name": "Web Article Summary",
        "description": "Claim-evidence-implication structure for online articles and blog posts",
        "sections": [
            ("Title", "[Article title]"),
            ("Author", "[Author name]"),
            ("Source", "[Publication/Website, Date, URL]"),
            ("Source Type", "Web Article"),
            ("Central Claim", "[1-2 sentences: main argument or thesis]"),
            ("Supporting Evidence", "1. [Evidence point 1]\n2. [Evidence point 2]\n3. [Evidence point 3]"),
            ("Counterarguments Addressed", "- [Counterargument and author's response]"),
            ("Implications", "- [What this means for the reader]"),
            ("Bias Check", "Author affiliation: [?] | Funding: [?] | Balanced perspective: [Yes/No]"),
            ("Actionable Takeaways", "- [What to do with this information]\n- [Next step]"),
            ("Quality Assessment", "Credibility: [High/Med/Low] | Evidence: [High/Med/Low] | Recency: [High/Med/Low] | Objectivity: [High/Med/Low]"),
        ],
    },
    "report": {
        "name": "Technical Report Summary",
        "description": "Structured summary for industry reports, whitepapers, and technical documentation",
        "sections": [
            ("Title", "[Report title]"),
            ("Organization", "[Publishing organization]"),
            ("Date", "[Publication date]"),
            ("Source Type", "Technical Report"),
            ("Executive Summary", "[2-3 sentences: scope, key conclusion, recommendation]"),
            ("Scope", "[What the report covers and what it excludes]"),
            ("Key Data Points", "1. [Statistic or data point with context]\n2. [Statistic or data point with context]\n3. [Statistic or data point with context]"),
            ("Methodology", "[How data was collected — survey, analysis, case study]"),
            ("Recommendations", "1. [Recommendation with supporting rationale]\n2. [Recommendation with supporting rationale]"),
            ("Limitations", "- [Sample bias, geographic scope, time period]"),
            ("Relevance", "[Why this matters for our context — specific applicability]"),
            ("Quality Assessment", "Credibility: [High/Med/Low] | Evidence: [High/Med/Low] | Recency: [High/Med/Low] | Objectivity: [High/Med/Low]"),
        ],
    },
    "executive": {
        "name": "Executive Brief",
        "description": "Condensed decision-focused summary for leadership consumption",
        "sections": [
            ("Source", "[Title, Author, Date]"),
            ("Bottom Line", "[1 sentence: the single most important takeaway]"),
            ("Key Facts", "1. [Fact]\n2. [Fact]\n3. [Fact]"),
            ("So What?", "[Why this matters for our business/product/strategy]"),
            ("Action Required", "- [Specific next step with owner and timeline]"),
            ("Confidence", "[High/Medium/Low] — based on source quality and evidence strength"),
        ],
    },
    "comparison": {
        "name": "Comparative Analysis",
        "description": "Side-by-side comparison matrix for 2-5 sources on the same topic",
        "sections": [
            ("Topic", "[Research topic or question being compared]"),
            ("Sources Compared", "1. [Source A — Author, Year]\n2. [Source B — Author, Year]\n3. [Source C — Author, Year]"),
            ("Comparison Matrix", "| Dimension | Source A | Source B | Source C |\n|-----------|---------|---------|---------|"
             "\n| Central Thesis | ... | ... | ... |"
             "\n| Methodology | ... | ... | ... |"
             "\n| Key Finding | ... | ... | ... |"
             "\n| Sample/Scope | ... | ... | ... |"
             "\n| Credibility | High/Med/Low | High/Med/Low | High/Med/Low |"),
            ("Consensus Findings", "[What most sources agree on]"),
            ("Contested Points", "[Where sources disagree — with strongest evidence for each side]"),
            ("Gaps", "[What none of the sources address]"),
            ("Synthesis", "[Weight-of-evidence recommendation: what to believe and do]"),
        ],
    },
    "literature": {
        "name": "Literature Review",
        "description": "Thematic organization of multiple sources for research synthesis",
        "sections": [
            ("Research Question", "[The question this review addresses]"),
            ("Search Scope", "[Databases, keywords, date range, inclusion/exclusion criteria]"),
            ("Sources Reviewed", "[Total count, breakdown by type]"),
            ("Theme 1: [Name]", "Summary: [Theme overview]\nKey Sources: [Author (Year), Author (Year)]\nFindings: [What sources say about this theme]"),
            ("Theme 2: [Name]", "Summary: [Theme overview]\nKey Sources: [Author (Year), Author (Year)]\nFindings: [What sources say about this theme]"),
            ("Theme 3: [Name]", "Summary: [Theme overview]\nKey Sources: [Author (Year), Author (Year)]\nFindings: [What sources say about this theme]"),
            ("Gaps in Literature", "- [Under-researched area 1]\n- [Under-researched area 2]"),
            ("Synthesis", "[Overall state of knowledge — what we know, what we don't, where to go next]"),
        ],
    },
}
LENGTH_CONFIGS = {
    "brief": {"max_sections": 4, "label": "Brief (key points only)"},
    "standard": {"max_sections": 99, "label": "Standard (full template)"},
    "detailed": {"max_sections": 99, "label": "Detailed (full template with extended guidance)"},
}
