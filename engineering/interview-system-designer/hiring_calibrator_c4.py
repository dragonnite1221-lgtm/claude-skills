# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin4:
    def _analyze_competency_bias(self, data: List[Dict[str, Any]], 
                               competencies: List[str]) -> Dict[str, Any]:
        """Analyze bias patterns within specific competencies."""
        competency_analysis = {}
        
        for competency in competencies:
            # Extract scores for this competency
            competency_scores = []
            for record in data:
                if competency in record["scores"]:
                    competency_scores.append({
                        "score": record["scores"][competency],
                        "interviewer": record["interviewer_id"],
                        "candidate": record["candidate_id"],
                        "overall_decision": record["hire_decision"]
                    })
            
            if len(competency_scores) < self.bias_thresholds["minimum_sample_size"]:
                continue
            
            # Analyze scoring patterns
            scores = [item["score"] for item in competency_scores]
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            
            # Analyze by interviewer
            interviewer_competency_scores = defaultdict(list)
            for item in competency_scores:
                interviewer_competency_scores[item["interviewer"]].append(item["score"])
            
            interviewer_variations = {}
            if len(interviewer_competency_scores) > 1:
                interviewer_means = {interviewer: statistics.mean(scores) 
                                   for interviewer, scores in interviewer_competency_scores.items()
                                   if len(scores) >= 3}
                
                if len(interviewer_means) > 1:
                    mean_of_means = statistics.mean(interviewer_means.values())
                    for interviewer, mean_score in interviewer_means.items():
                        deviation = abs(mean_score - mean_of_means)
                        if deviation > 0.5:  # More than half point deviation
                            interviewer_variations[interviewer] = {
                                "mean_score": round(mean_score, 2),
                                "deviation_from_average": round(deviation, 2),
                                "sample_size": len(interviewer_competency_scores[interviewer])
                            }
            
            competency_analysis[competency] = {
                "total_scores": len(competency_scores),
                "mean_score": round(statistics.mean(scores), 2),
                "score_variance": round(score_variance, 2),
                "interviewer_variations": interviewer_variations,
                "bias_detected": len(interviewer_variations) > 0
            }
        
        return competency_analysis
