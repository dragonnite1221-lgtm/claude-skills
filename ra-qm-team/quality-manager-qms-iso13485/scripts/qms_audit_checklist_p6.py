# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402
# fmt: off
from qms_audit_checklist_p5 import ISO13485_CLAUSES, PROCESS_MAPPING  # noqa: E402,E501
# fmt: on


def get_process_checklist(process: str) -> dict:
    """Get audit checklist for a specific process."""
    if process not in PROCESS_MAPPING:
        available = ", ".join(sorted(PROCESS_MAPPING.keys()))
        return {"error": f"Process '{process}' not found. Available: {available}"}

    clauses = PROCESS_MAPPING[process]
    questions = []

    for clause in clauses:
        if clause in ISO13485_CLAUSES:
            clause_data = ISO13485_CLAUSES[clause]
            for q in clause_data["questions"]:
                questions.append({
                    "clause": clause,
                    "clause_title": clause_data["title"],
                    "question": q
                })

    return {
        "process": process,
        "clauses_covered": clauses,
        "questions": questions,
        "question_count": len(questions)
    }
def get_system_audit_checklist() -> dict:
    """Get complete system audit checklist covering all clauses."""
    all_questions = []

    for clause, data in sorted(ISO13485_CLAUSES.items()):
        for q in data["questions"]:
            all_questions.append({
                "clause": clause,
                "clause_title": data["title"],
                "question": q
            })

    return {
        "audit_type": "system",
        "clauses_covered": list(ISO13485_CLAUSES.keys()),
        "questions": all_questions,
        "question_count": len(all_questions)
    }
def format_checklist_text(checklist: dict) -> str:
    """Format checklist for text output."""
    lines = []

    if "error" in checklist:
        return f"Error: {checklist['error']}"

    lines.append("=" * 70)
    lines.append("ISO 13485:2016 INTERNAL AUDIT CHECKLIST")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    if "clause" in checklist:
        lines.append(f"\nClause: {checklist['clause']} - {checklist['title']}")
        lines.append("-" * 50)
        for i, q in enumerate(checklist["questions"], 1):
            lines.append(f"\n{i}. {q}")
            lines.append("   [ ] C  [ ] NC  [ ] OBS  [ ] N/A")
            lines.append("   Evidence: _________________________________")
            lines.append("   Notes: ____________________________________")

    elif "process" in checklist:
        lines.append(f"\nProcess: {checklist['process'].replace('-', ' ').title()}")
        lines.append(f"Clauses Covered: {', '.join(checklist['clauses_covered'])}")
        lines.append("-" * 50)

        current_clause = None
        item_num = 1
        for q in checklist["questions"]:
            if q["clause"] != current_clause:
                current_clause = q["clause"]
                lines.append(f"\n--- {q['clause']} {q['clause_title']} ---")

            lines.append(f"\n{item_num}. {q['question']}")
            lines.append("   [ ] C  [ ] NC  [ ] OBS  [ ] N/A")
            lines.append("   Evidence: _________________________________")
            lines.append("   Notes: ____________________________________")
            item_num += 1

    elif "audit_type" in checklist:
        lines.append(f"\nAudit Type: Full System Audit")
        lines.append(f"Total Clauses: {len(checklist['clauses_covered'])}")
        lines.append("-" * 50)

        current_clause = None
        item_num = 1
        for q in checklist["questions"]:
            if q["clause"] != current_clause:
                current_clause = q["clause"]
                lines.append(f"\n{'=' * 40}")
                lines.append(f"CLAUSE {q['clause']}: {q['clause_title']}")
                lines.append("=" * 40)

            lines.append(f"\n{item_num}. {q['question']}")
            lines.append("   [ ] C  [ ] NC  [ ] OBS  [ ] N/A")
            lines.append("   Evidence: _________________________________")
            item_num += 1

    lines.append("\n" + "=" * 70)
    lines.append(f"Total Questions: {checklist['question_count']}")
    lines.append("")
    lines.append("Legend: C=Conforming, NC=Nonconforming, OBS=Observation, N/A=Not Applicable")
    lines.append("=" * 70)

    return "\n".join(lines)
