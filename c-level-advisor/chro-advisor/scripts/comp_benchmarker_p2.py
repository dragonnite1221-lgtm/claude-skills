# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comp_benchmarker_base import *  # noqa: F403,E402
# fmt: off
from comp_benchmarker_p1 import CompRoster, Employee, annualized_equity_value, band_position, compa_ratio, find_band, total_comp  # noqa: E402,E501
# fmt: on


def analyze_employee(emp: Employee, roster: CompRoster) -> dict:
    band = find_band(roster, emp.level, emp.function, emp.location_zone)
    result = {
        "id": emp.id,
        "name": emp.name,
        "role": emp.role,
        "level": emp.level,
        "function": emp.function,
        "zone": emp.location_zone,
        "base": emp.base_salary,
        "bonus_target": int(emp.base_salary * emp.bonus_target_pct),
        "equity_annual": annualized_equity_value(emp),
        "benefits": emp.benefits_annual,
        "total_comp": total_comp(emp),
        "performance": emp.performance_rating,
        "tenure_years": emp.tenure_years,
        "last_raise_months": emp.last_raise_months_ago,
        "band": band,
        "compa_ratio": None,
        "band_position": None,
        "vs_market_p50": None,
        "flags": [],
    }

    if band:
        cr = compa_ratio(emp.base_salary, band.band_mid)
        bp = band_position(emp.base_salary, band.band_min, band.band_max)
        result["compa_ratio"] = round(cr, 3)
        result["band_position"] = round(bp, 3)
        result["vs_market_p50"] = round((emp.base_salary - band.market_p50) / band.market_p50 * 100, 1)

        # Flags
        if emp.base_salary < band.band_min:
            result["flags"].append(("CRITICAL", "Base below band minimum — immediate attrition risk"))
        elif cr < 0.88:
            result["flags"].append(("HIGH", f"Compa-ratio {cr:.2f} — significantly below midpoint"))
        elif cr < 0.93:
            result["flags"].append(("MEDIUM", f"Compa-ratio {cr:.2f} — below target zone (0.95–1.05)"))

        if emp.base_salary > band.band_max:
            result["flags"].append(("HIGH", "Base above band maximum — review for promotion or band update"))

        if emp.performance_rating >= 4 and cr < 0.95:
            result["flags"].append(("HIGH", f"High performer (rating {emp.performance_rating}) underpaid — flight risk"))

        if emp.last_raise_months_ago > 18:
            result["flags"].append(("MEDIUM", f"No raise in {emp.last_raise_months_ago} months — review due"))

        if emp.equity_vest_years_remaining < 1.0 and (emp.last_equity_refresh_months_ago is None or emp.last_equity_refresh_months_ago > 24):
            result["flags"].append(("HIGH", "Equity nearly fully vested with no refresh — retention hook gone"))

    else:
        result["flags"].append(("INFO", "No band found for this level/function/zone"))

    return result
def pay_equity_audit(analyses: list[dict], employees: list[Employee]) -> dict:
    """Simple pay equity analysis by gender and ethnicity."""
    emp_by_id = {e.id: e for e in employees}

    def group_stats(group_key_fn):
        groups: dict[str, list[float]] = {}
        for a in analyses:
            if a["compa_ratio"] is None:
                continue
            emp = emp_by_id.get(a["id"])
            if not emp:
                continue
            key = group_key_fn(emp)
            if key not in groups:
                groups[key] = []
            groups[key].append(a["compa_ratio"])
        return {k: {"n": len(v), "avg_cr": round(sum(v)/len(v), 3), "min_cr": round(min(v), 3), "max_cr": round(max(v), 3)}
                for k, v in groups.items() if v}

    gender_stats = group_stats(lambda e: e.gender)
    ethnicity_stats = group_stats(lambda e: e.ethnicity)

    # Compute gap vs. the largest group
    def compute_gap(stats: dict) -> dict[str, float]:
        if not stats:
            return {}
        largest = max(stats.items(), key=lambda x: x[1]["n"])
        ref_cr = largest[1]["avg_cr"]
        return {k: round((v["avg_cr"] - ref_cr) / ref_cr * 100, 1) for k, v in stats.items()}

    gender_gaps = compute_gap(gender_stats)
    ethnicity_gaps = compute_gap(ethnicity_stats)

    return {
        "gender": gender_stats,
        "gender_gaps_pct": gender_gaps,
        "ethnicity": ethnicity_stats,
        "ethnicity_gaps_pct": ethnicity_gaps,
    }
def compa_ratio_distribution(analyses: list[dict]) -> dict:
    crs = [a["compa_ratio"] for a in analyses if a["compa_ratio"] is not None]
    if not crs:
        return {}
    buckets = {
        "< 0.85 (below band)": 0,
        "0.85–0.94 (developing)": 0,
        "0.95–1.05 (target zone)": 0,
        "1.06–1.15 (senior in role)": 0,
        "> 1.15 (above band)": 0,
    }
    for cr in crs:
        if cr < 0.85:
            buckets["< 0.85 (below band)"] += 1
        elif cr < 0.95:
            buckets["0.85–0.94 (developing)"] += 1
        elif cr <= 1.05:
            buckets["0.95–1.05 (target zone)"] += 1
        elif cr <= 1.15:
            buckets["1.06–1.15 (senior in role)"] += 1
        else:
            buckets["> 1.15 (above band)"] += 1
    avg = sum(crs) / len(crs)
    return {"distribution": buckets, "avg_compa_ratio": round(avg, 3), "n": len(crs)}
def fmt(n) -> str:
    return f"${int(n):,.0f}"
def bar(value: float, width: int = 20) -> str:
    filled = min(width, max(0, int(value * width)))
    return "█" * filled + "░" * (width - filled)
