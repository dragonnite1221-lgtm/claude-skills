# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin2:
    def _init_role_templates(self) -> Dict[str, Dict]:
        """Initialize role-specific interview templates."""
        return {
            "software_engineer": {
                "core_rounds": ["technical_phone_screen", "coding_deep_dive", "system_design", "behavioral"],
                "optional_rounds": ["technical_leadership", "domain_expertise", "culture_fit"],
                "total_duration_range": (180, 360),  # 3-6 hours
                "required_competencies": ["coding", "problem_solving", "communication"]
            },
            "product_manager": {
                "core_rounds": ["product_sense", "analytical_thinking", "execution_process", "behavioral"],
                "optional_rounds": ["strategic_thinking", "technical_collaboration", "leadership"],
                "total_duration_range": (180, 300),  # 3-5 hours
                "required_competencies": ["product_strategy", "analytical_thinking", "stakeholder_management"]
            },
            "designer": {
                "core_rounds": ["portfolio_review", "design_challenge", "collaboration_process", "behavioral"],
                "optional_rounds": ["design_system_thinking", "research_methodology", "leadership"],
                "total_duration_range": (180, 300),  # 3-5 hours
                "required_competencies": ["design_process", "user_empathy", "visual_communication"]
            },
            "data_scientist": {
                "core_rounds": ["technical_assessment", "case_study", "statistical_thinking", "behavioral"],
                "optional_rounds": ["ml_systems", "business_strategy", "technical_leadership"],
                "total_duration_range": (210, 330),  # 3.5-5.5 hours
                "required_competencies": ["statistical_analysis", "programming", "business_acumen"]
            },
            "devops_engineer": {
                "core_rounds": ["technical_assessment", "system_design", "troubleshooting", "behavioral"],
                "optional_rounds": ["security_assessment", "automation_design", "leadership"],
                "total_duration_range": (180, 300),  # 3-5 hours
                "required_competencies": ["infrastructure", "automation", "problem_solving"]
            },
            "engineering_manager": {
                "core_rounds": ["leadership_assessment", "technical_background", "people_management", "behavioral"],
                "optional_rounds": ["strategic_thinking", "hiring_assessment", "culture_building"],
                "total_duration_range": (240, 360),  # 4-6 hours
                "required_competencies": ["people_leadership", "technical_understanding", "strategic_thinking"]
            }
        }
    def _init_interviewer_skills(self) -> Dict[str, Dict]:
        """Initialize interviewer skill requirements for different round types."""
        return {
            "technical_phone_screen": {
                "required_skills": ["technical_assessment", "coding_evaluation"],
                "preferred_experience": ["same_domain", "senior_level"],
                "calibration_level": "standard"
            },
            "coding_deep_dive": {
                "required_skills": ["advanced_technical", "code_quality_assessment"],
                "preferred_experience": ["senior_engineer", "system_design"],
                "calibration_level": "high"
            },
            "system_design": {
                "required_skills": ["architecture_design", "scalability_assessment"],
                "preferred_experience": ["senior_architect", "large_scale_systems"],
                "calibration_level": "high"
            },
            "behavioral": {
                "required_skills": ["behavioral_interviewing", "competency_assessment"],
                "preferred_experience": ["hiring_manager", "people_leadership"],
                "calibration_level": "standard"
            },
            "technical_leadership": {
                "required_skills": ["leadership_assessment", "technical_mentoring"],
                "preferred_experience": ["engineering_manager", "tech_lead"],
                "calibration_level": "high"
            },
            "product_sense": {
                "required_skills": ["product_evaluation", "market_analysis"],
                "preferred_experience": ["product_manager", "product_leadership"],
                "calibration_level": "high"
            },
            "analytical_thinking": {
                "required_skills": ["data_analysis", "metrics_evaluation"],
                "preferred_experience": ["data_analyst", "product_manager"],
                "calibration_level": "standard"
            },
            "design_challenge": {
                "required_skills": ["design_evaluation", "user_experience"],
                "preferred_experience": ["senior_designer", "design_manager"],
                "calibration_level": "high"
            }
        }
