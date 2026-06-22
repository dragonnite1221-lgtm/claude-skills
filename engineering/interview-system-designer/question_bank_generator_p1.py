# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


def _mod_cg0_1():
    return {
        "frontend_development": {
                "junior": [
                    {
                        "question": "Create a responsive navigation menu using HTML, CSS, and vanilla JavaScript.",
                        "competency": "frontend_development",
                        "type": "coding",
                        "difficulty": "easy",
                        "time_limit": 30,
                        "key_concepts": ["html_css", "responsive_design", "dom_manipulation"]
                    }
                ],
                "mid": [
                    {
                        "question": "Build a React component that fetches and displays paginated data from an API.",
                        "competency": "frontend_development",
                        "type": "coding",
                        "difficulty": "medium",
                        "time_limit": 45,
                        "key_concepts": ["react_hooks", "api_integration", "state_management", "pagination"]
                    }
                ],
                "senior": [
                    {
                        "question": "Design and implement a custom React hook for managing complex form state with validation.",
                        "competency": "frontend_development",
                        "type": "coding",
                        "difficulty": "hard",
                        "time_limit": 60,
                        "key_concepts": ["custom_hooks", "form_validation", "state_management", "performance"]
                    }
                ]
            },
        "data_analysis": {
                "junior": [
                    {
                        "question": "Given a dataset of user activities, calculate the daily active users for the past month.",
                        "competency": "data_analysis",
                        "type": "analytical",
                        "difficulty": "easy",
                        "time_limit": 30,
                        "key_concepts": ["sql_basics", "date_functions", "aggregation"]
                    }
                ],
                "mid": [
                    {
                        "question": "Analyze conversion funnel data to identify the biggest drop-off point and propose solutions.",
                        "competency": "data_analysis", 
                        "type": "analytical",
                        "difficulty": "medium",
                        "time_limit": 45,
                        "key_concepts": ["funnel_analysis", "conversion_optimization", "statistical_significance"]
                    }
                ],
                "senior": [
                    {
                        "question": "Design an A/B testing framework to measure the impact of a new recommendation algorithm.",
                        "competency": "data_analysis",
                        "type": "analytical",
                        "difficulty": "hard", 
                        "time_limit": 60,
                        "key_concepts": ["experiment_design", "statistical_power", "bias_mitigation", "causal_inference"]
                    }
                ]
            },
        "machine_learning": {
                "mid": [
                    {
                        "question": "Explain how you would build a recommendation system for an e-commerce platform.",
                        "competency": "machine_learning",
                        "type": "conceptual",
                        "difficulty": "medium",
                        "time_limit": 45,
                        "key_concepts": ["collaborative_filtering", "content_based", "cold_start", "evaluation_metrics"]
                    }
                ],
                "senior": [
                    {
                        "question": "Design a real-time fraud detection system for financial transactions.",
                        "competency": "machine_learning",
                        "type": "design",
                        "difficulty": "hard",
                        "time_limit": 60,
                        "key_concepts": ["anomaly_detection", "real_time_ml", "feature_engineering", "model_monitoring"]
                    }
                ]
            },
        "product_strategy": {
                "mid": [
                    {
                        "question": "How would you prioritize features for a mobile app with limited engineering resources?",
                        "competency": "product_strategy",
                        "type": "case_study",
                        "difficulty": "medium",
                        "time_limit": 45,
                        "key_concepts": ["prioritization_frameworks", "resource_allocation", "impact_estimation"]
                    }
                ],
                "senior": [
                    {
                        "question": "Design a go-to-market strategy for a new B2B SaaS product entering a competitive market.",
                        "competency": "product_strategy",
                        "type": "strategic",
                        "difficulty": "hard",
                        "time_limit": 60,
                        "key_concepts": ["market_analysis", "competitive_positioning", "pricing_strategy", "channel_strategy"]
                    }
                ]
            },
    }
