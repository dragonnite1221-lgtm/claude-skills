# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin6:
    def _analyze_scoring_patterns(self, data: List[Dict[str, Any]], 
                                target_competencies: Optional[List[str]]) -> Dict[str, Any]:
        """Analyze overall scoring patterns and distributions."""
        
        # Overall score distribution
        all_individual_scores = []
        all_average_scores = []
        score_distribution = defaultdict(int)
        
        for record in data:
            avg_score = record["average_score"]
            all_average_scores.append(avg_score)
            
            for competency, score in record["scores"].items():
                if not target_competencies or competency in target_competencies:
                    all_individual_scores.append(score)
                    score_distribution[str(int(score))] += 1
        
        # Calculate distribution percentages
        total_scores = sum(score_distribution.values())
        score_percentages = {score: count/total_scores for score, count in score_distribution.items()}
        
        # Compare against expected distribution
        expected_dist = self.calibration_standards["score_distribution"]["expected_distribution"]
        distribution_analysis = {}
        
        for score in ["1", "2", "3", "4"]:
            expected_pct = expected_dist.get(score, 0)
            actual_pct = score_percentages.get(score, 0)
            difference = actual_pct - expected_pct
            
            distribution_analysis[score] = {
                "expected_percentage": expected_pct,
                "actual_percentage": round(actual_pct, 3),
                "difference": round(difference, 3),
                "significant_deviation": abs(difference) > 0.05  # 5% threshold
            }
        
        # Calculate scoring statistics
        mean_score = statistics.mean(all_individual_scores) if all_individual_scores else 0
        std_score = statistics.stdev(all_individual_scores) if len(all_individual_scores) > 1 else 0
        
        target_mean = self.calibration_standards["score_distribution"]["target_mean"]
        target_std = self.calibration_standards["score_distribution"]["target_std"]
        
        # Analyze pass rates by level
        level_pass_rates = {}
        level_groups = defaultdict(list)
        
        for record in data:
            level = record.get("normalized_level", "unknown")
            level_groups[level].append(record["hire_decision"])
        
        for level, decisions in level_groups.items():
            if len(decisions) >= self.bias_thresholds["minimum_sample_size"]:
                pass_rate = sum(decisions) / len(decisions)
                expected_rate = self.calibration_standards["pass_rates"].get(f"{level}_level", 0.15)
                
                level_pass_rates[level] = {
                    "actual_pass_rate": round(pass_rate, 3),
                    "expected_pass_rate": expected_rate,
                    "difference": round(pass_rate - expected_rate, 3),
                    "sample_size": len(decisions)
                }
        
        return {
            "score_statistics": {
                "mean_score": round(mean_score, 2),
                "std_score": round(std_score, 2),
                "target_mean": target_mean,
                "target_std": target_std,
                "mean_deviation": round(abs(mean_score - target_mean), 2),
                "std_deviation": round(abs(std_score - target_std), 2)
            },
            "score_distribution": distribution_analysis,
            "level_pass_rates": level_pass_rates,
            "overall_assessment": self._assess_scoring_health(distribution_analysis, mean_score, target_mean)
        }
