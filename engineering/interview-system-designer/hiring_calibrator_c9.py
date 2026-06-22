# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin9:
    def _calculate_health_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall calibration health score."""
        health_factors = []
        
        # Bias score (lower is better)
        bias_analysis = analysis.get("bias_analysis", {})
        bias_score = bias_analysis.get("overall_bias_score", 0)
        bias_health = max(0, 1 - bias_score)
        health_factors.append(("bias", bias_health, 0.3))
        
        # Calibration consistency
        calibration_analysis = analysis.get("calibration_analysis", {})
        if "calibration_quality" in calibration_analysis:
            quality_map = {"good": 1.0, "fair": 0.7, "poor": 0.3}
            calibration_health = quality_map.get(calibration_analysis["calibration_quality"], 0.5)
            health_factors.append(("calibration", calibration_health, 0.25))
        
        # Interviewer consistency
        interviewer_analysis = analysis.get("interviewer_analysis", {})
        overall_consistency = interviewer_analysis.get("overall_consistency", {})
        if "mean_consistency" in overall_consistency:
            consistency_health = overall_consistency["mean_consistency"]
            health_factors.append(("interviewer_consistency", consistency_health, 0.25))
        
        # Scoring patterns health
        scoring_analysis = analysis.get("scoring_analysis", {})
        if "overall_assessment" in scoring_analysis:
            assessment_map = {"healthy": 1.0, "concerning": 0.6, "poor": 0.2}
            scoring_health = assessment_map.get(scoring_analysis["overall_assessment"], 0.5)
            health_factors.append(("scoring_patterns", scoring_health, 0.2))
        
        # Calculate weighted average
        if health_factors:
            weighted_sum = sum(score * weight for _, score, weight in health_factors)
            total_weight = sum(weight for _, _, weight in health_factors)
            overall_score = weighted_sum / total_weight
        else:
            overall_score = 0.5  # Neutral if no data
        
        # Categorize health
        if overall_score >= 0.8:
            health_category = "excellent"
        elif overall_score >= 0.7:
            health_category = "good"
        elif overall_score >= 0.5:
            health_category = "fair"
        else:
            health_category = "poor"
        
        return {
            "overall_score": round(overall_score, 3),
            "health_category": health_category,
            "component_scores": {name: round(score, 3) for name, score, _ in health_factors},
            "improvement_priority": self._identify_improvement_priorities(health_factors)
        }
    def _identify_improvement_priorities(self, health_factors: List[Tuple[str, float, float]]) -> List[str]:
        """Identify areas that need the most improvement."""
        priorities = []
        
        for name, score, weight in health_factors:
            impact = (1 - score) * weight  # Low scores with high weights = high priority
            if impact > 0.15:  # Significant impact threshold
                priorities.append(name)
        
        # Sort by impact (highest first)
        priorities.sort(key=lambda name: next((1 - score) * weight for n, score, weight in health_factors if n == name), reverse=True)
        
        return priorities
