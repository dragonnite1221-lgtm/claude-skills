# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from prompt_optimizer_base import *  # noqa: F403,E402


TOKEN_RATIOS = {
    'gpt-4': 4.0,
    'gpt-3.5': 4.0,
    'claude': 3.5,
    'default': 4.0
}
COST_PER_1K = {
    'gpt-4': 0.03,
    'gpt-4-turbo': 0.01,
    'gpt-3.5-turbo': 0.0005,
    'claude-3-opus': 0.015,
    'claude-3-sonnet': 0.003,
    'claude-3-haiku': 0.00025,
    'default': 0.01
}
@dataclass
class PromptAnalysis:
    """Results of prompt analysis"""
    token_count: int
    estimated_cost: float
    model: str
    clarity_score: int
    structure_score: int
    issues: List[Dict[str, str]]
    suggestions: List[str]
    sections: List[Dict[str, any]]
    has_examples: bool
    example_count: int
    has_output_format: bool
    word_count: int
    line_count: int
@dataclass
class FewShotExample:
    """A single few-shot example"""
    input_text: str
    output_text: str
    index: int
def estimate_tokens(text: str, model: str = 'default') -> int:
    """Estimate token count based on character ratio"""
    ratio = TOKEN_RATIOS.get(model, TOKEN_RATIOS['default'])
    return int(len(text) / ratio)
def estimate_cost(token_count: int, model: str = 'default') -> float:
    """Estimate cost based on token count"""
    cost_per_1k = COST_PER_1K.get(model, COST_PER_1K['default'])
    return round((token_count / 1000) * cost_per_1k, 6)
def find_ambiguous_instructions(text: str) -> List[Dict[str, str]]:
    """Find vague or ambiguous instructions"""
    issues = []

    # Vague verbs that need specificity
    vague_patterns = [
        (r'\b(analyze|process|handle|deal with)\b', 'Vague verb - specify the exact action'),
        (r'\b(good|nice|appropriate|suitable)\b', 'Subjective term - define specific criteria'),
        (r'\b(etc\.|and so on|and more)\b', 'Open-ended list - enumerate all items explicitly'),
        (r'\b(if needed|as necessary|when appropriate)\b', 'Conditional without criteria - specify when'),
        (r'\b(some|several|many|few|various)\b', 'Vague quantity - use specific numbers'),
    ]

    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, message in vague_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                issues.append({
                    'type': 'ambiguity',
                    'line': i,
                    'text': match.group(),
                    'message': message,
                    'context': line.strip()[:80]
                })

    return issues
def find_redundant_content(text: str) -> List[Dict[str, str]]:
    """Find potentially redundant content"""
    issues = []
    lines = text.split('\n')

    # Check for repeated phrases (3+ words)
    seen_phrases = {}
    for i, line in enumerate(lines, 1):
        words = line.split()
        for j in range(len(words) - 2):
            phrase = ' '.join(words[j:j+3]).lower()
            phrase = re.sub(r'[^\w\s]', '', phrase)
            if phrase and len(phrase) > 10:
                if phrase in seen_phrases:
                    issues.append({
                        'type': 'redundancy',
                        'line': i,
                        'text': phrase,
                        'message': f'Phrase repeated from line {seen_phrases[phrase]}',
                        'context': line.strip()[:80]
                    })
                else:
                    seen_phrases[phrase] = i

    return issues
def check_output_format(text: str) -> Tuple[bool, List[str]]:
    """Check if prompt specifies output format"""
    suggestions = []

    format_indicators = [
        r'respond\s+(in|with)\s+(json|xml|csv|markdown)',
        r'output\s+format',
        r'return\s+(only|just)',
        r'format:\s*\n',
        r'\{["\']?\w+["\']?\s*:',  # JSON-like structure
        r'```\w*\n',  # Code block
    ]

    has_format = any(re.search(p, text, re.IGNORECASE) for p in format_indicators)

    if not has_format:
        suggestions.append('Add explicit output format specification (e.g., "Respond in JSON with keys: ...")')

    return has_format, suggestions
