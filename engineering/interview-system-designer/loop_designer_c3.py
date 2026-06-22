# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from loop_designer_base import *  # noqa: F403,E402


class InterviewLoopDesignerMixin3:
    def generate_interview_loop(self, role: str, level: str, team: Optional[str] = None, 
                              competencies: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a complete interview loop for the specified role and level."""
        
        # Normalize inputs
        role_key = role.lower().replace(" ", "_").replace("-", "_")
        level_key = level.lower()
        
        # Get role template and competency requirements
        if role_key not in self.competency_frameworks:
            role_key = self._find_closest_role(role_key)
        
        if level_key not in self.competency_frameworks[role_key]:
            level_key = self._find_closest_level(role_key, level_key)
        
        competency_req = self.competency_frameworks[role_key][level_key]
        role_template = self.role_templates.get(role_key, self.role_templates["software_engineer"])
        
        # Design the interview loop
        rounds = self._design_rounds(role_key, level_key, competency_req, role_template, competencies)
        schedule = self._create_schedule(rounds)
        scorecard = self._generate_scorecard(role_key, level_key, competency_req)
        interviewer_requirements = self._define_interviewer_requirements(rounds)
        
        return {
            "role": role,
            "level": level,
            "team": team,
            "generated_at": datetime.now().isoformat(),
            "total_duration_minutes": sum(round_info["duration_minutes"] for round_info in rounds.values()),
            "total_rounds": len(rounds),
            "rounds": rounds,
            "suggested_schedule": schedule,
            "scorecard_template": scorecard,
            "interviewer_requirements": interviewer_requirements,
            "competency_framework": competency_req,
            "calibration_notes": self._generate_calibration_notes(role_key, level_key)
        }
    def _find_closest_role(self, role_key: str) -> str:
        """Find the closest matching role template."""
        role_mappings = {
            "engineer": "software_engineer",
            "developer": "software_engineer",
            "swe": "software_engineer",
            "backend": "software_engineer",
            "frontend": "software_engineer",
            "fullstack": "software_engineer",
            "pm": "product_manager",
            "product": "product_manager",
            "ux": "designer",
            "ui": "designer",
            "graphic": "designer",
            "data": "data_scientist",
            "analyst": "data_scientist",
            "ml": "data_scientist",
            "ops": "devops_engineer",
            "sre": "devops_engineer",
            "infrastructure": "devops_engineer",
            "manager": "engineering_manager",
            "lead": "engineering_manager"
        }
        
        for key_part in role_key.split("_"):
            if key_part in role_mappings:
                return role_mappings[key_part]
        
        return "software_engineer"  # Default fallback
    def _find_closest_level(self, role_key: str, level_key: str) -> str:
        """Find the closest matching level for the role."""
        available_levels = list(self.competency_frameworks[role_key].keys())
        
        level_mappings = {
            "entry": "junior",
            "associate": "junior", 
            "jr": "junior",
            "mid": "mid",
            "middle": "mid",
            "sr": "senior",
            "senior": "senior",
            "staff": "staff",
            "principal": "principal",
            "lead": "senior",
            "manager": "senior"
        }
        
        mapped_level = level_mappings.get(level_key, level_key)
        
        if mapped_level in available_levels:
            return mapped_level
        elif "senior" in available_levels:
            return "senior"
        else:
            return available_levels[0]
