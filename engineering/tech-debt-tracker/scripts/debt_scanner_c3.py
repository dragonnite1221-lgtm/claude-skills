# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_scanner_base import *  # noqa: F403,E402


class DebtScannerMixin3:
    def _add_debt_item(self, debt_type: str, description: str, file_path: str, 
                      severity: str, metadata: Dict[str, Any]):
        """Add a debt item to the inventory."""
        item = {
            "id": f"DEBT-{len(self.debt_items) + 1:04d}",
            "type": debt_type,
            "description": description,
            "file_path": file_path,
            "severity": severity,
            "metadata": metadata,
            "detected_date": datetime.now().isoformat(),
            "status": "identified"
        }
        
        self.debt_items.append(item)
        self.stats[f"debt_{debt_type}"] += 1
        self.stats["total_debt_items"] += 1
        
        if file_path in self.file_stats:
            self.file_stats[file_path]["debt_count"] += 1
    def _generate_report(self, directory: str) -> Dict[str, Any]:
        """Generate the final debt report."""
        # Sort debt items by priority score
        self.debt_items.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        # Calculate summary statistics
        priority_counts = Counter(item["priority"] for item in self.debt_items)
        type_counts = Counter(item["type"] for item in self.debt_items)
        
        # Calculate health score (0-100, higher is better)
        total_files = self.stats.get("files_scanned", 1)
        debt_density = len(self.debt_items) / total_files
        health_score = max(0, 100 - (debt_density * 10))
        
        report = {
            "scan_metadata": {
                "directory": directory,
                "scan_date": datetime.now().isoformat(),
                "scanner_version": "1.0.0",
                "config": self.config
            },
            "summary": {
                "total_files_scanned": self.stats.get("files_scanned", 0),
                "total_lines_scanned": self.stats.get("total_lines", 0),
                "total_debt_items": len(self.debt_items),
                "health_score": round(health_score, 1),
                "debt_density": round(debt_density, 2),
                "priority_breakdown": dict(priority_counts),
                "type_breakdown": dict(type_counts)
            },
            "debt_items": self.debt_items,
            "file_statistics": self.file_stats,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on findings."""
        recommendations = []
        
        # Priority-based recommendations
        high_priority_count = len([item for item in self.debt_items 
                                  if item.get("priority") in ["critical", "high"]])
        
        if high_priority_count > 10:
            recommendations.append(
                f"Address {high_priority_count} high-priority debt items immediately - "
                "they pose significant risk to code quality and maintainability."
            )
        
        # Type-specific recommendations
        type_counts = Counter(item["type"] for item in self.debt_items)
        
        if type_counts.get("large_function", 0) > 5:
            recommendations.append(
                "Consider refactoring large functions into smaller, more focused units. "
                "This will improve readability and testability."
            )
        
        if type_counts.get("duplicate_code", 0) > 3:
            recommendations.append(
                "Extract duplicate code into reusable functions or modules. "
                "This reduces maintenance burden and potential for inconsistent changes."
            )
        
        if type_counts.get("todo_comment", 0) > 20:
            recommendations.append(
                "Review and address TODO/FIXME comments. Consider creating proper "
                "tickets for substantial work items."
            )
        
        # General recommendations
        total_files = self.stats.get("files_scanned", 1)
        if len(self.debt_items) / total_files > 2:
            recommendations.append(
                "High debt density detected. Consider establishing coding standards "
                "and regular code review processes to prevent debt accumulation."
            )
        
        if not recommendations:
            recommendations.append("Code quality looks good! Continue current practices.")
        
        return recommendations
