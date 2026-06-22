# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from gdpr_compliance_checker_base import *  # noqa: F403,E402


PERSONAL_DATA_PATTERNS = {
    "email": {
        "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "category": "contact_data",
        "gdpr_article": "Art. 4(1)",
        "risk": "medium"
    },
    "ip_address": {
        "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "category": "online_identifier",
        "gdpr_article": "Art. 4(1), Recital 30",
        "risk": "medium"
    },
    "phone_number": {
        "pattern": r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "category": "contact_data",
        "gdpr_article": "Art. 4(1)",
        "risk": "medium"
    },
    "credit_card": {
        "pattern": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "category": "financial_data",
        "gdpr_article": "Art. 4(1)",
        "risk": "high"
    },
    "iban": {
        "pattern": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}(?:[A-Z0-9]?){0,16}\b",
        "category": "financial_data",
        "gdpr_article": "Art. 4(1)",
        "risk": "high"
    },
    "german_id": {
        "pattern": r"\b[A-Z0-9]{9}\b",
        "category": "government_id",
        "gdpr_article": "Art. 4(1)",
        "risk": "high"
    },
    "date_of_birth": {
        "pattern": r"\b(?:birth|dob|geboren|geburtsdatum)\b",
        "category": "demographic_data",
        "gdpr_article": "Art. 4(1)",
        "risk": "medium"
    },
    "health_data": {
        "pattern": r"\b(?:diagnosis|treatment|medication|patient|medical|health|symptom|disease)\b",
        "category": "special_category",
        "gdpr_article": "Art. 9(1)",
        "risk": "critical"
    },
    "biometric": {
        "pattern": r"\b(?:fingerprint|facial|retina|biometric|voice_print)\b",
        "category": "special_category",
        "gdpr_article": "Art. 9(1)",
        "risk": "critical"
    },
    "religion": {
        "pattern": r"\b(?:religion|religious|faith|church|mosque|synagogue)\b",
        "category": "special_category",
        "gdpr_article": "Art. 9(1)",
        "risk": "critical"
    }
}
CODE_PATTERNS = {
    "logging_personal_data": {
        "pattern": r"(?:log|print|console)\s*\.\s*(?:info|debug|warn|error)\s*\([^)]*(?:email|user|name|address|phone)",
        "issue": "Potential logging of personal data",
        "gdpr_article": "Art. 5(1)(c) - Data minimization",
        "recommendation": "Review logging to ensure personal data is not logged or is properly pseudonymized",
        "severity": "high"
    },
    "missing_consent": {
        "pattern": r"(?:track|analytics|marketing|cookie)(?!.*consent)",
        "issue": "Tracking without apparent consent mechanism",
        "gdpr_article": "Art. 6(1)(a) - Consent",
        "recommendation": "Implement consent management before tracking",
        "severity": "high"
    },
    "hardcoded_retention": {
        "pattern": r"(?:retention|expire|ttl|lifetime)\s*[=:]\s*(?:null|undefined|0|never|forever)",
        "issue": "Indefinite data retention detected",
        "gdpr_article": "Art. 5(1)(e) - Storage limitation",
        "recommendation": "Define and implement data retention periods",
        "severity": "medium"
    },
    "third_party_transfer": {
        "pattern": r"(?:api|http|fetch|request)\s*\.\s*(?:post|put|send)\s*\([^)]*(?:user|personal|data)",
        "issue": "Potential third-party data transfer",
        "gdpr_article": "Art. 28 - Processor requirements",
        "recommendation": "Ensure Data Processing Agreement exists with third parties",
        "severity": "medium"
    },
    "encryption_missing": {
        "pattern": r"(?:password|secret|token|key)\s*[=:]\s*['\"][^'\"]+['\"]",
        "issue": "Potentially unencrypted sensitive data",
        "gdpr_article": "Art. 32(1)(a) - Encryption",
        "recommendation": "Encrypt sensitive data at rest and in transit",
        "severity": "critical"
    },
    "no_deletion": {
        "pattern": r"(?:delete|remove|erase).*(?:disabled|false|TODO|FIXME)",
        "issue": "Data deletion may be disabled or incomplete",
        "gdpr_article": "Art. 17 - Right to erasure",
        "recommendation": "Implement complete data deletion functionality",
        "severity": "high"
    }
}
CONFIG_PATTERNS = {
    "analytics_config": {
        "files": ["analytics.json", "gtag.js", "google-analytics.js"],
        "check": "anonymize_ip",
        "issue": "IP anonymization should be enabled for analytics",
        "gdpr_article": "Art. 5(1)(c)"
    },
    "cookie_config": {
        "files": ["cookie.config.js", "cookies.json"],
        "check": "consent_required",
        "issue": "Cookie consent should be required before non-essential cookies",
        "gdpr_article": "Art. 6(1)(a)"
    }
}
SCANNABLE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".kt",
    ".go", ".rb", ".php", ".cs", ".swift", ".json", ".yaml",
    ".yml", ".xml", ".html", ".env", ".config"
}
SKIP_PATTERNS = {
    "node_modules", "vendor", ".git", "__pycache__", "dist",
    "build", ".venv", "venv", "env"
}
