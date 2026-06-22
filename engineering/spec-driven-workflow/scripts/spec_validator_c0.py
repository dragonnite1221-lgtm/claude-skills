# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_validator_base import *  # noqa: F403,E402


class SpecValidatorMixin0:
    """Validates a spec document for completeness and quality."""
    def __init__(self, content: str, file_path: str = ""):
        self.content = content
        self.file_path = file_path
        self.lines = content.split("\n")
        self.findings: List[Dict[str, Any]] = []
        self.section_scores: Dict[str, Dict[str, Any]] = {}
    def validate(self) -> Dict[str, Any]:
        """Run all validation checks and return results."""
        self._check_sections_present()
        self._check_functional_requirements()
        self._check_acceptance_criteria()
        self._check_edge_cases()
        self._check_rfc_keywords()
        self._check_api_contracts()
        self._check_data_models()
        self._check_out_of_scope()
        self._check_placeholders()
        self._check_traceability()

        total_score = self._calculate_score()

        return {
            "file": self.file_path,
            "score": total_score,
            "grade": self._score_to_grade(total_score),
            "sections": self.section_scores,
            "findings": self.findings,
            "summary": self._build_summary(total_score),
        }
    def _add_finding(self, severity: str, section: str, message: str):
        """Record a validation finding."""
        self.findings.append({
            "severity": severity,  # "error", "warning", "info"
            "section": section,
            "message": message,
        })
    def _find_section_content(self, header_pattern: str) -> str:
        """Extract content between a section header and the next ## header."""
        in_section = False
        section_lines = []
        for line in self.lines:
            if re.match(header_pattern, line, re.IGNORECASE):
                in_section = True
                continue
            if in_section and re.match(r"^##\s+", line):
                break
            if in_section:
                section_lines.append(line)
        return "\n".join(section_lines)
    def _check_sections_present(self):
        """Check that all required sections exist."""
        for key, name, patterns, weight in SECTIONS:
            found = False
            for pattern in patterns:
                for line in self.lines:
                    if re.search(pattern, line, re.IGNORECASE):
                        found = True
                        break
                if found:
                    break

            if found:
                self.section_scores[key] = {"name": name, "present": True, "score": weight, "max": weight}
            else:
                self.section_scores[key] = {"name": name, "present": False, "score": 0, "max": weight}
                self._add_finding("error", key, f"Missing section: {name}")
    def _check_functional_requirements(self):
        """Validate functional requirements format and content."""
        content = self._find_section_content(r"^##\s+Functional\s+Requirements")
        if not content.strip():
            return

        fr_pattern = re.compile(r"-\s+FR-(\d+):")
        matches = fr_pattern.findall(content)

        if not matches:
            self._add_finding("error", "functional_requirements", "No numbered requirements found (expected FR-N: format)")
            if "functional_requirements" in self.section_scores:
                self.section_scores["functional_requirements"]["score"] = max(
                    0, self.section_scores["functional_requirements"]["score"] - 10
                )
            return

        fr_count = len(matches)
        if fr_count < 3:
            self._add_finding("warning", "functional_requirements", f"Only {fr_count} requirements found. Most features need 3+.")

        # Check for RFC keywords
        has_keyword = False
        for kw in RFC_KEYWORDS:
            if kw in content:
                has_keyword = True
                break
        if not has_keyword:
            self._add_finding("warning", "functional_requirements", "No RFC 2119 keywords (MUST/SHOULD/MAY) found.")
