# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent System Performance Evaluator")
    parser.add_argument("input_file", help="JSON file with execution logs")
    parser.add_argument("-o", "--output", help="Output file prefix (default: evaluation_report)")
    parser.add_argument("--format", choices=["json", "both"], default="both", 
                       help="Output format")
    parser.add_argument("--detailed", action="store_true", 
                       help="Include detailed analysis in output")
    
    args = parser.parse_args()
    
    try:
        # Load execution logs
        with open(args.input_file, 'r') as f:
            logs_data = json.load(f)
        
        # Parse logs
        evaluator = AgentEvaluator()
        logs = evaluator.parse_execution_logs(logs_data.get("execution_logs", []))
        
        if not logs:
            print("No valid execution logs found in input file", file=sys.stderr)
            sys.exit(1)
        
        # Generate evaluation report
        report = evaluator.generate_report(logs)
        
        # Prepare output
        output_data = asdict(report)
        
        # Output files
        output_prefix = args.output or "evaluation_report"
        
        if args.format in ["json", "both"]:
            with open(f"{output_prefix}.json", 'w') as f:
                json.dump(output_data, f, indent=2, default=str)
            print(f"JSON report written to {output_prefix}.json")
        
        if args.format == "both":
            # Generate separate detailed files
            
            # Performance summary
            summary_data = {
                "summary": report.summary,
                "system_metrics": asdict(report.system_metrics),
                "sla_compliance": report.sla_compliance
            }
            with open(f"{output_prefix}_summary.json", 'w') as f:
                json.dump(summary_data, f, indent=2, default=str)
            print(f"Summary report written to {output_prefix}_summary.json")
            
            # Recommendations
            recommendations_data = {
                "optimization_recommendations": [asdict(rec) for rec in report.optimization_recommendations],
                "bottleneck_analysis": [asdict(b) for b in report.bottleneck_analysis]
            }
            with open(f"{output_prefix}_recommendations.json", 'w') as f:
                json.dump(recommendations_data, f, indent=2)
            print(f"Recommendations written to {output_prefix}_recommendations.json")
            
            # Error analysis
            error_data = {
                "error_analysis": [asdict(e) for e in report.error_analysis],
                "error_summary": {
                    "total_errors": sum(e.count for e in report.error_analysis),
                    "high_impact_errors": len([e for e in report.error_analysis if e.impact_level == "high"])
                }
            }
            with open(f"{output_prefix}_errors.json", 'w') as f:
                json.dump(error_data, f, indent=2)
            print(f"Error analysis written to {output_prefix}_errors.json")
        
        # Print executive summary
        print(f"\n{'='*60}")
        print(f"AGENT SYSTEM EVALUATION REPORT")
        print(f"{'='*60}")
        print(f"Overall Health: {report.summary['overall_health'].upper()}")
        print(f"Total Tasks: {report.system_metrics.total_tasks}")
        print(f"Success Rate: {report.system_metrics.success_rate:.1%}")
        print(f"Average Duration: {report.system_metrics.average_duration_ms/1000:.1f}s")
        print(f"Total Cost: ${report.system_metrics.total_cost_usd:.2f}")
        print(f"Agents Analyzed: {len(report.agent_metrics)}")
        
        print(f"\nKey Findings:")
        for finding in report.summary['key_findings']:
            print(f"  • {finding}")
        
        print(f"\nTop Recommendations:")
        high_priority_recs = [r for r in report.optimization_recommendations if r.priority == "high"][:3]
        for i, rec in enumerate(high_priority_recs, 1):
            print(f"  {i}. {rec.title}")
        
        if report.summary['critical_issues'] > 0:
            print(f"\n⚠️  CRITICAL: {report.summary['critical_issues']} critical issues require immediate attention")
        
        print(f"\n📊 Detailed reports available in generated files")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
