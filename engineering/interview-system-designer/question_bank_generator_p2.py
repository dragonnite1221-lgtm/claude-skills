# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from question_bank_generator_base import *  # noqa: F403,E402


def format_human_readable(question_bank: Dict[str, Any]) -> str:
    """Format question bank data in human-readable format."""
    output = []
    
    # Header
    output.append(f"Interview Question Bank: {question_bank['role']} ({question_bank['level'].title()} Level)")
    output.append("=" * 70)
    output.append(f"Generated: {question_bank['generated_at']}")
    output.append(f"Total Questions: {question_bank['total_questions']}")
    output.append(f"Question Types: {', '.join(question_bank['question_types'])}")
    output.append(f"Target Competencies: {', '.join(question_bank['competencies'])}")
    output.append("")
    
    # Questions
    output.append("INTERVIEW QUESTIONS")
    output.append("-" * 50)
    
    for i, question in enumerate(question_bank['questions'], 1):
        output.append(f"\n{i}. {question['question']}")
        output.append(f"   Competency: {question['competency'].replace('_', ' ').title()}")
        output.append(f"   Type: {question.get('type', 'N/A').title()}")
        if 'time_limit' in question:
            output.append(f"   Time Limit: {question['time_limit']} minutes")
        if 'focus_areas' in question:
            output.append(f"   Focus Areas: {', '.join(question['focus_areas'])}")
    
    # Scoring Guidelines
    output.append("\n\nSCORING RUBRICS")
    output.append("-" * 50)
    
    # Show sample scoring criteria
    if question_bank['scoring_rubrics']:
        first_question = list(question_bank['scoring_rubrics'].keys())[0]
        sample_rubric = question_bank['scoring_rubrics'][first_question]
        
        output.append(f"Sample Scoring Criteria ({sample_rubric['type']} questions):")
        for criterion, scores in sample_rubric['scoring_criteria'].items():
            output.append(f"\n{criterion.replace('_', ' ').title()}:")
            for score, description in scores.items():
                output.append(f"  {score}: {description}")
    
    # Follow-up Probes
    output.append("\n\nFOLLOW-UP PROBE EXAMPLES")
    output.append("-" * 50)
    
    if question_bank['follow_up_probes']:
        first_question = list(question_bank['follow_up_probes'].keys())[0]
        sample_probes = question_bank['follow_up_probes'][first_question]
        
        output.append("Sample follow-up questions:")
        for probe in sample_probes[:3]:  # Show first 3
            output.append(f"  • {probe}")
    
    # Usage Guidelines
    output.append("\n\nUSAGE GUIDELINES")
    output.append("-" * 50)
    
    guidelines = question_bank['usage_guidelines']
    
    output.append("Interview Flow:")
    for phase, description in guidelines['interview_flow'].items():
        output.append(f"  • {phase.replace('_', ' ').title()}: {description}")
    
    output.append("\nTime Management:")
    for aspect, recommendation in guidelines['time_management'].items():
        output.append(f"  • {aspect.replace('_', ' ').title()}: {recommendation}")
    
    output.append("\nCommon Mistakes to Avoid:")
    for mistake in guidelines['common_mistakes'][:3]:  # Show first 3
        output.append(f"  • {mistake}")
    
    # Calibration Examples (if available)
    if question_bank['calibration_examples']:
        output.append("\n\nCALIBRATION EXAMPLES")
        output.append("-" * 50)
        
        first_example = list(question_bank['calibration_examples'].values())[0]
        output.append(f"Question: {first_example['question']}")
        
        output.append("\nSample Answer Quality Levels:")
        for quality, details in first_example['sample_answers'].items():
            output.append(f"  {quality.replace('_', ' ').title()} (Score {details['score']}):")
            if 'issues' in details:
                output.append(f"    Issues: {', '.join(details['issues'])}")
            if 'strengths' in details:
                output.append(f"    Strengths: {', '.join(details['strengths'])}")
    
    return "\n".join(output)
