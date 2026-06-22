# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_generator_base import *  # noqa: F403,E402
# fmt: off
from spec_generator_p1 import SPEC_TEMPLATE  # noqa: E402,E501
# fmt: on


def generate_context_prompt(description: str) -> str:
    """Generate a context section prompt based on the provided description."""
    if description:
        return textwrap.dedent(f"""\
            {description}

            _Expand this context section to include:_
            _- Why does this feature exist? What problem does it solve?_
            _- What is the business motivation? (link to user research, support tickets, metrics)_
            _- What is the current state? (what exists today, what pain points exist)_
            _- 2-4 paragraphs maximum._""")
    return textwrap.dedent("""\
        _Why does this feature exist? What problem does it solve? What is the business
        motivation? Include links to user research, support tickets, or metrics that
        justify this work. 2-4 paragraphs maximum._""")
def generate_spec(name: str, description: str) -> str:
    """Generate a spec document from name and description."""
    context_prompt = generate_context_prompt(description)
    return SPEC_TEMPLATE.format(
        name=name,
        date=date.today().isoformat(),
        context_prompt=context_prompt,
    )
def generate_spec_json(name: str, description: str) -> Dict[str, Any]:
    """Generate structured JSON representation of the spec template."""
    return {
        "spec": {
            "title": f"Spec: {name}",
            "metadata": {
                "author": "[your name]",
                "date": date.today().isoformat(),
                "status": "Draft",
                "reviewers": [],
                "related_specs": [],
            },
            "context": description or "[Describe why this feature exists]",
            "functional_requirements": [
                {"id": "FR-1", "keyword": "MUST", "description": "[describe required behavior]"},
                {"id": "FR-2", "keyword": "MUST", "description": "[describe another required behavior]"},
                {"id": "FR-3", "keyword": "SHOULD", "description": "[describe recommended behavior]"},
                {"id": "FR-4", "keyword": "MAY", "description": "[describe optional behavior]"},
                {"id": "FR-5", "keyword": "MUST NOT", "description": "[describe prohibited behavior]"},
            ],
            "non_functional_requirements": {
                "performance": [
                    {"id": "NFR-P1", "description": "[operation] MUST complete in < [threshold]"},
                ],
                "security": [
                    {"id": "NFR-S1", "description": "All data in transit MUST be encrypted via TLS 1.2+"},
                ],
                "accessibility": [
                    {"id": "NFR-A1", "description": "[UI component] MUST meet WCAG 2.1 AA"},
                ],
                "scalability": [
                    {"id": "NFR-SC1", "description": "[system] SHOULD handle [N] concurrent [entities]"},
                ],
                "reliability": [
                    {"id": "NFR-R1", "description": "[service] MUST maintain [N]% uptime"},
                ],
            },
            "acceptance_criteria": [
                {
                    "id": "AC-1",
                    "name": "[descriptive name]",
                    "references": ["FR-1"],
                    "given": "[precondition]",
                    "when": "[action]",
                    "then": "[expected result]",
                },
            ],
            "edge_cases": [
                {"id": "EC-1", "condition": "[input/condition]", "behavior": "[expected behavior]"},
            ],
            "api_contracts": [
                {
                    "method": "[METHOD]",
                    "endpoint": "[/api/path]",
                    "request_fields": [{"name": "field", "type": "string", "constraints": "[description]"}],
                    "success_response": {"status": 200, "fields": []},
                    "error_response": {"status": 400, "fields": []},
                },
            ],
            "data_models": [
                {
                    "name": "[Entity]",
                    "fields": [
                        {"name": "id", "type": "UUID", "constraints": "Primary key, auto-generated"},
                    ],
                },
            ],
            "out_of_scope": [
                {"id": "OS-1", "description": "[feature/capability]", "reason": "[reason]"},
            ],
            "open_questions": [],
        },
        "metadata": {
            "generated_by": "spec_generator.py",
            "feature_name": name,
            "feature_description": description,
        },
    }
