# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402


class DebtDashboardMixin2:
    def _categorize_debt_item(self, item: Dict[str, Any]) -> str:
        """Categorize debt item into high-level categories."""
        debt_type = item.get("type", "unknown")
        
        categories = {
            "code_quality": ["large_function", "high_complexity", "duplicate_code", 
                           "long_line", "missing_docstring"],
            "architecture": ["architecture_debt", "large_file"],
            "security": ["security_risk", "hardcoded_secrets", "sql_injection_risk"],
            "testing": ["test_debt", "missing_tests", "low_coverage"],
            "maintenance": ["todo_comment", "commented_code"],
            "dependencies": ["dependency_debt", "outdated_packages"],
            "infrastructure": ["deployment_debt", "monitoring_gaps"],
            "documentation": ["missing_docstring", "outdated_docs"]
        }
        
        for category, types in categories.items():
            if debt_type in types:
                return category
        
        return "other"
    def _calculate_total_effort(self, debt_items: List[Dict[str, Any]]) -> float:
        """Calculate total estimated effort for debt items."""
        total_effort = 0.0
        
        for item in debt_items:
            # Try to get effort from existing analysis
            if "effort_estimate" in item:
                total_effort += item["effort_estimate"].get("hours_estimate", 0)
            else:
                # Estimate based on debt type and severity
                effort = self._estimate_item_effort(item)
                total_effort += effort
        
        return total_effort
    def _estimate_item_effort(self, item: Dict[str, Any]) -> float:
        """Estimate effort for a debt item."""
        debt_type = item.get("type", "unknown")
        severity = item.get("severity", "medium")
        
        base_efforts = {
            "todo_comment": 2,
            "missing_docstring": 2,
            "long_line": 1,
            "large_function": 8,
            "high_complexity": 16,
            "duplicate_code": 12,
            "large_file": 32,
            "syntax_error": 4,
            "security_risk": 20,
            "architecture_debt": 80,
            "test_debt": 16
        }
        
        base_effort = base_efforts.get(debt_type, 8)
        
        severity_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "critical": 2.0
        }
        
        return base_effort * severity_multipliers.get(severity, 1.0)
    def _is_high_priority(self, item: Dict[str, Any]) -> bool:
        """Determine if debt item is high priority."""
        severity = item.get("severity", "medium")
        priority_score = item.get("priority_score", 0)
        debt_type = item.get("type", "")
        
        return (severity in ["high", "critical"] or 
                priority_score >= 7 or
                debt_type in ["security_risk", "syntax_error", "architecture_debt"])
    def _is_security_related(self, item: Dict[str, Any]) -> bool:
        """Determine if debt item is security-related."""
        debt_type = item.get("type", "")
        description = item.get("description", "").lower()
        
        security_types = ["security_risk", "hardcoded_secrets", "sql_injection_risk"]
        security_keywords = ["password", "token", "key", "secret", "auth", "security"]
        
        return (debt_type in security_types or 
                any(keyword in description for keyword in security_keywords))
