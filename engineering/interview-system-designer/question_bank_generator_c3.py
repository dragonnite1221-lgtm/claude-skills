# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


class QuestionBankGeneratorMixin3:
    def _init_follow_up_strategies(self) -> Dict[str, List[str]]:
        """Initialize follow-up question strategies by competency."""
        return {
            "coding_fundamentals": [
                "How would you optimize this solution for better time complexity?",
                "What edge cases should we consider for this problem?",
                "How would you test this function?",
                "What would happen if the input size was very large?"
            ],
            "system_design": [
                "How would you handle if the system needed to scale 10x?",
                "What would you do if one of your services went down?",
                "How would you monitor this system in production?",
                "What security considerations would you implement?"
            ],
            "leadership": [
                "What would you do differently if you faced this situation again?",
                "How did you handle team members who were resistant to the change?",
                "What metrics did you use to measure success?",
                "How did you communicate progress to stakeholders?"
            ],
            "problem_solving": [
                "Walk me through your thought process step by step",
                "What alternative approaches did you consider?",
                "How did you validate your solution worked?",
                "What did you learn from this experience?"
            ],
            "collaboration": [
                "How did you build consensus among the different stakeholders?",
                "What communication channels did you use to keep everyone aligned?",
                "How did you handle disagreements or conflicts?",
                "What would you do to improve collaboration in the future?"
            ]
        }
    def generate_question_bank(self, role: str, level: str = "senior", 
                              competencies: Optional[List[str]] = None,
                              question_types: Optional[List[str]] = None,
                              num_questions: int = 20) -> Dict[str, Any]:
        """Generate a comprehensive question bank for the specified role and competencies."""
        
        # Normalize inputs
        role_key = self._normalize_role(role)
        level_key = level.lower()
        
        # Get competency requirements
        role_competencies = self._get_role_competencies(role_key, level_key, competencies)
        
        # Determine question types to include
        if question_types is None:
            question_types = ["technical", "behavioral", "situational"]
        
        # Generate questions
        questions = self._generate_questions(role_competencies, question_types, level_key, num_questions)
        
        # Create scoring rubrics
        scoring_rubrics = self._create_scoring_rubrics(questions)
        
        # Generate follow-up probes
        follow_up_probes = self._generate_follow_up_probes(questions)
        
        # Create calibration examples
        calibration_examples = self._create_calibration_examples(questions[:5])  # Sample for first 5 questions
        
        return {
            "role": role,
            "level": level,
            "competencies": role_competencies,
            "question_types": question_types,
            "generated_at": datetime.now().isoformat(),
            "total_questions": len(questions),
            "questions": questions,
            "scoring_rubrics": scoring_rubrics,
            "follow_up_probes": follow_up_probes,
            "calibration_examples": calibration_examples,
            "usage_guidelines": self._generate_usage_guidelines(role_key, level_key)
        }
    def _normalize_role(self, role: str) -> str:
        """Normalize role name to match competency mapping keys."""
        role_lower = role.lower().replace(" ", "_").replace("-", "_")
        
        # Map variations to standard roles
        role_mappings = {
            "software_engineer": ["engineer", "developer", "swe", "software_developer"],
            "frontend_engineer": ["frontend", "front_end", "ui_engineer", "web_developer"],
            "backend_engineer": ["backend", "back_end", "server_engineer", "api_developer"],
            "product_manager": ["pm", "product", "product_owner", "po"],
            "data_scientist": ["ds", "data", "analyst", "ml_engineer"],
            "designer": ["ux", "ui", "ux_ui", "product_designer", "visual_designer"],
            "devops_engineer": ["devops", "sre", "platform_engineer", "infrastructure"]
        }
        
        for standard_role, variations in role_mappings.items():
            if any(var in role_lower for var in variations):
                return standard_role
        
        # Default fallback
        return "software_engineer"
