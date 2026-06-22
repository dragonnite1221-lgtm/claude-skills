# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


def format_human_readable(calibration_report: Dict[str, Any]) -> str:
    """Format calibration report in human-readable format."""
    output = []
    
    # Header
    output.append("HIRING CALIBRATION ANALYSIS REPORT")
    output.append("=" * 60)
    output.append(f"Analysis Type: {calibration_report.get('analysis_type', 'N/A').title()}")
    output.append(f"Generated: {calibration_report.get('generated_at', 'N/A')}")
    
    if "error" in calibration_report:
        output.append(f"\nError: {calibration_report['error']}")
        return "\n".join(output)
    
    # Data Summary
    data_summary = calibration_report.get("data_summary", {})
    if data_summary:
        output.append(f"\nDATA SUMMARY")
        output.append("-" * 30)
        output.append(f"Total Candidates: {data_summary.get('total_candidates', 0)}")
        output.append(f"Unique Interviewers: {data_summary.get('unique_interviewers', 0)}")
        output.append(f"Overall Hire Rate: {data_summary.get('hire_rate', 0):.1%}")
        
        score_stats = data_summary.get("score_statistics", {})
        output.append(f"Average Score: {score_stats.get('mean_average_scores', 0):.2f}")
        output.append(f"Score Std Dev: {score_stats.get('std_average_scores', 0):.2f}")
    
    # Health Score
    health_score = calibration_report.get("calibration_health_score", {})
    if health_score:
        output.append(f"\nCALIBRATION HEALTH SCORE")
        output.append("-" * 30)
        output.append(f"Overall Score: {health_score.get('overall_score', 0):.3f}")
        output.append(f"Health Category: {health_score.get('health_category', 'Unknown').title()}")
        
        if health_score.get("improvement_priority"):
            output.append(f"Priority Areas: {', '.join(health_score['improvement_priority'])}")
    
    # Bias Analysis
    bias_analysis = calibration_report.get("bias_analysis", {})
    if bias_analysis:
        output.append(f"\nBIAS ANALYSIS")
        output.append("-" * 30)
        output.append(f"Overall Bias Score: {bias_analysis.get('overall_bias_score', 0):.3f}")
        
        # Demographic bias
        demographic_bias = bias_analysis.get("demographic_bias", {})
        if demographic_bias:
            output.append(f"\nDemographic Bias Issues:")
            for demo, analysis in demographic_bias.items():
                output.append(f"  • {demo.replace('_', ' ').title()}: {analysis.get('bias_details', {}).keys()}")
        
        # Interviewer bias
        interviewer_bias = bias_analysis.get("interviewer_bias", {})
        outlier_interviewers = interviewer_bias.get("outlier_interviewers", {})
        if outlier_interviewers:
            output.append(f"\nOutlier Interviewers:")
            for interviewer, info in outlier_interviewers.items():
                issues = ", ".join(info["issues"])
                output.append(f"  • {interviewer}: {issues}")
    
    # Calibration Analysis
    calibration_analysis = calibration_report.get("calibration_analysis", {})
    if calibration_analysis and "error" not in calibration_analysis:
        output.append(f"\nCALIBRATION CONSISTENCY")
        output.append("-" * 30)
        output.append(f"Quality: {calibration_analysis.get('calibration_quality', 'Unknown').title()}")
        output.append(f"Agreement Rate: {calibration_analysis.get('agreement_within_one_point_rate', 0):.1%}")
        output.append(f"Score Std Dev: {calibration_analysis.get('mean_score_standard_deviation', 0):.3f}")
    
    # Scoring Analysis
    scoring_analysis = calibration_report.get("scoring_analysis", {})
    if scoring_analysis:
        output.append(f"\nSCORING PATTERNS")
        output.append("-" * 30)
        output.append(f"Overall Assessment: {scoring_analysis.get('overall_assessment', 'Unknown').title()}")
        
        score_stats = scoring_analysis.get("score_statistics", {})
        output.append(f"Mean Score: {score_stats.get('mean_score', 0):.2f} (Target: {score_stats.get('target_mean', 0):.2f})")
        
        # Distribution analysis
        distribution = scoring_analysis.get("score_distribution", {})
        if distribution:
            output.append(f"\nScore Distribution vs Expected:")
            for score in ["1", "2", "3", "4"]:
                if score in distribution:
                    actual = distribution[score]["actual_percentage"]
                    expected = distribution[score]["expected_percentage"]
                    output.append(f"  Score {score}: {actual:.1%} (Expected: {expected:.1%})")
    
    # Top Recommendations
    recommendations = calibration_report.get("recommendations", [])
    if recommendations:
        output.append(f"\nTOP RECOMMENDATIONS")
        output.append("-" * 30)
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
            output.append(f"{i}. {rec['title']} ({rec['priority'].title()} Priority)")
            output.append(f"   {rec['description']}")
            if rec.get('actions'):
                output.append(f"   Actions: {len(rec['actions'])} specific action items")
    
    return "\n".join(output)
