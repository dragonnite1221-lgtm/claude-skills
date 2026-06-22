# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402
from question_bank_generator_p0 import _mod_cg0_0  # noqa: F401,E501
from question_bank_generator_p1 import _mod_cg0_1  # noqa: F401,E501


class QuestionBankGeneratorMixin0:
    """Generates comprehensive interview question banks with scoring criteria."""
    def __init__(self):
        self.technical_questions = self._init_technical_questions()
        self.behavioral_questions = self._init_behavioral_questions()
        self.competency_mapping = self._init_competency_mapping()
        self.scoring_rubrics = self._init_scoring_rubrics()
        self.follow_up_strategies = self._init_follow_up_strategies()
    def _init_technical_questions(self) -> Dict[str, Dict]:
        """Initialize technical questions by competency area and level."""
        return {**_mod_cg0_0(), **_mod_cg0_1()}
    def _init_behavioral_questions(self) -> Dict[str, List[Dict]]:
        """Initialize behavioral questions by competency area."""
        return {
            "leadership": [
                {
                    "question": "Tell me about a time when you had to lead a team through a significant change or challenge.",
                    "competency": "leadership",
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["change_management", "team_motivation", "communication"]
                },
                {
                    "question": "Describe a situation where you had to influence someone without having direct authority over them.",
                    "competency": "leadership", 
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["influence", "persuasion", "stakeholder_management"]
                },
                {
                    "question": "Give me an example of when you had to make a difficult decision that affected your team.",
                    "competency": "leadership",
                    "type": "behavioral", 
                    "method": "STAR",
                    "focus_areas": ["decision_making", "team_impact", "communication"]
                }
            ],
            "collaboration": [
                {
                    "question": "Describe a time when you had to work with a difficult colleague or stakeholder.",
                    "competency": "collaboration",
                    "type": "behavioral",
                    "method": "STAR", 
                    "focus_areas": ["conflict_resolution", "relationship_building", "professionalism"]
                },
                {
                    "question": "Tell me about a project where you had to coordinate across multiple teams or departments.",
                    "competency": "collaboration",
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["cross_functional_work", "communication", "project_coordination"]
                }
            ],
            "problem_solving": [
                {
                    "question": "Walk me through a complex problem you solved recently. What was your approach?",
                    "competency": "problem_solving",
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["analytical_thinking", "methodology", "creativity"]
                },
                {
                    "question": "Describe a time when you had to solve a problem with limited information or resources.",
                    "competency": "problem_solving",
                    "type": "behavioral",
                    "method": "STAR", 
                    "focus_areas": ["resourcefulness", "ambiguity_tolerance", "decision_making"]
                }
            ],
            "communication": [
                {
                    "question": "Tell me about a time when you had to present complex technical information to a non-technical audience.",
                    "competency": "communication",
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["technical_communication", "audience_adaptation", "clarity"]
                },
                {
                    "question": "Describe a situation where you had to deliver difficult feedback to a colleague.",
                    "competency": "communication",
                    "type": "behavioral", 
                    "method": "STAR",
                    "focus_areas": ["feedback_delivery", "empathy", "constructive_criticism"]
                }
            ],
            "adaptability": [
                {
                    "question": "Tell me about a time when you had to quickly learn a new technology or skill for work.",
                    "competency": "adaptability",
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["learning_agility", "growth_mindset", "knowledge_acquisition"]
                },
                {
                    "question": "Describe how you handled a situation when project requirements changed significantly mid-way.",
                    "competency": "adaptability",
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["flexibility", "change_management", "resilience"]
                }
            ],
            "innovation": [
                {
                    "question": "Tell me about a time when you came up with a creative solution to improve a process or solve a problem.",
                    "competency": "innovation", 
                    "type": "behavioral",
                    "method": "STAR",
                    "focus_areas": ["creative_thinking", "process_improvement", "initiative"]
                }
            ]
        }
