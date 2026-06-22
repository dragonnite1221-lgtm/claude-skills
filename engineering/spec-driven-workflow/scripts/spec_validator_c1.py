# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_validator_base import *  # noqa: F403,E402


class SpecValidatorMixin1:
    def _check_acceptance_criteria(self):
        """Validate acceptance criteria use Given/When/Then format."""
        content = self._find_section_content(r"^##\s+Acceptance\s+Criteria")
        if not content.strip():
            return

        ac_pattern = re.compile(r"###\s+AC-(\d+):")
        matches = ac_pattern.findall(content)

        if not matches:
            self._add_finding("error", "acceptance_criteria", "No numbered acceptance criteria found (expected ### AC-N: format)")
            if "acceptance_criteria" in self.section_scores:
                self.section_scores["acceptance_criteria"]["score"] = max(
                    0, self.section_scores["acceptance_criteria"]["score"] - 15
                )
            return

        ac_count = len(matches)

        # Check Given/When/Then
        given_count = len(re.findall(r"(?i)\bgiven\b", content))
        when_count = len(re.findall(r"(?i)\bwhen\b", content))
        then_count = len(re.findall(r"(?i)\bthen\b", content))

        if given_count < ac_count:
            self._add_finding("warning", "acceptance_criteria",
                              f"Found {ac_count} criteria but only {given_count} 'Given' clauses. Each AC needs Given/When/Then.")
        if when_count < ac_count:
            self._add_finding("warning", "acceptance_criteria",
                              f"Found {ac_count} criteria but only {when_count} 'When' clauses.")
        if then_count < ac_count:
            self._add_finding("warning", "acceptance_criteria",
                              f"Found {ac_count} criteria but only {then_count} 'Then' clauses.")

        # Check for FR references
        fr_refs = re.findall(r"\(FR-\d+", content)
        if not fr_refs:
            self._add_finding("warning", "acceptance_criteria",
                              "No acceptance criteria reference functional requirements (expected (FR-N) in title).")
    def _check_edge_cases(self):
        """Validate edge cases section."""
        content = self._find_section_content(r"^##\s+Edge\s+Cases")
        if not content.strip():
            return

        ec_pattern = re.compile(r"-\s+EC-(\d+):")
        matches = ec_pattern.findall(content)

        if not matches:
            self._add_finding("warning", "edge_cases", "No numbered edge cases found (expected EC-N: format)")
        elif len(matches) < 3:
            self._add_finding("warning", "edge_cases", f"Only {len(matches)} edge cases. Consider failure modes for each external dependency.")
    def _check_rfc_keywords(self):
        """Check RFC 2119 keywords are used consistently (capitalized)."""
        # Look for lowercase must/should/may that might be intended as RFC keywords
        context_content = self._find_section_content(r"^##\s+Functional\s+Requirements")
        context_content += self._find_section_content(r"^##\s+Non-Functional\s+Requirements")

        for kw in ["must", "should", "may"]:
            # Find lowercase usage in requirement-like sentences
            pattern = rf"(?:system|service|API|endpoint)\s+{kw}\s+"
            if re.search(pattern, context_content):
                self._add_finding("warning", "rfc_keywords",
                                  f"Found lowercase '{kw}' in requirements. RFC 2119 keywords should be UPPERCASE: {kw.upper()}")
    def _check_api_contracts(self):
        """Validate API contracts section."""
        content = self._find_section_content(r"^##\s+API\s+Contracts")
        if not content.strip():
            return

        # Check for at least one endpoint definition
        has_endpoint = bool(re.search(r"(GET|POST|PUT|PATCH|DELETE)\s+/", content))
        if not has_endpoint:
            self._add_finding("warning", "api_contracts", "No HTTP method + path found (expected e.g., POST /api/endpoint)")

        # Check for request/response definitions
        has_interface = bool(re.search(r"interface\s+\w+", content))
        if not has_interface:
            self._add_finding("info", "api_contracts", "No TypeScript interfaces found. Consider defining request/response shapes.")
    def _check_data_models(self):
        """Validate data models section."""
        content = self._find_section_content(r"^##\s+Data\s+Models")
        if not content.strip():
            return

        # Check for table format
        has_table = bool(re.search(r"\|.*\|.*\|", content))
        if not has_table:
            self._add_finding("warning", "data_models", "No table-formatted data models found. Use | Field | Type | Constraints | format.")
    def _check_out_of_scope(self):
        """Validate out of scope section."""
        content = self._find_section_content(r"^##\s+Out\s+of\s+Scope")
        if not content.strip():
            return

        os_pattern = re.compile(r"-\s+OS-(\d+):")
        matches = os_pattern.findall(content)

        if not matches:
            self._add_finding("warning", "out_of_scope", "No numbered exclusions found (expected OS-N: format)")
        elif len(matches) < 2:
            self._add_finding("info", "out_of_scope", "Only 1 exclusion listed. Consider what was deliberately left out.")
