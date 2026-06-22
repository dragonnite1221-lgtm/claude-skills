# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from stakeholder_mapper_base import *  # noqa: F403,E402
# fmt: off
from stakeholder_mapper_p1 import classify_stakeholder  # noqa: E402,E501
# fmt: on


def render_grid(stakeholders: List[Dict], width: int = 60) -> str:
    """
    Render a 2D influence vs alignment grid with stakeholder positions.
    Y-axis: Influence (top = high)
    X-axis: Alignment (left = low, right = high)
    """
    rows = 10
    cols = 20
    
    grid = [[' ' for _ in range(cols)] for _ in range(rows)]
    
    for s in stakeholders:
        influence = s["influence"]
        alignment = s["alignment"]
        
        # Map scores 1–10 to grid coordinates
        col = int((alignment - 1) / 9 * (cols - 1))
        row = rows - 1 - int((influence - 1) / 9 * (rows - 1))
        
        col = max(0, min(cols - 1, col))
        row = max(0, min(rows - 1, row))
        
        initial = s["name"][0].upper()
        if grid[row][col] == ' ':
            grid[row][col] = initial
        else:
            grid[row][col] = '+'  # Overlap
    
    lines = []
    lines.append("  STAKEHOLDER MAP  (Influence ↑  |  Alignment →)")
    lines.append("")
    lines.append(f"  HIGH  ┌{'─'*cols}┐")
    
    for i, row in enumerate(grid):
        if i == rows // 2:
            prefix = "  INFL "
        else:
            prefix = "       "
        lines.append(f"{prefix}│{''.join(row)}│")
    
    lines.append(f"   LOW  └{'─'*cols}┘")
    lines.append(f"         {'BLOCKER':<12}  {'SWING':<8}   CHAMPION")
    lines.append(f"         Low alignment              High alignment")
    lines.append("")
    
    # Legend
    lines.append("  Legend (initials):")
    for s in stakeholders:
        cls = classify_stakeholder(s["influence"], s["alignment"])
        lines.append(f"    {s['name'][0].upper()} = {s['name']} ({cls['symbol']} {cls['quadrant']})")
    
    return "\n".join(lines)
def hr(char="─", width=65):
    return char * width
