# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pir_generator_base import *  # noqa: F403,E402


class PIRGeneratorMixin0:
    """
    Generates comprehensive Post-Incident Review documents with multiple
    RCA frameworks, lessons learned, and actionable follow-up items.
    """
    def __init__(self):
        """Initialize the PIR generator with templates and frameworks."""
        self.rca_frameworks = self._load_rca_frameworks()
        self.pir_templates = self._load_pir_templates()
        self.severity_guidelines = self._load_severity_guidelines()
        self.action_item_types = self._load_action_item_types()
        self.lessons_learned_categories = self._load_lessons_learned_categories()
    def _load_rca_frameworks(self) -> Dict[str, Dict]:
        """Load root cause analysis framework definitions."""
        return {
            "five_whys": {
                "name": "5 Whys Analysis",
                "description": "Iterative questioning technique to explore cause-and-effect relationships",
                "steps": [
                    "State the problem clearly",
                    "Ask why the problem occurred",
                    "For each answer, ask why again",
                    "Continue until root cause is identified",
                    "Verify the root cause addresses the original problem"
                ],
                "min_iterations": 3,
                "max_iterations": 7
            },
            "fishbone": {
                "name": "Fishbone (Ishikawa) Diagram",
                "description": "Systematic analysis across multiple categories of potential causes",
                "categories": [
                    {
                        "name": "People",
                        "description": "Human factors, training, communication, experience",
                        "examples": ["Training gaps", "Communication failures", "Skill deficits", "Staffing issues"]
                    },
                    {
                        "name": "Process",
                        "description": "Procedures, workflows, change management, review processes",
                        "examples": ["Missing procedures", "Inadequate reviews", "Change management gaps", "Documentation issues"]
                    },
                    {
                        "name": "Technology",
                        "description": "Systems, tools, architecture, automation",
                        "examples": ["Architecture limitations", "Tool deficiencies", "Automation gaps", "Infrastructure issues"]
                    },
                    {
                        "name": "Environment",
                        "description": "External factors, dependencies, infrastructure",
                        "examples": ["Third-party dependencies", "Network issues", "Hardware failures", "External service outages"]
                    }
                ]
            },
            "timeline": {
                "name": "Timeline Analysis",
                "description": "Chronological analysis of events to identify decision points and missed opportunities",
                "focus_areas": [
                    "Detection timing and effectiveness",
                    "Response time and escalation paths",
                    "Decision points and alternative paths",
                    "Communication effectiveness",
                    "Mitigation strategy effectiveness"
                ]
            },
            "bow_tie": {
                "name": "Bow Tie Analysis",
                "description": "Analysis of both preventive and protective measures around an incident",
                "components": [
                    "Hazards (what could go wrong)",
                    "Top events (what actually went wrong)",
                    "Threats (what caused it)",
                    "Consequences (what was the impact)",
                    "Barriers (what preventive/protective measures exist or could exist)"
                ]
            }
        }
