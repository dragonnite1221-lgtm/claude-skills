# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin3:
    def _analyze_interviewer_bias(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze bias patterns across different interviewers."""
        interviewer_stats = defaultdict(list)
        
        # Group by interviewer
        for record in data:
            interviewer_id = record["interviewer_id"]
            interviewer_stats[interviewer_id].append(record)
        
        # Calculate statistics per interviewer
        interviewer_analysis = {}
        for interviewer_id, records in interviewer_stats.items():
            if len(records) >= self.bias_thresholds["minimum_sample_size"]:
                scores = [r["average_score"] for r in records]
                hire_rate = sum(r["hire_decision"] for r in records) / len(records)
                
                interviewer_analysis[interviewer_id] = {
                    "total_interviews": len(records),
                    "mean_score": statistics.mean(scores),
                    "std_score": statistics.stdev(scores) if len(scores) > 1 else 0,
                    "hire_rate": hire_rate,
                    "score_inflation": self._detect_score_inflation(scores),
                    "consistency_score": self._calculate_interviewer_consistency(records)
                }
        
        # Identify outlier interviewers
        if len(interviewer_analysis) > 1:
            overall_mean_score = statistics.mean([stats["mean_score"] for stats in interviewer_analysis.values()])
            overall_hire_rate = statistics.mean([stats["hire_rate"] for stats in interviewer_analysis.values()])
            
            outlier_interviewers = {}
            for interviewer_id, stats in interviewer_analysis.items():
                issues = []
                
                # Check for score inflation/deflation
                if stats["mean_score"] > overall_mean_score * (1 + self.bias_thresholds["score_inflation_threshold"]):
                    issues.append("score_inflation")
                elif stats["mean_score"] < overall_mean_score * (1 - self.bias_thresholds["score_deflation_threshold"]):
                    issues.append("score_deflation")
                
                # Check for hire rate deviation
                hire_rate_diff = abs(stats["hire_rate"] - overall_hire_rate)
                if hire_rate_diff > self.bias_thresholds["pass_rate_difference_threshold"]:
                    issues.append("hire_rate_deviation")
                
                # Check for low consistency
                if stats["consistency_score"] < self.bias_thresholds["interviewer_consistency_threshold"]:
                    issues.append("low_consistency")
                
                if issues:
                    outlier_interviewers[interviewer_id] = {
                        "issues": issues,
                        "statistics": stats,
                        "severity": len(issues)  # More issues = higher severity
                    }
        
        return {
            "interviewer_statistics": interviewer_analysis,
            "outlier_interviewers": outlier_interviewers if len(interviewer_analysis) > 1 else {},
            "overall_consistency": self._calculate_overall_interviewer_consistency(data),
            "recommendations": self._generate_interviewer_recommendations(outlier_interviewers if len(interviewer_analysis) > 1 else {})
        }
