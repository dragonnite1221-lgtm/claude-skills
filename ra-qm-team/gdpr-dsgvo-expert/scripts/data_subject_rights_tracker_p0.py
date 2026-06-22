# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_subject_rights_tracker_base import *  # noqa: F403,E402


def main():
    parser = argparse.ArgumentParser(
        description="Track and manage data subject rights requests"
    )
    parser.add_argument(
        "--data-file",
        default="dsr_requests.json",
        help="Path to requests data file (default: dsr_requests.json)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add new request")
    add_parser.add_argument("--type", "-t", required=True, choices=RIGHTS_TYPES.keys())
    add_parser.add_argument("--subject", "-s", required=True, help="Subject name")
    add_parser.add_argument("--email", "-e", required=True, help="Subject email")
    add_parser.add_argument("--details", "-d", default="", help="Request details")

    # List command
    list_parser = subparsers.add_parser("list", help="List requests")
    list_parser.add_argument("--status", choices=STATUSES.keys(), help="Filter by status")
    list_parser.add_argument("--overdue", action="store_true", help="Show only overdue")
    list_parser.add_argument("--json", action="store_true", help="JSON output")

    # Status command
    status_parser = subparsers.add_parser("status", help="Get/update request status")
    status_parser.add_argument("--id", required=True, help="Request ID")
    status_parser.add_argument("--update", choices=STATUSES.keys(), help="Update status")
    status_parser.add_argument("--note", default="", help="Add note")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate compliance report")
    report_parser.add_argument("--output", "-o", help="Output file")

    # Template command
    template_parser = subparsers.add_parser("template", help="Generate response template")
    template_parser.add_argument("--id", required=True, help="Request ID")

    # Types command
    subparsers.add_parser("types", help="List available request types")

    args = parser.parse_args()

    tracker = RightsTracker(args.data_file)

    if args.command == "add":
        request = tracker.add_request(
            args.type, args.subject, args.email, args.details
        )
        print(f"Request created: {request['id']}")
        print(f"Type: {request['right_name']} ({request['article']})")
        print(f"Deadline: {request['dates']['deadline'][:10]}")

    elif args.command == "list":
        requests = tracker.list_requests(args.status, args.overdue)
        if args.json:
            print(json.dumps(requests, indent=2))
        else:
            if not requests:
                print("No requests found.")
                return
            print(f"{'ID':<20} {'Type':<15} {'Subject':<20} {'Status':<15} {'Deadline':<12} {'Overdue'}")
            print("-" * 95)
            for req in requests:
                overdue_flag = "YES" if req.get("is_overdue") else ""
                print(f"{req['id']:<20} {req['type']:<15} {req['subject']['name'][:20]:<20} {req['status']:<15} {req['dates']['deadline'][:10]:<12} {overdue_flag}")

    elif args.command == "status":
        if args.update:
            req = tracker.update_status(args.id, args.update, args.note)
            if req:
                print(f"Updated {args.id} to status: {args.update}")
            else:
                print(f"Request not found: {args.id}")
        else:
            req = tracker.get_request(args.id)
            if req:
                print(json.dumps(req, indent=2))
            else:
                print(f"Request not found: {args.id}")

    elif args.command == "report":
        report = tracker.generate_report()
        output = json.dumps(report, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Report written to {args.output}")
        else:
            print(output)

    elif args.command == "template":
        template = tracker.generate_response_template(args.id)
        if template:
            print(template)
        else:
            print(f"Request not found: {args.id}")

    elif args.command == "types":
        print("Available Request Types:")
        print("-" * 60)
        for key, info in RIGHTS_TYPES.items():
            print(f"\n{key} ({info['article']})")
            print(f"  {info['name']}")
            print(f"  Deadline: {info['deadline_days']} days")

    else:
        parser.print_help()
