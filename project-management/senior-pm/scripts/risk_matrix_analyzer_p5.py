# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from risk_matrix_analyzer_base import *  # noqa: F403,E402
# fmt: off
from risk_matrix_analyzer_p2 import Risk, RiskAnalysisResult  # noqa: E402,E501
from risk_matrix_analyzer_p3 import analyze_risk_categories, build_risk_matrix  # noqa: E402,E501
from risk_matrix_analyzer_p4 import analyze_mitigation_effectiveness, analyze_risk_trends, generate_risk_recommendations  # noqa: E402,E501
# fmt: on


def analyze_risks(data: Dict[str, Any]) -> RiskAnalysisResult:
    """Perform comprehensive risk analysis."""
    result = RiskAnalysisResult()
    
    try:
        # Parse risk data
        risk_records = data.get("risks", [])
        risks = [Risk(record) for record in risk_records]
        
        if not risks:
            raise ValueError("No risk data found")
        
        # Basic summary
        active_risks = [r for r in risks if r.is_active]
        result.summary = {
            "total_risks": len(risks),
            "active_risks": len(active_risks),
            "closed_risks": len(risks) - len(active_risks),
            "critical_risks": len([r for r in active_risks if r.risk_level == "critical"]),
            "high_risks": len([r for r in active_risks if r.risk_level == "high"]),
            "total_risk_exposure": sum(r.risk_score for r in active_risks),
            "average_risk_score": sum(r.risk_score for r in active_risks) / max(len(active_risks), 1),
            "overdue_risks": len([r for r in active_risks if r.is_overdue])
        }
        
        # Risk matrix analysis
        result.risk_matrix = build_risk_matrix(risks)
        
        # Category analysis
        result.category_analysis = analyze_risk_categories(risks)
        
        # Mitigation analysis
        result.mitigation_analysis = analyze_mitigation_effectiveness(risks)
        
        # Trend analysis (simplified without historical data)
        result.trend_analysis = analyze_risk_trends(risks, data.get("historical_data"))
        
        # Generate recommendations
        analysis_data = {
            "category_analysis": result.category_analysis,
            "mitigation_analysis": result.mitigation_analysis,
            "risk_matrix": result.risk_matrix
        }
        result.recommendations = generate_risk_recommendations(risks, analysis_data)
        
    except Exception as e:
        result.summary = {"error": str(e)}
    
    return result
