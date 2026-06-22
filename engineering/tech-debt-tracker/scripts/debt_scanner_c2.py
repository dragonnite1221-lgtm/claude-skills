# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_scanner_base import *  # noqa: F403,E402


class DebtScannerMixin2:
    def _scan_common_patterns(self, file_path: str, content: str, lines: List[str]):
        """Scan for common patterns across all file types."""
        # TODO/FIXME comments
        for i, line in enumerate(lines):
            for pattern_name, regex in self.comment_regexes.items():
                match = regex.search(line)
                if match:
                    if pattern_name == "todo":
                        self._add_debt_item(
                            "todo_comment",
                            f"TODO/FIXME comment: {match.group(0)}",
                            file_path,
                            "low",
                            {"line_number": i + 1, "comment": match.group(0).strip()}
                        )
        
        # Code smells
        for smell_name, pattern in self.smell_patterns.items():
            matches = pattern.finditer(content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self._add_debt_item(
                    smell_name,
                    f"Code smell detected: {smell_name}",
                    file_path,
                    "medium",
                    {"line_number": line_num, "pattern": match.group(0)[:100]}
                )
    def _detect_duplicates(self, directory: str):
        """Detect duplicate code blocks across files."""
        # Simple duplicate detection based on exact line matches
        line_hashes = defaultdict(list)
        
        for file_path, file_info in self.file_stats.items():
            try:
                full_path = os.path.join(directory, file_path)
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for i in range(len(lines) - self.config["min_duplicate_lines"] + 1):
                    block = ''.join(lines[i:i + self.config["min_duplicate_lines"]])
                    block_hash = hash(block.strip())
                    if len(block.strip()) > 50:  # Only consider substantial blocks
                        line_hashes[block_hash].append((file_path, i + 1, block))
            except Exception:
                continue
        
        # Report duplicates
        for block_hash, occurrences in line_hashes.items():
            if len(occurrences) > 1:
                for file_path, line_num, block in occurrences:
                    self._add_debt_item(
                        "duplicate_code",
                        f"Duplicate code block found in {len(occurrences)} files",
                        file_path,
                        "medium",
                        {
                            "line_number": line_num,
                            "duplicate_count": len(occurrences),
                            "other_files": [f[0] for f in occurrences if f[0] != file_path]
                        }
                    )
    def _calculate_priorities(self):
        """Calculate priority scores for debt items."""
        severity_weights = self.config["severity_weights"]
        
        for item in self.debt_items:
            base_score = severity_weights.get(item["severity"], 1)
            
            # Adjust based on debt type
            type_multipliers = {
                "syntax_error": 2.0,
                "security_risk": 1.8,
                "large_function": 1.5,
                "high_complexity": 1.4,
                "duplicate_code": 1.3,
                "todo_comment": 0.5
            }
            
            multiplier = type_multipliers.get(item["type"], 1.0)
            item["priority_score"] = int(base_score * multiplier)
            
            # Set priority category
            if item["priority_score"] >= 15:
                item["priority"] = "critical"
            elif item["priority_score"] >= 10:
                item["priority"] = "high"
            elif item["priority_score"] >= 5:
                item["priority"] = "medium"
            else:
                item["priority"] = "low"
