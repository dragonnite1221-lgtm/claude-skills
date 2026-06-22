# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin12:
    def _analyze_single_interviewer_consistency(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consistency for single-interviewer candidates."""
        # Look at consistency within individual interviewers
        interviewer_scores = defaultdict(list)
        
        for record in data:
            interviewer_scores[record["interviewer_id"]].extend(record["scores"].values())
        
        consistency_analysis = {}
        for interviewer, scores in interviewer_scores.items():
            if len(scores) >= 10:  # Need sufficient data
                consistency_analysis[interviewer] = {
                    "mean_score": round(statistics.mean(scores), 2),
                    "std_score": round(statistics.stdev(scores), 2),
                    "coefficient_of_variation": round(statistics.stdev(scores) / statistics.mean(scores), 2),
                    "total_scores": len(scores)
                }
        
        return consistency_analysis
