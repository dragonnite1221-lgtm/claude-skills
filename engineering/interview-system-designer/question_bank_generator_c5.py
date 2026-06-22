# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


class QuestionBankGeneratorMixin5:
    def _generate_fallback_questions(self, competency: str, level: str) -> List[Dict[str, Any]]:
        """Generate fallback questions when specific ones aren't available."""
        fallback_questions = [
            {
                "question": f"Describe your experience with {competency.replace('_', ' ')} in your current or previous role.",
                "competency": competency,
                "type": "experience",
                "focus_areas": ["experience_depth", "practical_application"]
            },
            {
                "question": f"What challenges have you faced related to {competency.replace('_', ' ')} and how did you overcome them?",
                "competency": competency,
                "type": "challenge_based",
                "focus_areas": ["problem_solving", "learning_from_experience"]
            }
        ]
        return fallback_questions
    def _create_scoring_rubrics(self, questions: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Create scoring rubrics for the generated questions."""
        rubrics = {}
        
        for i, question in enumerate(questions, 1):
            question_key = f"question_{i}"
            question_type = question.get("type", "behavioral")
            
            if question_type in self.scoring_rubrics:
                rubrics[question_key] = {
                    "question": question["question"],
                    "competency": question["competency"],
                    "type": question_type,
                    "scoring_criteria": self.scoring_rubrics[question_type],
                    "weight": self._determine_question_weight(question),
                    "time_limit": question.get("time_limit", 30)
                }
        
        return rubrics
    def _determine_question_weight(self, question: Dict[str, Any]) -> str:
        """Determine the weight/importance of a question."""
        competency = question.get("competency", "")
        question_type = question.get("type", "")
        difficulty = question.get("difficulty", "medium")
        
        # Core competencies get higher weight
        core_competencies = ["coding_fundamentals", "system_design", "leadership", "problem_solving"]
        
        if competency in core_competencies:
            return "high"
        elif question_type in ["coding", "design"] or difficulty == "hard":
            return "high" 
        elif difficulty == "easy":
            return "medium"
        else:
            return "medium"
    def _generate_follow_up_probes(self, questions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate follow-up probes for each question."""
        probes = {}
        
        for i, question in enumerate(questions, 1):
            question_key = f"question_{i}"
            competency = question.get("competency", "")
            
            # Get competency-specific follow-ups
            if competency in self.follow_up_strategies:
                competency_probes = self.follow_up_strategies[competency].copy()
            else:
                competency_probes = [
                    "Can you provide more specific details about your approach?",
                    "What would you do differently if you had to do this again?",
                    "What challenges did you face and how did you overcome them?"
                ]
            
            # Add question-type specific probes
            question_type = question.get("type", "")
            if question_type == "coding":
                competency_probes.extend([
                    "How would you test this solution?",
                    "What's the time and space complexity of your approach?",
                    "Can you think of any optimizations?"
                ])
            elif question_type == "behavioral":
                competency_probes.extend([
                    "What did you learn from this experience?",
                    "How did others react to your approach?",
                    "What metrics did you use to measure success?"
                ])
            elif question_type == "design":
                competency_probes.extend([
                    "How would you handle failure scenarios?",
                    "What monitoring would you implement?",
                    "How would this scale to 10x the load?"
                ])
            
            probes[question_key] = competency_probes[:5]  # Limit to 5 follow-ups
        
        return probes
