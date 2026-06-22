# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin10:
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis results."""
        recommendations = []
        
        # Bias-related recommendations
        bias_analysis = analysis.get("bias_analysis", {})
        
        # Demographic bias recommendations
        for demo, demo_analysis in bias_analysis.get("demographic_bias", {}).items():
            if demo_analysis.get("bias_detected"):
                recommendations.append({
                    "priority": "high",
                    "category": "bias_mitigation",
                    "title": f"Address {demo.replace('_', ' ').title()} Bias",
                    "description": demo_analysis.get("recommendation", f"Implement bias mitigation strategies for {demo}"),
                    "actions": [
                        "Conduct unconscious bias training focused on this demographic",
                        "Review and standardize interview questions",
                        "Implement diverse interview panels",
                        "Monitor hiring metrics by demographic group"
                    ]
                })
        
        # Interviewer-specific recommendations
        interviewer_analysis = bias_analysis.get("interviewer_bias", {})
        outlier_interviewers = interviewer_analysis.get("outlier_interviewers", {})
        
        for interviewer_id, outlier_info in outlier_interviewers.items():
            issues = outlier_info["issues"]
            priority = "high" if outlier_info["severity"] >= 3 else "medium"
            
            actions = []
            if "score_inflation" in issues:
                actions.extend([
                    "Provide calibration training on scoring standards",
                    "Shadow experienced interviewers for recalibration",
                    "Review examples of each score level"
                ])
            if "score_deflation" in issues:
                actions.extend([
                    "Review expectations for role level",
                    "Calibrate against recent successful hires",
                    "Discuss evaluation criteria with hiring manager"
                ])
            if "hire_rate_deviation" in issues:
                actions.extend([
                    "Review hiring bar standards",
                    "Participate in calibration sessions",
                    "Compare decision criteria with team"
                ])
            if "low_consistency" in issues:
                actions.extend([
                    "Practice structured interviewing techniques",
                    "Use standardized scorecards",
                    "Document specific examples for each score"
                ])
            
            recommendations.append({
                "priority": priority,
                "category": "interviewer_coaching",
                "title": f"Coach Interviewer {interviewer_id}",
                "description": f"Address issues: {', '.join(issues)}",
                "actions": list(set(actions))  # Remove duplicates
            })
        
        # Calibration recommendations
        calibration_analysis = analysis.get("calibration_analysis", {})
        if calibration_analysis.get("calibration_quality") in ["fair", "poor"]:
            recommendations.append({
                "priority": "high",
                "category": "calibration_improvement",
                "title": "Improve Interview Calibration",
                "description": f"Current calibration quality: {calibration_analysis.get('calibration_quality')}",
                "actions": [
                    "Conduct monthly calibration sessions",
                    "Create shared examples of good/poor answers",
                    "Implement mandatory interviewer shadowing",
                    "Standardize scoring rubrics across all interviewers",
                    "Review and align on role expectations"
                ]
            })
        
        # Scoring pattern recommendations
        scoring_analysis = analysis.get("scoring_analysis", {})
        if scoring_analysis.get("overall_assessment") in ["concerning", "poor"]:
            recommendations.append({
                "priority": "medium",
                "category": "scoring_standards",
                "title": "Adjust Scoring Standards",
                "description": "Scoring patterns deviate significantly from expected distribution",
                "actions": [
                    "Review and communicate target score distributions",
                    "Provide examples for each score level",
                    "Monitor pass rates by role level",
                    "Adjust hiring bar if consistently too high/low"
                ]
            })
        
        # Health score recommendations
        health_score = analysis.get("calibration_health_score", {})
        priorities = health_score.get("improvement_priority", [])
        
        if "bias" in priorities:
            recommendations.append({
                "priority": "critical",
                "category": "bias_mitigation", 
                "title": "Implement Comprehensive Bias Mitigation",
                "description": "Multiple bias indicators detected across the hiring process",
                "actions": [
                    "Mandatory unconscious bias training for all interviewers",
                    "Implement structured interview protocols",
                    "Diversify interview panels",
                    "Regular bias audits and monitoring",
                    "Create accountability metrics for fair hiring"
                ]
            })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return recommendations
