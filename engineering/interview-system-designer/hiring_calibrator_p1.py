# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from hiring_calibrator_base import *  # noqa: F403,E402
from hiring_calibrator_p0 import format_human_readable  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="Analyze interview data for bias and calibration issues")
    parser.add_argument("--input", type=str, required=True, help="Input JSON file with interview results data")
    parser.add_argument("--analysis-type", type=str, choices=["comprehensive", "bias", "calibration", "interviewer", "scoring"], 
                       default="comprehensive", help="Type of analysis to perform")
    parser.add_argument("--competencies", type=str, help="Comma-separated list of competencies to focus on")
    parser.add_argument("--trend-analysis", action="store_true", help="Perform trend analysis over time")
    parser.add_argument("--period", type=str, choices=["daily", "weekly", "monthly", "quarterly"], 
                       default="monthly", help="Time period for trend analysis")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--format", choices=["json", "text", "both"], default="both", help="Output format")
    
    args = parser.parse_args()
    
    # Load input data
    try:
        with open(args.input, 'r') as f:
            interview_data = json.load(f)
        
        if not isinstance(interview_data, list):
            print("Error: Input data must be a JSON array of interview records")
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Initialize calibrator and run analysis
    calibrator = HiringCalibrator()
    
    competencies = args.competencies.split(',') if args.competencies else None
    
    try:
        results = calibrator.analyze_hiring_calibration(
            interview_data=interview_data,
            analysis_type=args.analysis_type,
            competencies=competencies,
            trend_analysis=args.trend_analysis,
            period=args.period
        )
        
        # Handle output
        if args.output:
            output_path = args.output
            json_path = output_path if output_path.endswith('.json') else f"{output_path}.json"
            text_path = output_path.replace('.json', '.txt') if output_path.endswith('.json') else f"{output_path}.txt"
        else:
            base_filename = f"calibration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            json_path = f"{base_filename}.json"
            text_path = f"{base_filename}.txt"
        
        # Write outputs
        if args.format in ["json", "both"]:
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"JSON report written to: {json_path}")
        
        if args.format in ["text", "both"]:
            with open(text_path, 'w') as f:
                f.write(format_human_readable(results))
            print(f"Text report written to: {text_path}")
        
        # Print summary
        print(f"\nCalibration Analysis Summary:")
        if "error" in results:
            print(f"Error: {results['error']}")
        else:
            health_score = results.get("calibration_health_score", {})
            print(f"Health Score: {health_score.get('overall_score', 0):.3f} ({health_score.get('health_category', 'Unknown').title()})")
            
            bias_score = results.get("bias_analysis", {}).get("overall_bias_score", 0)
            print(f"Bias Score: {bias_score:.3f} (Lower is better)")
            
            recommendations = results.get("recommendations", [])
            print(f"Recommendations Generated: {len(recommendations)}")
            
            if recommendations:
                print(f"Top Priority: {recommendations[0]['title']} ({recommendations[0]['priority'].title()})")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)
