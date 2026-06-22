# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin7:
    def _generate_scorecard(self, role_key: str, level_key: str, competency_req: Dict) -> Dict[str, Any]:
        """Generate a scorecard template for the interview loop."""
        scoring_dimensions = []
        
        # Add competency-based scoring dimensions
        for competency in competency_req["required"]:
            scoring_dimensions.append({
                "dimension": competency,
                "weight": "high",
                "scale": "1-4",
                "description": f"Assessment of {competency.replace('_', ' ')} competency"
            })
        
        for competency in competency_req.get("preferred", []):
            scoring_dimensions.append({
                "dimension": competency,
                "weight": "medium",
                "scale": "1-4", 
                "description": f"Assessment of {competency.replace('_', ' ')} competency"
            })
        
        # Add standard dimensions
        standard_dimensions = [
            {"dimension": "communication", "weight": "high", "scale": "1-4"},
            {"dimension": "cultural_fit", "weight": "medium", "scale": "1-4"},
            {"dimension": "learning_agility", "weight": "medium", "scale": "1-4"}
        ]
        
        scoring_dimensions.extend(standard_dimensions)
        
        return {
            "scoring_scale": {
                "4": "Exceeds Expectations - Demonstrates mastery beyond required level",
                "3": "Meets Expectations - Solid performance meeting all requirements", 
                "2": "Partially Meets - Shows potential but has development areas",
                "1": "Does Not Meet - Significant gaps in required competencies"
            },
            "dimensions": scoring_dimensions,
            "overall_recommendation": {
                "options": ["Strong Hire", "Hire", "No Hire", "Strong No Hire"],
                "criteria": "Based on weighted average and minimum thresholds"
            },
            "calibration_notes": {
                "required": True,
                "min_length": 100,
                "sections": ["strengths", "areas_for_development", "specific_examples"]
            }
        }
    def _define_interviewer_requirements(self, rounds: Dict[str, Dict]) -> Dict[str, Dict]:
        """Define interviewer skill requirements for each round."""
        requirements = {}
        
        for round_name, round_info in rounds.items():
            round_type = round_name.split("_", 2)[-1]  # Extract round type
            
            if round_type in self.interviewer_skills:
                skill_req = self.interviewer_skills[round_type].copy()
                skill_req["suggested_interviewers"] = self._suggest_interviewer_profiles(round_type)
                requirements[round_name] = skill_req
            else:
                # Default requirements
                requirements[round_name] = {
                    "required_skills": ["interviewing_basics", "evaluation_skills"],
                    "preferred_experience": ["relevant_domain"],
                    "calibration_level": "standard",
                    "suggested_interviewers": ["experienced_interviewer"]
                }
        
        return requirements
    def _suggest_interviewer_profiles(self, round_type: str) -> List[str]:
        """Suggest specific interviewer profiles for different round types."""
        profile_mapping = {
            "technical_phone_screen": ["senior_engineer", "tech_lead"],
            "coding_deep_dive": ["senior_engineer", "staff_engineer"],
            "system_design": ["senior_architect", "staff_engineer"],
            "behavioral": ["hiring_manager", "people_manager"],
            "technical_leadership": ["engineering_manager", "senior_staff"],
            "product_sense": ["senior_pm", "product_leader"],
            "analytical_thinking": ["senior_analyst", "data_scientist"],
            "design_challenge": ["senior_designer", "design_manager"]
        }
        
        return profile_mapping.get(round_type, ["experienced_interviewer"])
    def _generate_calibration_notes(self, role_key: str, level_key: str) -> Dict[str, Any]:
        """Generate calibration notes and best practices."""
        return {
            "hiring_bar_notes": f"Calibrated for {level_key} level {role_key.replace('_', ' ')} role",
            "common_pitfalls": [
                "Avoid comparing candidates to each other rather than to the role standard",
                "Don't let one strong/weak area overshadow overall assessment",
                "Ensure consistent application of evaluation criteria"
            ],
            "calibration_checkpoints": [
                "Review score distribution after every 5 candidates",
                "Conduct monthly interviewer calibration sessions",
                "Track correlation with 6-month performance reviews"
            ],
            "escalation_criteria": [
                "Any candidate receiving all 4s or all 1s",
                "Significant disagreement between interviewers (>1.5 point spread)",
                "Unusual circumstances or accommodations needed"
            ]
        }
