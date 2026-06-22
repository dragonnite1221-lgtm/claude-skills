# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402
from release_planner_p0 import ComponentStatus, RiskLevel  # noqa: F401,E501


class ReleasePlannerMixin2:
    def assess_release_readiness(self) -> Dict:
        """Assess overall release readiness."""
        assessment = {
            'overall_status': 'ready',
            'readiness_score': 0.0,
            'blocking_issues': [],
            'warnings': [],
            'recommendations': [],
            'feature_summary': {},
            'quality_gate_summary': {},
            'timeline_assessment': {}
        }
        
        total_score = 0
        max_score = 0
        
        # Assess features
        feature_stats = {
            'total': len(self.features),
            'ready': 0,
            'blocked': 0,
            'in_progress': 0,
            'pending': 0,
            'high_risk': 0,
            'breaking_changes': 0,
            'missing_approvals': 0,
            'low_test_coverage': 0
        }
        
        for feature in self.features:
            max_score += 10  # Each feature worth 10 points
            
            if feature.status == ComponentStatus.READY:
                feature_stats['ready'] += 1
                total_score += 10
            elif feature.status == ComponentStatus.BLOCKED:
                feature_stats['blocked'] += 1
                assessment['blocking_issues'].append(
                    f"Feature '{feature.title}' ({feature.id}) is blocked"
                )
            elif feature.status == ComponentStatus.IN_PROGRESS:
                feature_stats['in_progress'] += 1
                total_score += 5  # Partial credit
                assessment['warnings'].append(
                    f"Feature '{feature.title}' ({feature.id}) still in progress"
                )
            else:
                feature_stats['pending'] += 1
                assessment['warnings'].append(
                    f"Feature '{feature.title}' ({feature.id}) is pending"
                )
            
            # Check risk level
            if feature.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                feature_stats['high_risk'] += 1
            
            # Check breaking changes
            if feature.breaking_changes:
                feature_stats['breaking_changes'] += 1
            
            # Check approvals
            missing_approvals = self._check_feature_approvals(feature)
            if missing_approvals:
                feature_stats['missing_approvals'] += 1
                assessment['blocking_issues'].append(
                    f"Feature '{feature.title}' missing approvals: {', '.join(missing_approvals)}"
                )
            
            # Check test coverage
            if (feature.test_coverage_actual is not None and 
                feature.test_coverage_actual < feature.test_coverage_required):
                feature_stats['low_test_coverage'] += 1
                assessment['warnings'].append(
                    f"Feature '{feature.title}' has low test coverage: "
                    f"{feature.test_coverage_actual}% < {feature.test_coverage_required}%"
                )
        
        assessment['feature_summary'] = feature_stats
        
        # Assess quality gates
        gate_stats = {
            'total': len(self.quality_gates),
            'passed': 0,
            'failed': 0,
            'pending': 0,
            'required_failed': 0
        }
        
        for gate in self.quality_gates:
            max_score += 5  # Each gate worth 5 points
            
            if gate.status == ComponentStatus.READY:
                gate_stats['passed'] += 1
                total_score += 5
            elif gate.status == ComponentStatus.FAILED:
                gate_stats['failed'] += 1
                if gate.required:
                    gate_stats['required_failed'] += 1
                    assessment['blocking_issues'].append(
                        f"Required quality gate '{gate.name}' failed"
                    )
            else:
                gate_stats['pending'] += 1
                if gate.required:
                    assessment['warnings'].append(
                        f"Required quality gate '{gate.name}' is pending"
                    )
        
        assessment['quality_gate_summary'] = gate_stats
        
        # Timeline assessment
        if self.target_date:
            # Handle timezone-aware datetime comparison
            now = datetime.now(self.target_date.tzinfo) if self.target_date.tzinfo else datetime.now()
            days_until_release = (self.target_date - now).days
            assessment['timeline_assessment'] = {
                'target_date': self.target_date.isoformat(),
                'days_remaining': days_until_release,
                'timeline_status': 'on_track' if days_until_release > 0 else 'overdue'
            }
            
            if days_until_release < 0:
                assessment['blocking_issues'].append(f"Release is {abs(days_until_release)} days overdue")
            elif days_until_release < 3 and feature_stats['blocked'] > 0:
                assessment['blocking_issues'].append("Not enough time to resolve blocked features")
        
        # Calculate overall readiness score
        if max_score > 0:
            assessment['readiness_score'] = (total_score / max_score) * 100
        
        # Determine overall status
        if assessment['blocking_issues']:
            assessment['overall_status'] = 'blocked'
        elif assessment['warnings']:
            assessment['overall_status'] = 'at_risk'
        else:
            assessment['overall_status'] = 'ready'
        
        # Generate recommendations
        if feature_stats['missing_approvals'] > 0:
            assessment['recommendations'].append("Obtain required approvals for pending features")
        
        if feature_stats['low_test_coverage'] > 0:
            assessment['recommendations'].append("Improve test coverage for features below threshold")
        
        if gate_stats['pending'] > 0:
            assessment['recommendations'].append("Complete pending quality gate validations")
        
        if feature_stats['high_risk'] > 0:
            assessment['recommendations'].append("Review high-risk features for additional validation")
        
        return assessment
