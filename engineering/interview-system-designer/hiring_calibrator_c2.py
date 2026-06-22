# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin2:
    def _analyze_bias_patterns(self, data: List[Dict[str, Any]], 
                              target_competencies: Optional[List[str]]) -> Dict[str, Any]:
        """Analyze potential bias patterns in interview decisions."""
        bias_analysis = {
            "demographic_bias": {},
            "interviewer_bias": {},
            "competency_bias": {},
            "overall_bias_score": 0
        }
        
        # Analyze demographic bias
        for demographic in self.demographic_categories:
            if all(record.get(demographic) == "unknown" for record in data):
                continue
                
            demographic_analysis = self._analyze_demographic_bias(data, demographic)
            if demographic_analysis["bias_detected"]:
                bias_analysis["demographic_bias"][demographic] = demographic_analysis
        
        # Analyze interviewer bias
        bias_analysis["interviewer_bias"] = self._analyze_interviewer_bias(data)
        
        # Analyze competency bias if specified
        if target_competencies:
            bias_analysis["competency_bias"] = self._analyze_competency_bias(data, target_competencies)
        
        # Calculate overall bias score
        bias_analysis["overall_bias_score"] = self._calculate_bias_score(bias_analysis)
        
        return bias_analysis
    def _analyze_demographic_bias(self, data: List[Dict[str, Any]], 
                                 demographic: str) -> Dict[str, Any]:
        """Analyze bias for a specific demographic category."""
        # Group data by demographic values
        demographic_groups = defaultdict(list)
        for record in data:
            demo_value = record.get(demographic, "unknown")
            if demo_value != "unknown":
                demographic_groups[demo_value].append(record)
        
        if len(demographic_groups) < 2:
            return {"bias_detected": False, "reason": "insufficient_groups"}
        
        # Calculate statistics for each group
        group_stats = {}
        for group, records in demographic_groups.items():
            if len(records) >= self.bias_thresholds["minimum_sample_size"]:
                scores = [r["average_score"] for r in records]
                hire_rate = sum(r["hire_decision"] for r in records) / len(records)
                
                group_stats[group] = {
                    "count": len(records),
                    "mean_score": statistics.mean(scores),
                    "hire_rate": hire_rate,
                    "std_score": statistics.stdev(scores) if len(scores) > 1 else 0
                }
        
        if len(group_stats) < 2:
            return {"bias_detected": False, "reason": "insufficient_sample_sizes"}
        
        # Detect statistical differences
        bias_detected = False
        bias_details = {}
        
        # Check for significant differences in hire rates
        hire_rates = [stats["hire_rate"] for stats in group_stats.values()]
        max_hire_rate_diff = max(hire_rates) - min(hire_rates)
        
        if max_hire_rate_diff > self.bias_thresholds["demographic_parity_threshold"]:
            bias_detected = True
            bias_details["hire_rate_disparity"] = {
                "max_difference": round(max_hire_rate_diff, 3),
                "threshold": self.bias_thresholds["demographic_parity_threshold"],
                "group_stats": group_stats
            }
        
        # Check for significant differences in scoring
        mean_scores = [stats["mean_score"] for stats in group_stats.values()]
        max_score_diff = max(mean_scores) - min(mean_scores)
        
        if max_score_diff > 0.5:  # Half point difference threshold
            bias_detected = True
            bias_details["scoring_disparity"] = {
                "max_difference": round(max_score_diff, 3),
                "group_stats": group_stats
            }
        
        return {
            "bias_detected": bias_detected,
            "demographic": demographic,
            "group_statistics": group_stats,
            "bias_details": bias_details,
            "recommendation": self._generate_demographic_bias_recommendation(demographic, bias_details) if bias_detected else None
        }
