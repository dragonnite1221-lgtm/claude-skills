# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_prioritizer_base import *  # noqa: F403,E402
from debt_prioritizer_p0 import EffortEstimate  # noqa: F401,E501


class DebtPrioritizerMixin1:
    def _enrich_debt_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich debt item with detailed estimates and impact analysis."""
        enriched = item.copy()
        
        # Generate effort estimate
        effort = self._estimate_effort(item)
        enriched["effort_estimate"] = asdict(effort)
        
        # Generate business impact assessment
        business_impact = self._assess_business_impact(item)
        enriched["business_impact"] = asdict(business_impact)
        
        # Calculate interest rate
        interest_rate = self._calculate_interest_rate(item, business_impact)
        enriched["interest_rate"] = asdict(interest_rate)
        
        # Calculate cost of delay
        enriched["cost_of_delay"] = self._calculate_cost_of_delay(interest_rate, effort)
        
        # Assign categories and tags
        enriched["category"] = self._categorize_debt_item(item)
        enriched["impact_tags"] = self._generate_impact_tags(item, business_impact)
        
        return enriched
    def _estimate_effort(self, item: Dict[str, Any]) -> EffortEstimate:
        """Estimate effort required to fix debt item."""
        debt_type = item.get("type", "unknown")
        severity = item.get("severity", "medium")
        
        # Base effort estimation by debt type
        base_efforts = {
            "todo_comment": (1, 2),
            "missing_docstring": (1, 4),
            "long_line": (0.5, 1),
            "large_function": (4, 16),
            "high_complexity": (8, 32),
            "duplicate_code": (6, 24),
            "large_file": (16, 64),
            "syntax_error": (2, 8),
            "security_risk": (4, 40),
            "architecture_debt": (40, 160),
            "test_debt": (8, 40),
            "dependency_debt": (4, 24)
        }
        
        min_hours, max_hours = base_efforts.get(debt_type, (4, 16))
        
        # Adjust by severity
        severity_multipliers = {
            "low": 0.5,
            "medium": 1.0,
            "high": 1.5,
            "critical": 2.0
        }
        
        multiplier = severity_multipliers.get(severity, 1.0)
        hours_estimate = (min_hours + max_hours) / 2 * multiplier
        
        # Convert to story points (assuming 6 hours per point)
        size_points = max(1, round(hours_estimate / 6))
        
        # Determine risk factor
        risk_factor = 1.0
        if debt_type in ["architecture_debt", "security_risk", "large_file"]:
            risk_factor = 1.8
        elif debt_type in ["high_complexity", "duplicate_code"]:
            risk_factor = 1.4
        elif debt_type in ["syntax_error", "dependency_debt"]:
            risk_factor = 1.2
        
        # Determine skill level required
        skill_requirements = {
            "architecture_debt": "expert",
            "security_risk": "senior",
            "high_complexity": "senior",
            "large_function": "mid",
            "duplicate_code": "mid",
            "dependency_debt": "mid",
            "test_debt": "mid",
            "todo_comment": "junior",
            "missing_docstring": "junior",
            "long_line": "junior"
        }
        
        skill_level = skill_requirements.get(debt_type, "mid")
        
        # Confidence based on debt type clarity
        confidence_levels = {
            "todo_comment": 0.9,
            "missing_docstring": 0.9,
            "long_line": 0.95,
            "syntax_error": 0.8,
            "large_function": 0.7,
            "duplicate_code": 0.6,
            "high_complexity": 0.5,
            "architecture_debt": 0.3,
            "security_risk": 0.4
        }
        
        confidence = confidence_levels.get(debt_type, 0.6)
        
        return EffortEstimate(
            size_points=size_points,
            hours_estimate=hours_estimate,
            risk_factor=risk_factor,
            skill_level_required=skill_level,
            confidence=confidence
        )
