# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


class QuestionBankGeneratorMixin4:
    def _get_role_competencies(self, role_key: str, level_key: str, 
                              custom_competencies: Optional[List[str]]) -> List[str]:
        """Get competencies for the role and level."""
        if role_key not in self.competency_mapping:
            role_key = "software_engineer"
        
        role_mapping = self.competency_mapping[role_key]
        competencies = role_mapping["core_competencies"].copy()
        
        # Add level-specific competencies
        if level_key in role_mapping["level_specific"]:
            competencies.extend(role_mapping["level_specific"][level_key])
        elif "senior" in role_mapping["level_specific"]:
            competencies.extend(role_mapping["level_specific"]["senior"])
        
        # Add custom competencies if specified
        if custom_competencies:
            competencies.extend([comp.strip() for comp in custom_competencies if comp.strip() not in competencies])
        
        return list(set(competencies))  # Remove duplicates
    def _generate_questions(self, competencies: List[str], question_types: List[str], 
                           level: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate questions based on competencies and types."""
        questions = []
        questions_per_competency = max(1, num_questions // len(competencies))
        
        for competency in competencies:
            competency_questions = []
            
            # Add technical questions if requested and available
            if "technical" in question_types and competency in self.technical_questions:
                tech_questions = []
                
                # Get questions for current level and below
                level_order = ["junior", "mid", "senior", "staff", "principal"]
                current_level_idx = level_order.index(level) if level in level_order else 2
                
                for lvl_idx in range(current_level_idx + 1):
                    lvl = level_order[lvl_idx]
                    if lvl in self.technical_questions[competency]:
                        tech_questions.extend(self.technical_questions[competency][lvl])
                
                competency_questions.extend(tech_questions[:questions_per_competency])
            
            # Add behavioral questions if requested
            if "behavioral" in question_types and competency in self.behavioral_questions:
                behavioral_q = self.behavioral_questions[competency][:questions_per_competency]
                competency_questions.extend(behavioral_q)
            
            # Add situational questions (variations of behavioral)
            if "situational" in question_types:
                situational_q = self._generate_situational_questions(competency, questions_per_competency)
                competency_questions.extend(situational_q)
            
            # Ensure we have enough questions for this competency
            while len(competency_questions) < questions_per_competency:
                competency_questions.extend(self._generate_fallback_questions(competency, level))
                if len(competency_questions) >= questions_per_competency:
                    break
            
            questions.extend(competency_questions[:questions_per_competency])
        
        # Shuffle and limit to requested number
        random.shuffle(questions)
        return questions[:num_questions]
    def _generate_situational_questions(self, competency: str, count: int) -> List[Dict[str, Any]]:
        """Generate situational questions for a competency."""
        situational_templates = {
            "leadership": [
                {
                    "question": "You're leading a project that's behind schedule and the client is unhappy. How do you handle this situation?",
                    "competency": competency,
                    "type": "situational",
                    "focus_areas": ["crisis_management", "client_communication", "team_leadership"]
                }
            ],
            "collaboration": [
                {
                    "question": "You're working on a cross-functional project and two team members have opposing views on the technical approach. How do you resolve this?",
                    "competency": competency, 
                    "type": "situational",
                    "focus_areas": ["conflict_resolution", "technical_decision_making", "facilitation"]
                }
            ],
            "problem_solving": [
                {
                    "question": "You've been assigned to improve the performance of a critical system, but you have limited time and budget. Walk me through your approach.",
                    "competency": competency,
                    "type": "situational", 
                    "focus_areas": ["prioritization", "resource_constraints", "systematic_approach"]
                }
            ]
        }
        
        if competency in situational_templates:
            return situational_templates[competency][:count]
        return []
