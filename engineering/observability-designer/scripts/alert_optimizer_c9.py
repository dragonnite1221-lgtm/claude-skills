# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from alert_optimizer_base import *  # noqa: F403,E402


class AlertOptimizerMixin9:
    def _generate_html_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate HTML report of analysis results."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Alert Configuration Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .critical {{ border-left: 5px solid #ff0000; }}
        .warning {{ border-left: 5px solid #ff9900; }}
        .info {{ border-left: 5px solid #0066cc; }}
        .success {{ border-left: 5px solid #00aa00; }}
        ul {{ margin: 10px 0; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Alert Configuration Analysis Report</h1>
        <p>Generated: {analysis_results['summary']['analysis_timestamp']}</p>
        <p>Total Alerts Analyzed: {analysis_results['summary']['total_alerts']}</p>
    </div>
    
    <div class="section critical">
        <h2>Overall Recommendations</h2>
        <ul>
        {''.join(f'<li>{rec}</li>' for rec in analysis_results['overall_recommendations'])}
        </ul>
    </div>
    
    <div class="section warning">
        <h2>Alert Fatigue Assessment</h2>
        <p><strong>Risk Level:</strong> {analysis_results['alert_fatigue_assessment']['risk_level'].upper()}</p>
        <p><strong>Risk Factors:</strong></p>
        <ul>
        {''.join(f'<li>{factor}</li>' for factor in analysis_results['alert_fatigue_assessment']['risk_factors'])}
        </ul>
    </div>
    
    <div class="section info">
        <h2>Noisy Alerts ({len(analysis_results['noisy_alerts'])})</h2>
        {''.join(f'<div><strong>{alert["alert_name"]}</strong> (Score: {alert["noise_score"]})<ul>{"".join(f"<li>{reason}</li>" for reason in alert["reasons"])}</ul></div>' 
                for alert in analysis_results['noisy_alerts'][:5])}
    </div>
    
    <div class="section info">
        <h2>Coverage Gaps</h2>
        <p><strong>Missing Categories:</strong> {', '.join(analysis_results['coverage_gaps']['missing_categories']) or 'None'}</p>
        <p><strong>Missing Golden Signals:</strong> {', '.join(analysis_results['coverage_gaps']['missing_golden_signals']) or 'None'}</p>
        <p><strong>Critical Gaps:</strong> {len(analysis_results['coverage_gaps']['critical_gaps'])}</p>
    </div>
    
</body>
</html>
        """
        return html
    def print_summary(self, analysis_results: Dict[str, Any]):
        """Print human-readable summary of analysis."""
        print(f"\n{'='*60}")
        print(f"ALERT CONFIGURATION ANALYSIS SUMMARY")
        print(f"{'='*60}")
        
        summary = analysis_results['summary']
        print(f"\nOverall Statistics:")
        print(f"  Total Alerts: {summary['total_alerts']}")
        print(f"  Analysis Date: {summary['analysis_timestamp']}")
        
        # Alert fatigue assessment
        fatigue = analysis_results['alert_fatigue_assessment']
        print(f"\nAlert Fatigue Risk: {fatigue['risk_level'].upper()}")
        if fatigue['risk_factors']:
            print(f"  Risk Factors:")
            for factor in fatigue['risk_factors']:
                print(f"    • {factor}")
        
        # Noisy alerts
        noisy = analysis_results['noisy_alerts']
        print(f"\nNoisy Alerts: {len(noisy)}")
        if noisy:
            print(f"  Top 3 Noisiest:")
            for alert in noisy[:3]:
                print(f"    • {alert['alert_name']} (Score: {alert['noise_score']})")
        
        # Coverage gaps
        gaps = analysis_results['coverage_gaps']
        print(f"\nMonitoring Coverage:")
        print(f"  Missing Categories: {len(gaps['missing_categories'])}")
        print(f"  Missing Golden Signals: {len(gaps['missing_golden_signals'])}")
        print(f"  Critical Gaps: {len(gaps['critical_gaps'])}")
        
        # Duplicates
        duplicates = analysis_results['duplicate_alerts']
        print(f"\nDuplicate Alerts: {len(duplicates)} groups")
        
        # Overall recommendations
        recommendations = analysis_results['overall_recommendations']
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n{'='*60}\n")
