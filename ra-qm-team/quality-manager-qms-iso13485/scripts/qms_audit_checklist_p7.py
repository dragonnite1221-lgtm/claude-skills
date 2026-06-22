# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from qms_audit_checklist_base import *  # noqa: F403,E402
# fmt: off
from qms_audit_checklist_p5 import ISO13485_CLAUSES, PROCESS_MAPPING, get_clause_checklist  # noqa: E402,E501
from qms_audit_checklist_p6 import format_checklist_text, get_process_checklist, get_system_audit_checklist  # noqa: E402,E501
# fmt: on


def interactive_mode():
    """Run interactive audit checklist generator."""
    print("\n" + "=" * 50)
    print("QMS INTERNAL AUDIT CHECKLIST GENERATOR")
    print("=" * 50)

    print("\nSelect audit type:")
    print("1. Clause-specific audit")
    print("2. Process audit")
    print("3. Full system audit")
    print("4. List available processes")
    print("5. List all clauses")
    print("6. Exit")

    choice = input("\nEnter choice (1-6): ").strip()

    if choice == "1":
        print("\nAvailable clause sections:")
        print("  4.x - Quality Management System")
        print("  5.x - Management Responsibility")
        print("  6.x - Resource Management")
        print("  7.x - Product Realization")
        print("  8.x - Measurement, Analysis, Improvement")

        clause = input("\nEnter clause number (e.g., 7.3.1): ").strip()
        checklist = get_clause_checklist(clause)
        print(format_checklist_text(checklist))

    elif choice == "2":
        processes = sorted(PROCESS_MAPPING.keys())
        print("\nAvailable processes:")
        for i, p in enumerate(processes, 1):
            clauses = PROCESS_MAPPING[p]
            print(f"  {i}. {p} (clauses: {', '.join(clauses)})")

        process = input("\nEnter process name: ").strip().lower()
        checklist = get_process_checklist(process)
        print(format_checklist_text(checklist))

    elif choice == "3":
        print("\nGenerating full system audit checklist...")
        checklist = get_system_audit_checklist()
        print(format_checklist_text(checklist))

    elif choice == "4":
        processes = sorted(PROCESS_MAPPING.keys())
        print("\nAvailable QMS Processes:")
        print("-" * 50)
        for p in processes:
            clauses = PROCESS_MAPPING[p]
            print(f"  {p}")
            print(f"    Clauses: {', '.join(clauses)}")

    elif choice == "5":
        print("\nISO 13485:2016 Clauses:")
        print("-" * 50)
        for clause, data in sorted(ISO13485_CLAUSES.items()):
            print(f"  {clause}: {data['title']} ({len(data['questions'])} questions)")

    elif choice == "6":
        print("Exiting.")
        return

    else:
        print("Invalid choice.")
