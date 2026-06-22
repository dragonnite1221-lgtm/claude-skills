# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from decision_matrix_scorer_base import *  # noqa: F403,E402
# fmt: off
from decision_matrix_scorer_p2 import print_report  # noqa: E402,E501
from decision_matrix_scorer_p3 import interactive_mode  # noqa: E402,E501
# fmt: on


SAMPLE_DATA = {
    "decision": "How to extend runway: Cut costs vs. Raise bridge vs. Accelerate revenue",
    "criteria": [
        {
            "name": "Speed to impact",
            "weight": 0.25,
            "description": "How quickly does this improve our situation?"
        },
        {
            "name": "Execution risk",
            "weight": 0.30,
            "description": "How likely is this to actually work? (10=low risk)"
        },
        {
            "name": "Team morale impact",
            "weight": 0.20,
            "description": "Effect on team (10=positive, 1=very negative)"
        },
        {
            "name": "Runway extension",
            "weight": 0.15,
            "description": "How much runway does this actually buy?"
        },
        {
            "name": "Strategic fit",
            "weight": 0.10,
            "description": "Does this align with where we want to go?"
        }
    ],
    "options": [
        {
            "name": "Cost cut 25%",
            "description": "Reduce headcount and discretionary spend by 25%",
            "scores": {
                "Speed to impact": 9,
                "Execution risk": 8,
                "Team morale impact": 2,
                "Runway extension": 8,
                "Strategic fit": 5
            }
        },
        {
            "name": "Bridge from investors",
            "description": "Raise $500K bridge from existing investors to hit next milestone",
            "scores": {
                "Speed to impact": 6,
                "Execution risk": 5,
                "Team morale impact": 7,
                "Runway extension": 6,
                "Strategic fit": 7
            }
        },
        {
            "name": "Accelerate revenue",
            "description": "Push 3 enterprise deals hard, offer incentives for Q4 close",
            "scores": {
                "Speed to impact": 4,
                "Execution risk": 3,
                "Team morale impact": 9,
                "Runway extension": 9,
                "Strategic fit": 10
            }
        },
        {
            "name": "Hybrid: cut 15% + bridge",
            "description": "Smaller cuts combined with a modest bridge round",
            "scores": {
                "Speed to impact": 7,
                "Execution risk": 6,
                "Team morale impact": 5,
                "Runway extension": 7,
                "Strategic fit": 6
            }
        }
    ]
}
def main():
    parser = argparse.ArgumentParser(
        description="Decision Matrix Scorer — weighted analysis with sensitivity testing"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode: enter decision data manually"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Load decision data from JSON file"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Show sample data structure and exit"
    )
    
    args = parser.parse_args()
    
    if args.sample:
        print(json.dumps(SAMPLE_DATA, indent=2))
        return
    
    if args.interactive:
        interactive_mode()
        return
    
    if args.file:
        try:
            with open(args.file) as f:
                data = json.load(f)
            print_report(data)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{args.file}': {e}")
            sys.exit(1)
        return
    
    # Default: run sample data
    print()
    print("Running with sample data. Use --interactive for custom input or --file for JSON.")
    print_report(SAMPLE_DATA)
