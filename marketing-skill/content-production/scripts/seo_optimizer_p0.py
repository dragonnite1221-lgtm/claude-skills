# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_optimizer_base import *  # noqa: F403,E402


def optimize_content(content: str, keyword: str = None, 
                     secondary_keywords: List[str] = None) -> str:
    """Main function to optimize content"""
    optimizer = SEOOptimizer()
    
    # Parse secondary keywords from comma-separated string if provided
    if secondary_keywords and isinstance(secondary_keywords, str):
        secondary_keywords = [kw.strip() for kw in secondary_keywords.split(',')]
    
    results = optimizer.analyze(content, keyword, secondary_keywords)
    
    # Format output
    output = [
        "=== SEO Content Analysis ===",
        f"Overall SEO Score: {results['optimization_score']}/100",
        f"Content Length: {results['content_length']} words",
        f"",
        "Content Structure:",
        f"  Headings: {results['structure_analysis']['headings']['total']}",
        f"  Paragraphs: {results['structure_analysis']['paragraphs']}",
        f"  Avg Paragraph Length: {results['structure_analysis']['avg_paragraph_length']} words",
        f"  Internal Links: {results['structure_analysis']['links']['internal']}",
        f"  External Links: {results['structure_analysis']['links']['external']}",
        f"",
        f"Readability: {results['readability']['level']} (Score: {results['readability']['score']})",
        f""
    ]
    
    if results['keyword_analysis']:
        kw = results['keyword_analysis']['primary_keyword']
        output.extend([
            "Keyword Analysis:",
            f"  Primary Keyword: {kw['keyword']}",
            f"  Count: {kw['count']}",
            f"  Density: {kw['density']:.2%}",
            f"  In First Paragraph: {'Yes' if kw['in_first_paragraph'] else 'No'}",
            f""
        ])
        
        if results['keyword_analysis']['lsi_keywords']:
            output.append("  Related Keywords Found:")
            for lsi in results['keyword_analysis']['lsi_keywords'][:5]:
                output.append(f"    • {lsi}")
            output.append("")
    
    if results['meta_suggestions']:
        output.extend([
            "Meta Tag Suggestions:",
            f"  Title: {results['meta_suggestions']['title']}",
            f"  Description: {results['meta_suggestions']['meta_description']}",
            f"  URL Slug: {results['meta_suggestions']['url_slug']}",
            f""
        ])
    
    output.extend([
        "Recommendations:",
    ])
    
    for rec in results['recommendations']:
        output.append(f"  • {rec}")
    
    return '\n'.join(output)
