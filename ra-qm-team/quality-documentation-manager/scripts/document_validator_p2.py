# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402
from document_validator_p0 import Document, format_text_output  # noqa: F401,E501
from document_validator_p1 import interactive_mode  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(
        description="Quality Documentation Validator"
    )
    parser.add_argument(
        "--doc",
        type=str,
        help="JSON file with document metadata"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Generate sample document JSON"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if args.sample:
        sample = {
            "number": "SOP-02-001",
            "title": "Document Control Procedure",
            "doc_type": "SOP",
            "revision": "03",
            "status": "Effective",
            "effective_date": "2024-01-15",
            "review_date": "2025-01-15",
            "author": "J. Smith",
            "approver": "M. Jones",
            "approval_date": "2024-01-10",
            "change_history": [
                {"revision": "01", "date": "2022-01-01", "description": "Initial release"},
                {"revision": "02", "date": "2023-01-15", "description": "Updated approval workflow"},
                {"revision": "03", "date": "2024-01-15", "description": "Added electronic signature requirements"}
            ],
            "has_audit_trail": True,
            "has_electronic_signature": True,
            "signature_components": 2
        }
        print(json.dumps(sample, indent=2))
        return

    if args.doc:
        with open(args.doc, "r") as f:
            data = json.load(f)

        doc = Document(
            number=data.get("number", ""),
            title=data.get("title", ""),
            doc_type=data.get("doc_type", ""),
            revision=data.get("revision", ""),
            status=data.get("status", ""),
            effective_date=data.get("effective_date"),
            review_date=data.get("review_date"),
            author=data.get("author"),
            approver=data.get("approver"),
            approval_date=data.get("approval_date"),
            change_history=data.get("change_history", []),
            has_audit_trail=data.get("has_audit_trail", False),
            has_electronic_signature=data.get("has_electronic_signature", False),
            signature_components=data.get("signature_components", 0)
        )
    else:
        # Demo document
        doc = Document(
            number="SOP-02-001",
            title="Document Control",
            doc_type="SOP",
            revision="01",
            status="Effective",
            effective_date="2024-01-15",
            author="J. Smith",
            has_audit_trail=True,
            has_electronic_signature=True,
            signature_components=2
        )

    validator = DocumentValidator(doc)
    result = validator.validate()

    if args.output == "json":
        print(json.dumps(asdict(result), indent=2))
    else:
        print(format_text_output(result))
