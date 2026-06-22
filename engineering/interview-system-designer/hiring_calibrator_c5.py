# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin5:
    def _analyze_calibration_consistency(self, data: List[Dict[str, Any]], 
                                       target_competencies: Optional[List[str]]) -> Dict[str, Any]:
        """Analyze calibration consistency across interviews."""
        
        # Group candidates by those interviewed by multiple people
        candidate_interviewers = defaultdict(list)
        for record in data:
            candidate_interviewers[record["candidate_id"]].append(record)
        
        multi_interviewer_candidates = {
            candidate: records for candidate, records in candidate_interviewers.items()
            if len(records) > 1
        }
        
        if not multi_interviewer_candidates:
            return {
                "error": "No candidates with multiple interviewers found",
                "single_interviewer_analysis": self._analyze_single_interviewer_consistency(data)
            }
        
        # Calculate agreement statistics
        agreement_stats = []
        score_correlations = []
        
        for candidate, records in multi_interviewer_candidates.items():
            candidate_scores = []
            interviewer_pairs = []
            
            for record in records:
                avg_score = record["average_score"]
                candidate_scores.append(avg_score)
                interviewer_pairs.append(record["interviewer_id"])
            
            if len(candidate_scores) > 1:
                # Calculate standard deviation of scores for this candidate
                score_std = statistics.stdev(candidate_scores)
                agreement_stats.append(score_std)
                
                # Check if all interviewers agree within 1 point
                score_range = max(candidate_scores) - min(candidate_scores)
                agreement_within_one = score_range <= 1.0
                
                score_correlations.append({
                    "candidate": candidate,
                    "scores": candidate_scores,
                    "interviewers": interviewer_pairs,
                    "score_std": score_std,
                    "score_range": score_range,
                    "agreement_within_one": agreement_within_one
                })
        
        # Calculate overall calibration metrics
        mean_score_std = statistics.mean(agreement_stats) if agreement_stats else 0
        agreement_rate = sum(1 for corr in score_correlations if corr["agreement_within_one"]) / len(score_correlations) if score_correlations else 0
        
        calibration_quality = "good"
        if mean_score_std > self.calibration_standards["interviewer_agreement"]["maximum_std_deviation"]:
            calibration_quality = "poor"
        elif agreement_rate < self.calibration_standards["interviewer_agreement"]["agreement_threshold"]:
            calibration_quality = "fair"
        
        return {
            "multi_interviewer_candidates": len(multi_interviewer_candidates),
            "mean_score_standard_deviation": round(mean_score_std, 3),
            "agreement_within_one_point_rate": round(agreement_rate, 3),
            "calibration_quality": calibration_quality,
            "candidate_agreement_details": score_correlations,
            "target_standards": self.calibration_standards["interviewer_agreement"],
            "recommendations": self._generate_calibration_recommendations(mean_score_std, agreement_rate)
        }
