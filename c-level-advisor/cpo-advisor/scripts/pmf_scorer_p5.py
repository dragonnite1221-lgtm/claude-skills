# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from pmf_scorer_base import *  # noqa: F403,E402
# fmt: off
from pmf_scorer_p1 import DIMENSION_WEIGHTS, THRESHOLDS, sample_data  # noqa: E402,E501
from pmf_scorer_p2 import score_engagement, score_retention  # noqa: E402,E501
from pmf_scorer_p3 import pmf_status, score_growth, score_satisfaction  # noqa: E402,E501
from pmf_scorer_p4 import render_report  # noqa: E402,E501
# fmt: on


def run(data: dict) -> dict:
    """
    Score PMF from input data dict.
    Returns dict with overall score, dimension scores, and findings.
    """
    model = data.get("business_model", "b2b_saas")
    thresholds = THRESHOLDS.get(model, THRESHOLDS["b2b_saas"])

    dim_scores = {}
    dim_findings = {}

    ret_score, ret_findings = score_retention(data, thresholds)
    dim_scores["retention"] = ret_score
    dim_findings["retention"] = ret_findings

    eng_score, eng_findings = score_engagement(data, thresholds)
    dim_scores["engagement"] = eng_score
    dim_findings["engagement"] = eng_findings

    sat_score, sat_findings = score_satisfaction(data, thresholds)
    dim_scores["satisfaction"] = sat_score
    dim_findings["satisfaction"] = sat_findings

    grow_score, grow_findings = score_growth(data, thresholds)
    dim_scores["growth"] = grow_score
    dim_findings["growth"] = grow_findings

    overall = sum(
        dim_scores[dim] * weight
        for dim, weight in DIMENSION_WEIGHTS.items()
    )

    return {
        "overall": overall,
        "dim_scores": dim_scores,
        "dim_findings": dim_findings,
        "status": pmf_status(overall)[0],
    }
def main():
    parser = argparse.ArgumentParser(
        description="PMF Scorer — Multi-dimensional Product-Market Fit analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="JSON file with your product data (default: built-in sample data)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of formatted report",
    )
    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No input file provided — running with sample data.\n")
        data = sample_data()

    result = run(data)

    if args.json:
        output = {
            "product_name": data.get("product_name"),
            "business_model": data.get("business_model"),
            "overall_score": round(result["overall"], 4),
            "overall_pct": f"{result['overall']:.0%}",
            "status": result["status"],
            "dimensions": {
                dim: {
                    "score": round(result["dim_scores"][dim], 4),
                    "pct": f"{result['dim_scores'][dim]:.0%}",
                    "weight": f"{DIMENSION_WEIGHTS[dim]:.0%}",
                    "findings": result["dim_findings"][dim],
                }
                for dim in DIMENSION_WEIGHTS
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(render_report(data, result["dim_scores"], result["dim_findings"], result["overall"]))
