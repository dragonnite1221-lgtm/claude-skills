# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin11:
    def _generate_demographic_bias_recommendation(self, demographic: str, bias_details: Dict[str, Any]) -> str:
        """Generate specific recommendation for demographic bias."""
        if "hire_rate_disparity" in bias_details:
            return f"Significant hire rate disparity detected for {demographic}. Implement structured interviews and diverse panels."
        elif "scoring_disparity" in bias_details:
            return f"Scoring disparity detected for {demographic}. Provide unconscious bias training and standardize evaluation criteria."
        else:
            return f"Potential bias detected for {demographic}. Monitor closely and implement bias mitigation strategies."
    def _generate_interviewer_recommendations(self, outlier_interviewers: Dict[str, Any]) -> List[str]:
        """Generate recommendations for interviewer issues."""
        if not outlier_interviewers:
            return ["All interviewers performing within expected ranges"]
        
        recommendations = []
        for interviewer, info in outlier_interviewers.items():
            issues = info["issues"]
            if len(issues) >= 2:
                recommendations.append(f"Interviewer {interviewer}: Requires comprehensive recalibration - multiple issues detected")
            elif "score_inflation" in issues:
                recommendations.append(f"Interviewer {interviewer}: Provide calibration training on scoring standards")
            elif "hire_rate_deviation" in issues:
                recommendations.append(f"Interviewer {interviewer}: Review hiring bar standards and decision criteria")
        
        return recommendations
    def _generate_calibration_recommendations(self, mean_std: float, agreement_rate: float) -> List[str]:
        """Generate calibration improvement recommendations."""
        recommendations = []
        
        if mean_std > self.calibration_standards["interviewer_agreement"]["maximum_std_deviation"]:
            recommendations.append("High score variance detected - implement regular calibration sessions")
            recommendations.append("Create shared examples of scoring standards for each competency")
        
        if agreement_rate < self.calibration_standards["interviewer_agreement"]["agreement_threshold"]:
            recommendations.append("Low interviewer agreement rate - standardize interview questions and evaluation criteria")
            recommendations.append("Implement mandatory interviewer training on consistent evaluation")
        
        if not recommendations:
            recommendations.append("Calibration appears healthy - maintain current practices")
        
        return recommendations
    def _assess_scoring_health(self, distribution: Dict[str, Any], mean_score: float, target_mean: float) -> str:
        """Assess overall health of scoring patterns."""
        issues = 0
        
        # Check distribution deviations
        for score_level, analysis in distribution.items():
            if analysis["significant_deviation"]:
                issues += 1
        
        # Check mean deviation
        if abs(mean_score - target_mean) > 0.3:
            issues += 1
        
        if issues == 0:
            return "healthy"
        elif issues <= 2:
            return "concerning"
        else:
            return "poor"
    def _generate_trend_insights(self, score_trend: float, hire_rate_trend: float, period_metrics: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis."""
        insights = []
        
        if abs(score_trend) > 0.05:
            direction = "increasing" if score_trend > 0 else "decreasing"
            insights.append(f"Significant {direction} trend in average scores over time")
            
            if score_trend > 0:
                insights.append("May indicate score inflation or improving candidate quality")
            else:
                insights.append("May indicate stricter evaluation or declining candidate quality")
        
        if abs(hire_rate_trend) > 0.02:
            direction = "increasing" if hire_rate_trend > 0 else "decreasing"
            insights.append(f"Significant {direction} trend in hire rates over time")
            
            if hire_rate_trend > 0:
                insights.append("Consider if hiring bar has lowered or candidate pool improved")
            else:
                insights.append("Consider if hiring bar has raised or candidate pool declined")
        
        # Check for consistency
        period_values = list(period_metrics.values())
        hire_rates = [p["hire_rate"] for p in period_values]
        hire_rate_variance = statistics.variance(hire_rates) if len(hire_rates) > 1 else 0
        
        if hire_rate_variance > 0.01:  # High variance in hire rates
            insights.append("High variance in hire rates across periods - consider process standardization")
        
        if not insights:
            insights.append("Hiring patterns appear stable over time")
        
        return insights
