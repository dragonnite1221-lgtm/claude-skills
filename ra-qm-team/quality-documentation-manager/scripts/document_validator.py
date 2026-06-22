# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from document_validator_base import *  # noqa: F403,E402
from document_validator_p0 import Document, DocumentStatus, DocumentType, Severity, ValidationFinding, ValidationResult, format_text_output  # noqa: F401,E501
from document_validator_p1 import interactive_mode  # noqa: F401,E501
from document_validator_p2 import main  # noqa: F401,E501
from document_validator_c0 import DocumentValidatorMixin0  # noqa: F401
from document_validator_c1 import DocumentValidatorMixin1  # noqa: F401
from document_validator_c2 import DocumentValidatorMixin2  # noqa: F401
from document_validator_c3 import DocumentValidatorMixin3  # noqa: F401


class DocumentValidator(DocumentValidatorMixin0, DocumentValidatorMixin1, DocumentValidatorMixin2, DocumentValidatorMixin3):
    pass


if __name__ == "__main__":
    main()
