# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


class QuestionBankGeneratorMixin1:
    def _init_competency_mapping(self) -> Dict[str, Dict]:
        """Initialize role to competency mapping."""
        return {
            "software_engineer": {
                "core_competencies": ["coding_fundamentals", "system_design", "problem_solving", "collaboration"],
                "level_specific": {
                    "junior": ["coding_fundamentals", "debugging", "learning_agility"],
                    "mid": ["advanced_coding", "system_design", "mentoring_basics"], 
                    "senior": ["system_architecture", "technical_leadership", "innovation"],
                    "staff": ["architectural_vision", "organizational_impact", "strategic_thinking"]
                }
            },
            "frontend_engineer": {
                "core_competencies": ["frontend_development", "ui_ux_understanding", "problem_solving", "collaboration"],
                "level_specific": {
                    "junior": ["html_css_js", "responsive_design", "basic_frameworks"],
                    "mid": ["react_vue_angular", "state_management", "performance_optimization"],
                    "senior": ["frontend_architecture", "team_leadership", "cross_functional_collaboration"],
                    "staff": ["frontend_strategy", "technology_evaluation", "organizational_impact"]
                }
            },
            "backend_engineer": {
                "core_competencies": ["backend_development", "database_design", "api_design", "system_design"],
                "level_specific": {
                    "junior": ["server_side_programming", "database_basics", "api_consumption"],
                    "mid": ["microservices", "caching", "security_basics"],
                    "senior": ["distributed_systems", "performance_optimization", "technical_leadership"],
                    "staff": ["system_architecture", "technology_strategy", "cross_team_influence"]
                }
            },
            "product_manager": {
                "core_competencies": ["product_strategy", "user_research", "data_analysis", "stakeholder_management"],
                "level_specific": {
                    "junior": ["feature_specification", "user_stories", "basic_analytics"],
                    "mid": ["product_roadmap", "cross_functional_leadership", "market_research"],
                    "senior": ["business_strategy", "team_leadership", "p&l_responsibility"],
                    "staff": ["portfolio_management", "organizational_strategy", "market_creation"]
                }
            },
            "data_scientist": {
                "core_competencies": ["statistical_analysis", "machine_learning", "data_analysis", "business_acumen"],
                "level_specific": {
                    "junior": ["python_r", "sql", "basic_ml", "data_visualization"],
                    "mid": ["advanced_ml", "experiment_design", "model_evaluation"],
                    "senior": ["ml_systems", "data_strategy", "stakeholder_communication"],
                    "staff": ["data_platform", "ai_strategy", "organizational_impact"]
                }
            },
            "designer": {
                "core_competencies": ["design_process", "user_research", "visual_design", "collaboration"],
                "level_specific": {
                    "junior": ["design_tools", "user_empathy", "visual_communication"],
                    "mid": ["design_systems", "user_testing", "cross_functional_work"],
                    "senior": ["design_strategy", "team_leadership", "business_impact"],
                    "staff": ["design_vision", "organizational_design", "strategic_influence"]
                }
            },
            "devops_engineer": {
                "core_competencies": ["infrastructure", "automation", "monitoring", "troubleshooting"],
                "level_specific": {
                    "junior": ["scripting", "basic_cloud", "ci_cd_basics"],
                    "mid": ["infrastructure_as_code", "container_orchestration", "security"],
                    "senior": ["platform_design", "reliability_engineering", "team_leadership"],
                    "staff": ["platform_strategy", "organizational_infrastructure", "technology_vision"]
                }
            }
        }
