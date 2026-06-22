# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from comp_benchmarker_base import *  # noqa: F403,E402
# fmt: off
from comp_benchmarker_p1 import CompRoster  # noqa: E402,E501
from comp_benchmarker_p2 import analyze_employee  # noqa: E402,E501
# fmt: on


def export_csv(roster: CompRoster) -> str:
    analyses = [analyze_employee(e, roster) for e in roster.employees]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Role", "Level", "Function", "Zone",
                     "Base", "Bonus Target", "Equity Annual", "Benefits", "Total Comp",
                     "Compa Ratio", "Band Position", "vs Market P50 %",
                     "Performance", "Tenure Years", "Last Raise (mo)",
                     "Gender", "Ethnicity", "Critical Flags", "High Flags"])
    for a, e in zip(analyses, roster.employees):
        critical_flags = "; ".join(msg for sev, msg in a["flags"] if sev == "CRITICAL")
        high_flags = "; ".join(msg for sev, msg in a["flags"] if sev == "HIGH")
        writer.writerow([a["id"], a["name"], a["role"], a["level"], a["function"], a["zone"],
                         a["base"], a["bonus_target"], a["equity_annual"], a["benefits"], a["total_comp"],
                         a["compa_ratio"], a["band_position"], a["vs_market_p50"],
                         a["performance"], a["tenure_years"], a["last_raise_months"],
                         e.gender, e.ethnicity, critical_flags, high_flags])
    return output.getvalue()
