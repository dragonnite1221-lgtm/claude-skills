# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin1:
    def _init_competency_frameworks(self) -> Dict[str, Dict]:
        """Initialize competency frameworks for different roles."""
        return {
            "software_engineer": {
                "junior": {
                    "required": ["coding_fundamentals", "debugging", "testing_basics", "version_control"],
                    "preferred": ["system_understanding", "code_review", "collaboration"],
                    "focus_areas": ["technical_execution", "learning_agility", "team_collaboration"]
                },
                "mid": {
                    "required": ["advanced_coding", "system_design_basics", "testing_strategy", "debugging_complex"],
                    "preferred": ["mentoring_basics", "technical_communication", "project_ownership"],
                    "focus_areas": ["technical_depth", "system_thinking", "ownership"]
                },
                "senior": {
                    "required": ["system_architecture", "technical_leadership", "mentoring", "cross_team_collab"],
                    "preferred": ["technology_evaluation", "process_improvement", "hiring_contribution"],
                    "focus_areas": ["technical_leadership", "system_architecture", "people_development"]
                },
                "staff": {
                    "required": ["architectural_vision", "organizational_impact", "technical_strategy", "team_building"],
                    "preferred": ["industry_influence", "innovation_leadership", "executive_communication"],
                    "focus_areas": ["organizational_impact", "technical_vision", "strategic_influence"]
                },
                "principal": {
                    "required": ["company_wide_impact", "technical_vision", "talent_development", "strategic_planning"],
                    "preferred": ["industry_leadership", "board_communication", "market_influence"],
                    "focus_areas": ["strategic_leadership", "organizational_transformation", "external_influence"]
                }
            },
            "product_manager": {
                "junior": {
                    "required": ["product_execution", "user_research", "data_analysis", "stakeholder_comm"],
                    "preferred": ["market_awareness", "technical_understanding", "project_management"],
                    "focus_areas": ["execution_excellence", "user_focus", "analytical_thinking"]
                },
                "mid": {
                    "required": ["product_strategy", "cross_functional_leadership", "metrics_design", "market_analysis"],
                    "preferred": ["team_building", "technical_collaboration", "competitive_analysis"],
                    "focus_areas": ["strategic_thinking", "leadership", "business_impact"]
                },
                "senior": {
                    "required": ["business_strategy", "team_leadership", "p&l_ownership", "market_positioning"],
                    "preferred": ["hiring_leadership", "board_communication", "partnership_development"],
                    "focus_areas": ["business_leadership", "market_strategy", "organizational_impact"]
                },
                "staff": {
                    "required": ["portfolio_management", "organizational_leadership", "strategic_planning", "market_creation"],
                    "preferred": ["executive_presence", "investor_relations", "acquisition_strategy"],
                    "focus_areas": ["strategic_leadership", "market_innovation", "organizational_transformation"]
                }
            },
            "designer": {
                "junior": {
                    "required": ["design_fundamentals", "user_research", "prototyping", "design_tools"],
                    "preferred": ["user_empathy", "visual_design", "collaboration"],
                    "focus_areas": ["design_execution", "user_research", "creative_problem_solving"]
                },
                "mid": {
                    "required": ["design_systems", "user_testing", "cross_functional_collab", "design_strategy"],
                    "preferred": ["mentoring", "process_improvement", "business_understanding"],
                    "focus_areas": ["design_leadership", "system_thinking", "business_impact"]
                },
                "senior": {
                    "required": ["design_leadership", "team_building", "strategic_design", "stakeholder_management"],
                    "preferred": ["design_culture", "hiring_leadership", "executive_communication"],
                    "focus_areas": ["design_strategy", "team_leadership", "organizational_impact"]
                }
            },
            "data_scientist": {
                "junior": {
                    "required": ["statistical_analysis", "python_r", "data_visualization", "sql"],
                    "preferred": ["machine_learning", "business_understanding", "communication"],
                    "focus_areas": ["analytical_skills", "technical_execution", "business_impact"]
                },
                "mid": {
                    "required": ["advanced_ml", "experiment_design", "data_engineering", "stakeholder_comm"],
                    "preferred": ["mentoring", "project_leadership", "product_collaboration"],
                    "focus_areas": ["advanced_analytics", "project_leadership", "cross_functional_impact"]
                },
                "senior": {
                    "required": ["data_strategy", "team_leadership", "ml_systems", "business_strategy"],
                    "preferred": ["hiring_leadership", "executive_communication", "technology_evaluation"],
                    "focus_areas": ["strategic_leadership", "technical_vision", "organizational_impact"]
                }
            },
            "devops_engineer": {
                "junior": {
                    "required": ["infrastructure_basics", "scripting", "monitoring", "troubleshooting"],
                    "preferred": ["automation", "cloud_platforms", "security_awareness"],
                    "focus_areas": ["operational_excellence", "automation_mindset", "problem_solving"]
                },
                "mid": {
                    "required": ["ci_cd_design", "infrastructure_as_code", "security_implementation", "performance_optimization"],
                    "preferred": ["team_collaboration", "incident_management", "capacity_planning"],
                    "focus_areas": ["system_reliability", "automation_leadership", "cross_team_collaboration"]
                },
                "senior": {
                    "required": ["platform_architecture", "team_leadership", "security_strategy", "organizational_impact"],
                    "preferred": ["hiring_contribution", "technology_evaluation", "executive_communication"],
                    "focus_areas": ["platform_leadership", "strategic_thinking", "organizational_transformation"]
                }
            },
            "engineering_manager": {
                "junior": {
                    "required": ["team_leadership", "technical_background", "people_management", "project_coordination"],
                    "preferred": ["hiring_experience", "performance_management", "technical_mentoring"],
                    "focus_areas": ["people_leadership", "team_building", "execution_excellence"]
                },
                "senior": {
                    "required": ["organizational_leadership", "strategic_planning", "talent_development", "cross_functional_leadership"],
                    "preferred": ["technical_vision", "culture_building", "executive_communication"],
                    "focus_areas": ["organizational_impact", "strategic_leadership", "talent_development"]
                },
                "staff": {
                    "required": ["multi_team_leadership", "organizational_strategy", "executive_presence", "cultural_transformation"],
                    "preferred": ["board_communication", "market_understanding", "acquisition_integration"],
                    "focus_areas": ["organizational_transformation", "strategic_leadership", "cultural_evolution"]
                }
            }
        }
