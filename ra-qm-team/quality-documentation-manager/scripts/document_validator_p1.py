# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402
from document_validator_p0 import Document, format_text_output  # noqa: F401,E501


def interactive_mode():
    """Run interactive document validation."""
    print("=" * 60)
    print("Document Validator - Interactive Mode")
    print("=" * 60)

    print("\nEnter document information:\n")

    number = input("Document Number (e.g., SOP-02-001): ").strip()
    title = input("Document Title: ").strip()

    print("\nDocument Types: QM, SOP, WI, TF, POL, SPEC, PLN, RPT")
    doc_type = input("Document Type: ").strip().upper()

    revision = input("Revision (e.g., 01 or A): ").strip()

    print("\nStatuses: Draft, Under Review, Approved, Effective, Superseded, Obsolete")
    status = input("Status: ").strip()

    effective_date = input("Effective Date (YYYY-MM-DD, or Enter to skip): ").strip() or None
    review_date = input("Next Review Date (YYYY-MM-DD, or Enter to skip): ").strip() or None

    author = input("Author Name (or Enter to skip): ").strip() or None
    approver = input("Approver Name (or Enter to skip): ").strip() or None

    has_audit = input("Has Audit Trail? (y/n): ").strip().lower() == 'y'
    has_esig = input("Uses Electronic Signatures? (y/n): ").strip().lower() == 'y'

    sig_components = 0
    if has_esig:
        sig_input = input("Number of signature components (e.g., 2): ").strip()
        sig_components = int(sig_input) if sig_input.isdigit() else 0

    doc = Document(
        number=number,
        title=title,
        doc_type=doc_type,
        revision=revision,
        status=status,
        effective_date=effective_date,
        review_date=review_date,
        author=author,
        approver=approver,
        has_audit_trail=has_audit,
        has_electronic_signature=has_esig,
        signature_components=sig_components
    )

    validator = DocumentValidator(doc)
    result = validator.validate()
    print("\n" + format_text_output(result))
