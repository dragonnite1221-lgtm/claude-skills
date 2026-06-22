# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


class QuestionBankGeneratorMixin2:
    def _init_scoring_rubrics(self) -> Dict[str, Dict]:
        """Initialize scoring rubrics for different question types."""
        return {
            "coding": {
                "correctness": {
                    "4": "Solution is completely correct, handles all edge cases, optimal complexity",
                    "3": "Solution is correct for main cases, good complexity, minor edge case issues",
                    "2": "Solution works but has some bugs or suboptimal approach",
                    "1": "Solution has significant issues or doesn't work"
                },
                "code_quality": {
                    "4": "Clean, readable, well-structured code with excellent naming and comments",
                    "3": "Good code structure, readable with appropriate naming",
                    "2": "Code works but has style/structure issues",
                    "1": "Poor code quality, hard to understand"
                },
                "problem_solving_approach": {
                    "4": "Excellent problem breakdown, clear thinking process, considers alternatives",
                    "3": "Good approach, logical thinking, systematic problem solving",
                    "2": "Decent approach but some confusion or inefficiency",
                    "1": "Poor approach, unclear thinking process"
                },
                "communication": {
                    "4": "Excellent explanation of approach, asks clarifying questions, clear reasoning",
                    "3": "Good communication, explains thinking well",
                    "2": "Adequate communication, some explanation",
                    "1": "Poor communication, little explanation"
                }
            },
            "behavioral": {
                "situation_clarity": {
                    "4": "Clear, specific situation with relevant context and stakes",
                    "3": "Good situation description with adequate context",
                    "2": "Situation described but lacks some specifics",
                    "1": "Vague or unclear situation description"
                },
                "action_quality": {
                    "4": "Specific, thoughtful actions showing strong competency",
                    "3": "Good actions demonstrating competency",
                    "2": "Adequate actions but could be stronger",
                    "1": "Weak or inappropriate actions"
                },
                "result_impact": {
                    "4": "Significant positive impact with measurable results",
                    "3": "Good positive impact with clear outcomes",
                    "2": "Some positive impact demonstrated",
                    "1": "Little or no positive impact shown"
                },
                "self_awareness": {
                    "4": "Excellent self-reflection, learns from experience, acknowledges growth areas",
                    "3": "Good self-awareness and learning orientation",
                    "2": "Some self-reflection demonstrated",
                    "1": "Limited self-awareness or reflection"
                }
            },
            "design": {
                "system_thinking": {
                    "4": "Comprehensive system view, considers all components and interactions",
                    "3": "Good system understanding with most components identified",
                    "2": "Basic system thinking with some gaps",
                    "1": "Limited system thinking, misses key components"
                },
                "scalability": {
                    "4": "Excellent scalability considerations, multiple strategies discussed",
                    "3": "Good scalability awareness with practical solutions",
                    "2": "Basic scalability understanding",
                    "1": "Little to no scalability consideration"
                },
                "trade_offs": {
                    "4": "Excellent trade-off analysis, considers multiple dimensions",
                    "3": "Good trade-off awareness with clear reasoning",
                    "2": "Some trade-off consideration",
                    "1": "Limited trade-off analysis"
                },
                "technical_depth": {
                    "4": "Deep technical knowledge with implementation details",
                    "3": "Good technical knowledge with solid understanding",
                    "2": "Adequate technical knowledge",
                    "1": "Limited technical depth"
                }
            }
        }
