# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prompt_optimizer_base import *  # noqa: F403,E402
# fmt: off
from prompt_optimizer_p1 import FewShotExample, PromptAnalysis  # noqa: E402,E501
# fmt: on


def extract_sections(text: str) -> List[Dict[str, any]]:
    """Extract logical sections from prompt"""
    sections = []

    # Common section patterns
    section_patterns = [
        r'^#+\s+(.+)$',  # Markdown headers
        r'^([A-Z][A-Za-z\s]+):\s*$',  # Title Case Label:
        r'^(Instructions|Context|Examples?|Input|Output|Task|Role|Format)[:.]',
    ]

    lines = text.split('\n')
    current_section = {'name': 'Introduction', 'start': 1, 'content': []}

    for i, line in enumerate(lines, 1):
        is_header = False
        for pattern in section_patterns:
            match = re.match(pattern, line.strip(), re.IGNORECASE)
            if match:
                if current_section['content']:
                    current_section['end'] = i - 1
                    current_section['line_count'] = len(current_section['content'])
                    sections.append(current_section)
                current_section = {
                    'name': match.group(1).strip() if match.groups() else line.strip(),
                    'start': i,
                    'content': []
                }
                is_header = True
                break

        if not is_header:
            current_section['content'].append(line)

    # Add last section
    if current_section['content']:
        current_section['end'] = len(lines)
        current_section['line_count'] = len(current_section['content'])
        sections.append(current_section)

    return sections
def extract_few_shot_examples(text: str) -> List[FewShotExample]:
    """Extract few-shot examples from prompt"""
    examples = []

    # Pattern 1: "Example N:" or "Example:" blocks
    example_pattern = r'Example\s*\d*:\s*\n(Input:\s*(.+?)\n(?:Output:\s*(.+?)(?=\n\nExample|\n\n[A-Z]|\Z)))'

    matches = re.finditer(example_pattern, text, re.DOTALL | re.IGNORECASE)
    for i, match in enumerate(matches, 1):
        examples.append(FewShotExample(
            input_text=match.group(2).strip() if match.group(2) else '',
            output_text=match.group(3).strip() if match.group(3) else '',
            index=i
        ))

    # Pattern 2: Input/Output pairs without "Example" label
    if not examples:
        io_pattern = r'Input:\s*["\']?(.+?)["\']?\s*\nOutput:\s*(.+?)(?=\nInput:|\Z)'
        matches = re.finditer(io_pattern, text, re.DOTALL)
        for i, match in enumerate(matches, 1):
            examples.append(FewShotExample(
                input_text=match.group(1).strip(),
                output_text=match.group(2).strip(),
                index=i
            ))

    return examples
def calculate_clarity_score(text: str, issues: List[Dict]) -> int:
    """Calculate clarity score (0-100)"""
    score = 100

    # Deduct for issues
    score -= len([i for i in issues if i['type'] == 'ambiguity']) * 5
    score -= len([i for i in issues if i['type'] == 'redundancy']) * 3

    # Check for structure
    if not re.search(r'^#+\s|^[A-Z][a-z]+:', text, re.MULTILINE):
        score -= 10  # No clear sections

    # Check for instruction clarity
    if not re.search(r'(you (should|must|will)|please|your task)', text, re.IGNORECASE):
        score -= 5  # No clear directives

    return max(0, min(100, score))
def calculate_structure_score(sections: List[Dict], has_format: bool, has_examples: bool) -> int:
    """Calculate structure score (0-100)"""
    score = 50  # Base score

    # Bonus for clear sections
    if len(sections) >= 2:
        score += 15
    if len(sections) >= 4:
        score += 10

    # Bonus for output format
    if has_format:
        score += 15

    # Bonus for examples
    if has_examples:
        score += 10

    return min(100, score)
def generate_suggestions(analysis: PromptAnalysis) -> List[str]:
    """Generate optimization suggestions"""
    suggestions = []

    if not analysis.has_output_format:
        suggestions.append('Add explicit output format: "Respond in JSON with keys: ..."')

    if analysis.example_count == 0:
        suggestions.append('Consider adding 2-3 few-shot examples for consistent outputs')
    elif analysis.example_count == 1:
        suggestions.append('Add 1-2 more examples to improve consistency')
    elif analysis.example_count > 5:
        suggestions.append(f'Consider reducing examples from {analysis.example_count} to 3-5 to save tokens')

    if analysis.clarity_score < 70:
        suggestions.append('Improve clarity: replace vague terms with specific instructions')

    if analysis.token_count > 2000:
        suggestions.append(f'Prompt is {analysis.token_count} tokens - consider condensing for cost efficiency')

    # Check for role prompting
    if not re.search(r'you are|act as|as a\s+\w+', analysis.sections[0].get('content', [''])[0] if analysis.sections else '', re.IGNORECASE):
        suggestions.append('Consider adding role context: "You are an expert..."')

    return suggestions
