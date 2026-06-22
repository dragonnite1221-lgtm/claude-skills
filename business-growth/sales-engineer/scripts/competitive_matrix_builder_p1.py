# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitive_matrix_builder_base import *  # noqa: F403,E402


FEATURE_SCORES: dict[str, int] = {
    "full": 3,
    "partial": 2,
    "limited": 1,
    "none": 0,
}
FEATURE_LABELS: dict[int, str] = {
    3: "Full",
    2: "Partial",
    1: "Limited",
    0: "None",
}
def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator
def load_competitive_data(filepath: str) -> dict[str, Any]:
    """Load and validate competitive data from a JSON file.

    Args:
        filepath: Path to the JSON file containing competitive data.

    Returns:
        Parsed competitive data dictionary.

    Raises:
        SystemExit: If the file cannot be read or parsed.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)

    if "categories" not in data:
        print("Error: JSON must contain a 'categories' array.", file=sys.stderr)
        sys.exit(1)

    if "our_product" not in data:
        print("Error: JSON must contain 'our_product' name.", file=sys.stderr)
        sys.exit(1)

    if "competitors" not in data or not data["competitors"]:
        print("Error: JSON must contain a non-empty 'competitors' array.", file=sys.stderr)
        sys.exit(1)

    return data
def normalize_score(score_value: Any) -> int:
    """Normalize a score value to an integer.

    Args:
        score_value: Score as string label or integer.

    Returns:
        Normalized integer score (0-3).
    """
    if isinstance(score_value, str):
        return FEATURE_SCORES.get(score_value.lower(), 0)
    if isinstance(score_value, (int, float)):
        return max(0, min(3, int(score_value)))
    return 0
