# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402
# fmt: off
from qms_audit_checklist_p5 import ISO13485_CLAUSES, PROCESS_MAPPING, get_clause_checklist  # noqa: E402,E501
from qms_audit_checklist_p6 import format_checklist_text, get_process_checklist, get_system_audit_checklist  # noqa: E402,E501
from qms_audit_checklist_p7 import interactive_mode  # noqa: E402,E501
# fmt: on


def main():
    parser = argparse.ArgumentParser(
        description="Generate ISO 13485:2016 internal audit checklists",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python qms_audit_checklist.py --clause 7.3
  python qms_audit_checklist.py --process design-control
  python qms_audit_checklist.py --audit-type system --output json
  python qms_audit_checklist.py --list-processes
  python qms_audit_checklist.py --list-clauses
  python qms_audit_checklist.py --interactive
        """
    )

    parser.add_argument(
        "--clause",
        help="Generate checklist for specific clause (e.g., 7.3.1, 8.5.2)"
    )
    parser.add_argument(
        "--process",
        help="Generate checklist for process (e.g., design-control, capa)"
    )
    parser.add_argument(
        "--audit-type",
        choices=["clause", "process", "system"],
        help="Audit type for checklist generation"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--list-processes",
        action="store_true",
        help="List available QMS processes"
    )
    parser.add_argument(
        "--list-clauses",
        action="store_true",
        help="List all ISO 13485 clauses"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.list_processes:
        processes = sorted(PROCESS_MAPPING.keys())
        if args.output == "json":
            result = {p: PROCESS_MAPPING[p] for p in processes}
            print(json.dumps(result, indent=2))
        else:
            print("\nAvailable QMS Processes:")
            print("-" * 50)
            for p in processes:
                clauses = PROCESS_MAPPING[p]
                print(f"  {p}: {', '.join(clauses)}")
        return

    if args.list_clauses:
        if args.output == "json":
            result = {c: {"title": d["title"], "question_count": len(d["questions"])}
                     for c, d in sorted(ISO13485_CLAUSES.items())}
            print(json.dumps(result, indent=2))
        else:
            print("\nISO 13485:2016 Clauses:")
            print("-" * 50)
            for clause, data in sorted(ISO13485_CLAUSES.items()):
                print(f"  {clause}: {data['title']} ({len(data['questions'])} questions)")
        return

    checklist = None

    if args.clause:
        checklist = get_clause_checklist(args.clause)
    elif args.process:
        checklist = get_process_checklist(args.process)
    elif args.audit_type == "system":
        checklist = get_system_audit_checklist()
    else:
        parser.print_help()
        return

    if checklist:
        if args.output == "json":
            print(json.dumps(checklist, indent=2))
        else:
            print(format_checklist_text(checklist))
