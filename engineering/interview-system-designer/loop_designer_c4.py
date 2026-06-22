# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin4:
    def _design_rounds(self, role_key: str, level_key: str, competency_req: Dict, 
                      role_template: Dict, custom_competencies: Optional[List[str]]) -> Dict[str, Dict]:
        """Design the specific interview rounds based on role and level."""
        rounds = {}
        
        # Determine which rounds to include
        core_rounds = role_template["core_rounds"].copy()
        optional_rounds = role_template["optional_rounds"].copy()
        
        # Add optional rounds based on level
        if level_key in ["senior", "staff", "principal"]:
            if "technical_leadership" in optional_rounds and role_key in ["software_engineer", "engineering_manager"]:
                core_rounds.append("technical_leadership")
            if "strategic_thinking" in optional_rounds and role_key in ["product_manager", "engineering_manager"]:
                core_rounds.append("strategic_thinking")
            if "design_system_thinking" in optional_rounds and role_key == "designer":
                core_rounds.append("design_system_thinking")
        
        if level_key in ["staff", "principal"]:
            if "domain_expertise" in optional_rounds:
                core_rounds.append("domain_expertise")
        
        # Define round details
        round_definitions = self._get_round_definitions()
        
        for i, round_type in enumerate(core_rounds, 1):
            if round_type in round_definitions:
                round_def = round_definitions[round_type].copy()
                round_def["order"] = i
                round_def["focus_areas"] = self._customize_focus_areas(round_type, competency_req, custom_competencies)
                rounds[f"round_{i}_{round_type}"] = round_def
        
        return rounds
    def _get_round_definitions(self) -> Dict[str, Dict]:
        """Get predefined round definitions with standard durations and formats."""
        return {
            "technical_phone_screen": {
                "name": "Technical Phone Screen",
                "duration_minutes": 45,
                "format": "virtual",
                "objectives": ["Assess coding fundamentals", "Evaluate problem-solving approach", "Screen for basic technical competency"],
                "question_types": ["coding_problems", "technical_concepts", "experience_questions"],
                "evaluation_criteria": ["technical_accuracy", "problem_solving_process", "communication_clarity"]
            },
            "coding_deep_dive": {
                "name": "Coding Deep Dive",
                "duration_minutes": 75,
                "format": "in_person_or_virtual",
                "objectives": ["Evaluate coding skills in depth", "Assess code quality and testing", "Review debugging approach"],
                "question_types": ["complex_coding_problems", "code_review", "testing_strategy"],
                "evaluation_criteria": ["code_quality", "testing_approach", "debugging_skills", "optimization_thinking"]
            },
            "system_design": {
                "name": "System Design",
                "duration_minutes": 75,
                "format": "collaborative_whiteboard",
                "objectives": ["Assess architectural thinking", "Evaluate scalability considerations", "Review trade-off analysis"],
                "question_types": ["system_architecture", "scalability_design", "trade_off_analysis"],
                "evaluation_criteria": ["architectural_thinking", "scalability_awareness", "trade_off_reasoning"]
            },
            "behavioral": {
                "name": "Behavioral Interview",
                "duration_minutes": 45,
                "format": "conversational",
                "objectives": ["Assess cultural fit", "Evaluate past experiences", "Review leadership examples"],
                "question_types": ["star_method_questions", "situational_scenarios", "values_alignment"],
                "evaluation_criteria": ["communication_skills", "leadership_examples", "cultural_alignment"]
            },
            "technical_leadership": {
                "name": "Technical Leadership",
                "duration_minutes": 60,
                "format": "discussion_based",
                "objectives": ["Evaluate mentoring capability", "Assess technical decision making", "Review cross-team collaboration"],
                "question_types": ["leadership_scenarios", "technical_decisions", "mentoring_examples"],
                "evaluation_criteria": ["leadership_potential", "technical_judgment", "influence_skills"]
            },
            "product_sense": {
                "name": "Product Sense",
                "duration_minutes": 75,
                "format": "case_study",
                "objectives": ["Assess product intuition", "Evaluate user empathy", "Review market understanding"],
                "question_types": ["product_scenarios", "feature_prioritization", "user_journey_analysis"],
                "evaluation_criteria": ["product_intuition", "user_empathy", "analytical_thinking"]
            },
            "analytical_thinking": {
                "name": "Analytical Thinking",
                "duration_minutes": 60,
                "format": "data_analysis",
                "objectives": ["Evaluate data interpretation", "Assess metric design", "Review experiment planning"],
                "question_types": ["data_interpretation", "metric_design", "experiment_analysis"],
                "evaluation_criteria": ["analytical_rigor", "metric_intuition", "experimental_thinking"]
            },
            "design_challenge": {
                "name": "Design Challenge",
                "duration_minutes": 90,
                "format": "hands_on_design",
                "objectives": ["Assess design process", "Evaluate user-centered thinking", "Review iteration approach"],
                "question_types": ["design_problems", "user_research", "design_critique"],
                "evaluation_criteria": ["design_process", "user_focus", "visual_communication"]
            },
            "portfolio_review": {
                "name": "Portfolio Review",
                "duration_minutes": 75,
                "format": "presentation_discussion",
                "objectives": ["Review past work", "Assess design thinking", "Evaluate impact measurement"],
                "question_types": ["portfolio_walkthrough", "design_decisions", "impact_stories"],
                "evaluation_criteria": ["design_quality", "process_thinking", "business_impact"]
            }
        }
