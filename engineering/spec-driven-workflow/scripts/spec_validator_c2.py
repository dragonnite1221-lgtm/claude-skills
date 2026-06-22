# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from spec_validator_base import *  # noqa: F403,E402


class SpecValidatorMixin2:
    def _check_placeholders(self):
        """Check for unfilled placeholder text."""
        placeholder_count = 0
        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            placeholder_count += len(matches)

        if placeholder_count > 0:
            self._add_finding("warning", "placeholders",
                              f"Found {placeholder_count} placeholder(s) that need to be filled in (e.g., [your name], [describe ...]).")
            # Deduct from overall score proportionally
            for key in self.section_scores:
                if self.section_scores[key]["present"]:
                    deduction = min(3, self.section_scores[key]["score"])
                    self.section_scores[key]["score"] = max(0, self.section_scores[key]["score"] - deduction)
    def _check_traceability(self):
        """Check that acceptance criteria reference functional requirements."""
        ac_content = self._find_section_content(r"^##\s+Acceptance\s+Criteria")
        fr_content = self._find_section_content(r"^##\s+Functional\s+Requirements")

        if not ac_content.strip() or not fr_content.strip():
            return

        # Extract FR IDs
        fr_ids = set(re.findall(r"FR-(\d+)", fr_content))
        # Extract FR references from AC
        ac_fr_refs = set(re.findall(r"FR-(\d+)", ac_content))

        unreferenced = fr_ids - ac_fr_refs
        if unreferenced:
            unreferenced_list = ", ".join(f"FR-{i}" for i in sorted(unreferenced))
            self._add_finding("warning", "traceability",
                              f"Functional requirements without acceptance criteria: {unreferenced_list}")
    def _calculate_score(self) -> int:
        """Calculate the total completeness score."""
        total = sum(s["score"] for s in self.section_scores.values())
        maximum = sum(s["max"] for s in self.section_scores.values())

        if maximum == 0:
            return 0

        # Apply finding-based deductions
        error_count = sum(1 for f in self.findings if f["severity"] == "error")
        warning_count = sum(1 for f in self.findings if f["severity"] == "warning")

        base_score = round((total / maximum) * 100)
        deduction = (error_count * 5) + (warning_count * 2)

        return max(0, min(100, base_score - deduction))
    @staticmethod
    def _score_to_grade(score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"
    def _build_summary(self, score: int) -> str:
        """Build human-readable summary."""
        errors = [f for f in self.findings if f["severity"] == "error"]
        warnings = [f for f in self.findings if f["severity"] == "warning"]
        infos = [f for f in self.findings if f["severity"] == "info"]

        lines = [
            f"Spec Completeness Score: {score}/100 (Grade: {self._score_to_grade(score)})",
            f"Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(infos)}",
            "",
        ]

        if errors:
            lines.append("ERRORS (must fix):")
            for e in errors:
                lines.append(f"  [{e['section']}] {e['message']}")
            lines.append("")

        if warnings:
            lines.append("WARNINGS (should fix):")
            for w in warnings:
                lines.append(f"  [{w['section']}] {w['message']}")
            lines.append("")

        if infos:
            lines.append("INFO:")
            for i in infos:
                lines.append(f"  [{i['section']}] {i['message']}")
            lines.append("")

        # Section breakdown
        lines.append("Section Breakdown:")
        for key, data in self.section_scores.items():
            status = "PRESENT" if data["present"] else "MISSING"
            lines.append(f"  {data['name']}: {data['score']}/{data['max']} ({status})")

        return "\n".join(lines)
