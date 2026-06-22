# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prompt_optimizer_base import *  # noqa: F403,E402
# fmt: off
from prompt_optimizer_p1 import PromptAnalysis, check_output_format, estimate_cost, estimate_tokens, find_ambiguous_instructions, find_redundant_content  # noqa: E402,E501
from prompt_optimizer_p2 import calculate_clarity_score, calculate_structure_score, extract_few_shot_examples, extract_sections, generate_suggestions  # noqa: E402,E501
# fmt: on


def analyze_prompt(text: str, model: str = 'gpt-4') -> PromptAnalysis:
    """Perform comprehensive prompt analysis"""

    # Basic metrics
    token_count = estimate_tokens(text, model)
    cost = estimate_cost(token_count, model)
    word_count = len(text.split())
    line_count = len(text.split('\n'))

    # Find issues
    ambiguity_issues = find_ambiguous_instructions(text)
    redundancy_issues = find_redundant_content(text)
    all_issues = ambiguity_issues + redundancy_issues

    # Extract structure
    sections = extract_sections(text)
    examples = extract_few_shot_examples(text)
    has_format, format_suggestions = check_output_format(text)

    # Calculate scores
    clarity_score = calculate_clarity_score(text, all_issues)
    structure_score = calculate_structure_score(sections, has_format, len(examples) > 0)

    analysis = PromptAnalysis(
        token_count=token_count,
        estimated_cost=cost,
        model=model,
        clarity_score=clarity_score,
        structure_score=structure_score,
        issues=all_issues,
        suggestions=[],
        sections=[{'name': s['name'], 'lines': f"{s['start']}-{s.get('end', s['start'])}"} for s in sections],
        has_examples=len(examples) > 0,
        example_count=len(examples),
        has_output_format=has_format,
        word_count=word_count,
        line_count=line_count
    )

    analysis.suggestions = generate_suggestions(analysis) + format_suggestions

    return analysis
def optimize_prompt(text: str) -> str:
    """Generate optimized version of prompt"""
    optimized = text

    # Remove redundant whitespace
    optimized = re.sub(r'\n{3,}', '\n\n', optimized)
    optimized = re.sub(r' {2,}', ' ', optimized)

    # Trim lines
    lines = [line.rstrip() for line in optimized.split('\n')]
    optimized = '\n'.join(lines)

    return optimized.strip()
def format_report(analysis: PromptAnalysis) -> str:
    """Format analysis as human-readable report"""
    report = []
    report.append("=" * 50)
    report.append("PROMPT ANALYSIS REPORT")
    report.append("=" * 50)
    report.append("")

    report.append("📊 METRICS")
    report.append(f"  Token count:     {analysis.token_count:,}")
    report.append(f"  Estimated cost:  ${analysis.estimated_cost:.4f} ({analysis.model})")
    report.append(f"  Word count:      {analysis.word_count:,}")
    report.append(f"  Line count:      {analysis.line_count}")
    report.append("")

    report.append("📈 SCORES")
    report.append(f"  Clarity:    {analysis.clarity_score}/100 {'✅' if analysis.clarity_score >= 70 else '⚠️'}")
    report.append(f"  Structure:  {analysis.structure_score}/100 {'✅' if analysis.structure_score >= 70 else '⚠️'}")
    report.append("")

    report.append("📋 STRUCTURE")
    report.append(f"  Sections:      {len(analysis.sections)}")
    report.append(f"  Examples:      {analysis.example_count} {'✅' if analysis.has_examples else '❌'}")
    report.append(f"  Output format: {'✅ Specified' if analysis.has_output_format else '❌ Missing'}")
    report.append("")

    if analysis.sections:
        report.append("  Detected sections:")
        for section in analysis.sections:
            report.append(f"    - {section['name']} (lines {section['lines']})")
        report.append("")

    if analysis.issues:
        report.append(f"⚠️ ISSUES FOUND ({len(analysis.issues)})")
        for issue in analysis.issues[:10]:  # Limit to first 10
            report.append(f"  Line {issue['line']}: {issue['message']}")
            report.append(f"    Found: \"{issue['text']}\"")
        if len(analysis.issues) > 10:
            report.append(f"  ... and {len(analysis.issues) - 10} more issues")
        report.append("")

    if analysis.suggestions:
        report.append("💡 SUGGESTIONS")
        for i, suggestion in enumerate(analysis.suggestions, 1):
            report.append(f"  {i}. {suggestion}")
        report.append("")

    report.append("=" * 50)

    return '\n'.join(report)
