# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from test_extractor_base import *  # noqa: F403,E402


class SpecParser:
    """Parses spec documents to extract testable criteria."""

    def __init__(self, content: str):
        self.content = content
        self.lines = content.split("\n")

    def extract_acceptance_criteria(self) -> List[Dict[str, Any]]:
        """Extract AC-N blocks with Given/When/Then clauses."""
        criteria = []
        ac_pattern = re.compile(r"###\s+AC-(\d+):\s*(.+?)(?:\s*\(([^)]+)\))?\s*$")

        in_ac = False
        current_ac: Optional[Dict[str, Any]] = None
        body_lines: List[str] = []

        for line in self.lines:
            match = ac_pattern.match(line)
            if match:
                # Save previous AC
                if current_ac is not None:
                    current_ac["body"] = "\n".join(body_lines).strip()
                    self._parse_gwt(current_ac)
                    criteria.append(current_ac)

                ac_id = int(match.group(1))
                name = match.group(2).strip()
                refs = match.group(3).strip() if match.group(3) else ""

                current_ac = {
                    "id": f"AC-{ac_id}",
                    "name": name,
                    "references": [r.strip() for r in refs.split(",") if r.strip()] if refs else [],
                    "given": "",
                    "when": "",
                    "then": [],
                    "body": "",
                }
                body_lines = []
                in_ac = True
            elif in_ac:
                # Check if we hit another ## section
                if re.match(r"^##\s+", line) and not re.match(r"^###\s+", line):
                    in_ac = False
                    if current_ac is not None:
                        current_ac["body"] = "\n".join(body_lines).strip()
                        self._parse_gwt(current_ac)
                        criteria.append(current_ac)
                        current_ac = None
                else:
                    body_lines.append(line)

        # Don't forget the last one
        if current_ac is not None:
            current_ac["body"] = "\n".join(body_lines).strip()
            self._parse_gwt(current_ac)
            criteria.append(current_ac)

        return criteria

    def extract_edge_cases(self) -> List[Dict[str, Any]]:
        """Extract EC-N edge case items."""
        edge_cases = []
        ec_pattern = re.compile(r"-\s+EC-(\d+):\s*(.+?)(?:\s*->\s*|\s*->\s*|\s*→\s*)(.+)")

        in_section = False
        for line in self.lines:
            if re.match(r"^##\s+Edge\s+Cases", line, re.IGNORECASE):
                in_section = True
                continue
            if in_section and re.match(r"^##\s+", line):
                break
            if in_section:
                match = ec_pattern.match(line.strip())
                if match:
                    edge_cases.append({
                        "id": f"EC-{match.group(1)}",
                        "condition": match.group(2).strip().rstrip("."),
                        "behavior": match.group(3).strip().rstrip("."),
                    })

        return edge_cases

    def extract_spec_title(self) -> str:
        """Extract the spec title from the first H1."""
        for line in self.lines:
            match = re.match(r"^#\s+(?:Spec:\s*)?(.+)", line)
            if match:
                return match.group(1).strip()
        return "UnknownFeature"

    @staticmethod
    def _parse_gwt(ac: Dict[str, Any]):
        """Parse Given/When/Then from the AC body text."""
        body = ac["body"]
        lines = body.split("\n")

        current_section = None
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            lower = stripped.lower()
            if lower.startswith("given "):
                current_section = "given"
                ac["given"] = stripped[6:].strip()
            elif lower.startswith("when "):
                current_section = "when"
                ac["when"] = stripped[5:].strip()
            elif lower.startswith("then "):
                current_section = "then"
                ac["then"].append(stripped[5:].strip())
            elif lower.startswith("and "):
                if current_section == "then":
                    ac["then"].append(stripped[4:].strip())
                elif current_section == "given":
                    ac["given"] += " AND " + stripped[4:].strip()
                elif current_section == "when":
                    ac["when"] += " AND " + stripped[4:].strip()
def _sanitize_name(name: str) -> str:
    """Convert a human-readable name to a valid function/method name."""
    # Remove parenthetical references like (FR-1)
    name = re.sub(r"\([^)]*\)", "", name)
    # Replace non-alphanumeric with underscore
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name)
    # Remove leading/trailing underscores
    name = name.strip("_").lower()
    return name or "unnamed"
