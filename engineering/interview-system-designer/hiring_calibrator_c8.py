# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin8:
    def _detect_score_inflation(self, scores: List[float]) -> Dict[str, Any]:
        """Detect if an interviewer shows score inflation patterns."""
        if len(scores) < 5:
            return {"insufficient_data": True}
        
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores)
        
        # Check against expected mean (2.8)
        expected_mean = self.calibration_standards["score_distribution"]["target_mean"]
        deviation = mean_score - expected_mean
        
        # High scores with low variance might indicate inflation
        high_scores_low_variance = mean_score > 3.2 and std_score < 0.5
        
        # Check distribution - too many 4s might indicate inflation
        score_counts = Counter([int(score) for score in scores])
        four_count_ratio = score_counts.get(4, 0) / len(scores)
        
        return {
            "mean_score": round(mean_score, 2),
            "expected_mean": expected_mean,
            "deviation": round(deviation, 2),
            "high_scores_low_variance": high_scores_low_variance,
            "four_count_ratio": round(four_count_ratio, 2),
            "inflation_detected": deviation > 0.3 or high_scores_low_variance or four_count_ratio > 0.4
        }
    def _calculate_interviewer_consistency(self, records: List[Dict[str, Any]]) -> float:
        """Calculate consistency score for an interviewer."""
        if len(records) < 3:
            return 0.5  # Neutral score for insufficient data
        
        # Look at variance in scoring
        avg_scores = [r["average_score"] for r in records]
        score_variance = statistics.variance(avg_scores)
        
        # Look at decision consistency relative to scores
        decisions = [r["hire_decision"] for r in records]
        scores_of_hires = [r["average_score"] for r in records if r["hire_decision"]]
        scores_of_no_hires = [r["average_score"] for r in records if not r["hire_decision"]]
        
        # Good consistency means hires have higher average scores
        decision_consistency = 0.5
        if scores_of_hires and scores_of_no_hires:
            hire_mean = statistics.mean(scores_of_hires)
            no_hire_mean = statistics.mean(scores_of_no_hires)
            score_gap = hire_mean - no_hire_mean
            decision_consistency = min(1.0, max(0.0, score_gap / 2.0))  # Normalize to 0-1
        
        # Combine metrics (lower variance = higher consistency)
        variance_consistency = max(0.0, 1.0 - (score_variance / 2.0))
        
        return (decision_consistency + variance_consistency) / 2
    def _calculate_overall_interviewer_consistency(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall consistency across all interviewers."""
        interviewer_consistency_scores = []
        
        interviewer_records = defaultdict(list)
        for record in data:
            interviewer_records[record["interviewer_id"]].append(record)
        
        for interviewer_id, records in interviewer_records.items():
            if len(records) >= 3:
                consistency = self._calculate_interviewer_consistency(records)
                interviewer_consistency_scores.append(consistency)
        
        if not interviewer_consistency_scores:
            return {"error": "Insufficient data per interviewer for consistency analysis"}
        
        return {
            "mean_consistency": round(statistics.mean(interviewer_consistency_scores), 3),
            "std_consistency": round(statistics.stdev(interviewer_consistency_scores) if len(interviewer_consistency_scores) > 1 else 0, 3),
            "min_consistency": round(min(interviewer_consistency_scores), 3),
            "max_consistency": round(max(interviewer_consistency_scores), 3),
            "interviewers_analyzed": len(interviewer_consistency_scores),
            "target_threshold": self.bias_thresholds["interviewer_consistency_threshold"]
        }
    def _calculate_bias_score(self, bias_analysis: Dict[str, Any]) -> float:
        """Calculate overall bias score (0-1, where 1 is most biased)."""
        bias_factors = []
        
        # Demographic bias factors
        demographic_bias = bias_analysis.get("demographic_bias", {})
        for demo, analysis in demographic_bias.items():
            if analysis.get("bias_detected"):
                bias_factors.append(0.3)  # Each demographic bias adds 0.3
        
        # Interviewer bias factors
        interviewer_bias = bias_analysis.get("interviewer_bias", {})
        outlier_interviewers = interviewer_bias.get("outlier_interviewers", {})
        if outlier_interviewers:
            # Scale by severity and number of outliers
            total_severity = sum(info["severity"] for info in outlier_interviewers.values())
            bias_factors.append(min(0.5, total_severity * 0.1))
        
        # Competency bias factors  
        competency_bias = bias_analysis.get("competency_bias", {})
        for comp, analysis in competency_bias.items():
            if analysis.get("bias_detected"):
                bias_factors.append(0.2)  # Each competency bias adds 0.2
        
        return min(1.0, sum(bias_factors))
