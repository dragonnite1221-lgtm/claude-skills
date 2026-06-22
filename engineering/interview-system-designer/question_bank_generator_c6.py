# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


class QuestionBankGeneratorMixin6:
    def _create_calibration_examples(self, sample_questions: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Create calibration examples with poor/good/great answers."""
        examples = {}
        
        for i, question in enumerate(sample_questions, 1):
            question_key = f"question_{i}"
            examples[question_key] = {
                "question": question["question"],
                "competency": question["competency"],
                "sample_answers": {
                    "poor_answer": self._generate_sample_answer(question, "poor"),
                    "good_answer": self._generate_sample_answer(question, "good"), 
                    "great_answer": self._generate_sample_answer(question, "great")
                },
                "scoring_rationale": self._generate_scoring_rationale(question)
            }
        
        return examples
    def _generate_sample_answer(self, question: Dict[str, Any], quality: str) -> Dict[str, str]:
        """Generate sample answers of different quality levels."""
        competency = question.get("competency", "")
        question_type = question.get("type", "")
        
        if quality == "poor":
            return {
                "answer": f"Sample poor answer for {competency} question - lacks detail, specificity, or demonstrates weak competency",
                "score": "1-2",
                "issues": ["Vague response", "Limited evidence of competency", "Poor structure"]
            }
        elif quality == "good":
            return {
                "answer": f"Sample good answer for {competency} question - adequate detail, demonstrates competency clearly",
                "score": "3", 
                "strengths": ["Clear structure", "Demonstrates competency", "Adequate detail"]
            }
        else:  # great
            return {
                "answer": f"Sample excellent answer for {competency} question - exceptional detail, strong evidence, goes above and beyond",
                "score": "4",
                "strengths": ["Exceptional detail", "Strong evidence", "Strategic thinking", "Goes beyond requirements"]
            }
    def _generate_scoring_rationale(self, question: Dict[str, Any]) -> Dict[str, str]:
        """Generate rationale for scoring this question."""
        competency = question.get("competency", "")
        return {
            "key_indicators": f"Look for evidence of {competency.replace('_', ' ')} competency",
            "red_flags": "Vague answers, lack of specifics, negative outcomes without learning",
            "green_flags": "Specific examples, clear impact, demonstrates growth and learning"
        }
    def _generate_usage_guidelines(self, role_key: str, level_key: str) -> Dict[str, Any]:
        """Generate usage guidelines for the question bank."""
        return {
            "interview_flow": {
                "warm_up": "Start with 1-2 easier questions to build rapport",
                "core_assessment": "Focus majority of time on core competency questions",
                "closing": "End with questions about candidate's questions/interests"
            },
            "time_management": {
                "technical_questions": "Allow extra time for coding/design questions",
                "behavioral_questions": "Keep to time limits but allow for follow-ups",
                "total_recommendation": "45-75 minutes per interview round"
            },
            "question_selection": {
                "variety": "Mix question types within each competency area",
                "difficulty": "Adjust based on candidate responses and energy",
                "customization": "Adapt questions based on candidate's background"
            },
            "common_mistakes": [
                "Don't ask all questions mechanically",
                "Don't skip follow-up questions",
                "Don't forget to assess cultural fit alongside competencies",
                "Don't let one strong/weak area bias overall assessment"
            ],
            "calibration_reminders": [
                "Compare against role standard, not other candidates",
                "Focus on evidence demonstrated, not potential",
                "Consider level-appropriate expectations",
                "Document specific examples in feedback"
            ]
        }
