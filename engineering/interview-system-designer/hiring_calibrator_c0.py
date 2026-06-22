# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402


class HiringCalibratorMixin0:
    """Analyzes interview data for bias detection and calibration issues."""
    def __init__(self):
        self.bias_thresholds = self._init_bias_thresholds()
        self.calibration_standards = self._init_calibration_standards()
        self.demographic_categories = self._init_demographic_categories()
    def _init_bias_thresholds(self) -> Dict[str, float]:
        """Initialize statistical thresholds for bias detection."""
        return {
            "score_variance_threshold": 1.5,  # Standard deviations
            "pass_rate_difference_threshold": 0.15,  # 15% difference
            "interviewer_consistency_threshold": 0.8,  # Correlation coefficient
            "demographic_parity_threshold": 0.10,  # 10% difference
            "score_inflation_threshold": 0.3,  # 30% above historical average
            "score_deflation_threshold": 0.3,  # 30% below historical average
            "minimum_sample_size": 5  # Minimum candidates per analysis
        }
    def _init_calibration_standards(self) -> Dict[str, Dict]:
        """Initialize expected calibration standards."""
        return {
            "score_distribution": {
                "target_mean": 2.8,  # Expected average score (1-4 scale)
                "target_std": 0.9,   # Expected standard deviation
                "expected_distribution": {
                    "1": 0.10,  # 10% score 1 (does not meet)
                    "2": 0.25,  # 25% score 2 (partially meets)
                    "3": 0.45,  # 45% score 3 (meets expectations) 
                    "4": 0.20   # 20% score 4 (exceeds expectations)
                }
            },
            "interviewer_agreement": {
                "minimum_correlation": 0.70,  # Minimum correlation between interviewers
                "maximum_std_deviation": 0.8,  # Maximum std dev in scores for same candidate
                "agreement_threshold": 0.75   # % of time interviewers should agree within 1 point
            },
            "pass_rates": {
                "junior_level": 0.25,   # 25% pass rate for junior roles
                "mid_level": 0.20,      # 20% pass rate for mid roles
                "senior_level": 0.15,   # 15% pass rate for senior roles
                "staff_level": 0.10,    # 10% pass rate for staff+ roles
                "leadership": 0.12      # 12% pass rate for leadership roles
            }
        }
    def _init_demographic_categories(self) -> List[str]:
        """Initialize demographic categories to analyze for bias."""
        return [
            "gender", "ethnicity", "education_level", "previous_company_size",
            "years_experience", "university_tier", "geographic_location"
        ]
    def analyze_hiring_calibration(self, interview_data: List[Dict[str, Any]], 
                                  analysis_type: str = "comprehensive",
                                  competencies: Optional[List[str]] = None,
                                  trend_analysis: bool = False,
                                  period: str = "monthly") -> Dict[str, Any]:
        """Perform comprehensive hiring calibration analysis."""
        
        # Validate and preprocess data
        processed_data = self._preprocess_interview_data(interview_data)
        
        if len(processed_data) < self.bias_thresholds["minimum_sample_size"]:
            return {
                "error": "Insufficient data for analysis",
                "minimum_required": self.bias_thresholds["minimum_sample_size"],
                "actual_samples": len(processed_data)
            }
        
        # Perform different types of analysis based on request
        analysis_results = {
            "analysis_type": analysis_type,
            "data_summary": self._generate_data_summary(processed_data),
            "generated_at": datetime.now().isoformat()
        }
        
        if analysis_type in ["comprehensive", "bias"]:
            analysis_results["bias_analysis"] = self._analyze_bias_patterns(processed_data, competencies)
        
        if analysis_type in ["comprehensive", "calibration"]:
            analysis_results["calibration_analysis"] = self._analyze_calibration_consistency(processed_data, competencies)
        
        if analysis_type in ["comprehensive", "interviewer"]:
            analysis_results["interviewer_analysis"] = self._analyze_interviewer_bias(processed_data)
        
        if analysis_type in ["comprehensive", "scoring"]:
            analysis_results["scoring_analysis"] = self._analyze_scoring_patterns(processed_data, competencies)
        
        if trend_analysis:
            analysis_results["trend_analysis"] = self._analyze_trends_over_time(processed_data, period)
        
        # Generate recommendations
        analysis_results["recommendations"] = self._generate_recommendations(analysis_results)
        
        # Calculate overall calibration health score
        analysis_results["calibration_health_score"] = self._calculate_health_score(analysis_results)
        
        return analysis_results
    def _preprocess_interview_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and validate interview data."""
        processed_data = []
        
        for record in raw_data:
            if self._validate_interview_record(record):
                processed_record = self._standardize_record(record)
                processed_data.append(processed_record)
        
        return processed_data
