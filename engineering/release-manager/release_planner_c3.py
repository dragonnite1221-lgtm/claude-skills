# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from release_planner_base import *  # noqa: F403,E402
from release_planner_p0 import ComponentStatus, Feature, RiskLevel  # noqa: F401,E501


class ReleasePlannerMixin3:
    def _check_feature_approvals(self, feature: Feature) -> List[str]:
        """Check which approvals are missing for a feature."""
        missing = []
        
        # Determine required approvals based on risk level
        required = self.required_approvals.copy()
        if feature.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            required = self.high_risk_approval_requirements.copy()
        
        if 'pm_approved' in required and not feature.pm_approved:
            missing.append('PM approval')
        
        if 'qa_approved' in required and not feature.qa_approved:
            missing.append('QA approval')
        
        if 'security_approved' in required and not feature.security_approved:
            missing.append('Security approval')
        
        return missing
    def generate_release_checklist(self) -> List[Dict]:
        """Generate comprehensive release checklist."""
        checklist = []
        
        # Pre-release validation
        checklist.extend([
            {
                'category': 'Pre-Release Validation',
                'item': 'All features implemented and tested',
                'status': 'ready' if all(f.status == ComponentStatus.READY for f in self.features) else 'pending',
                'details': f"{len([f for f in self.features if f.status == ComponentStatus.READY])}/{len(self.features)} features ready"
            },
            {
                'category': 'Pre-Release Validation', 
                'item': 'Breaking changes documented',
                'status': 'ready' if self._check_breaking_change_docs() else 'pending',
                'details': f"{len([f for f in self.features if f.breaking_changes])} features have breaking changes"
            },
            {
                'category': 'Pre-Release Validation',
                'item': 'Migration scripts tested',
                'status': 'ready' if self._check_migrations() else 'pending',
                'details': f"{len([f for f in self.features if f.requires_migration])} features require migrations"
            }
        ])
        
        # Quality gates
        for gate in self.quality_gates:
            checklist.append({
                'category': 'Quality Gates',
                'item': gate.name,
                'status': gate.status.value,
                'details': gate.details,
                'required': gate.required
            })
        
        # Approvals
        approval_items = [
            ('Product Manager sign-off', self._check_pm_approvals()),
            ('QA validation complete', self._check_qa_approvals()), 
            ('Security team clearance', self._check_security_approvals())
        ]
        
        for item, status in approval_items:
            checklist.append({
                'category': 'Approvals',
                'item': item,
                'status': 'ready' if status else 'pending'
            })
        
        # Documentation
        doc_items = [
            'CHANGELOG.md updated',
            'API documentation updated', 
            'User documentation updated',
            'Migration guide written',
            'Rollback procedure documented'
        ]
        
        for item in doc_items:
            checklist.append({
                'category': 'Documentation',
                'item': item,
                'status': 'pending'  # Would need integration with docs system to check
            })
        
        # Deployment preparation
        deployment_items = [
            'Database migrations prepared',
            'Environment variables configured',
            'Monitoring alerts updated',
            'Rollback plan tested',
            'Stakeholders notified'
        ]
        
        for item in deployment_items:
            checklist.append({
                'category': 'Deployment',
                'item': item,
                'status': 'pending'
            })
        
        return checklist
    def _check_breaking_change_docs(self) -> bool:
        """Check if breaking changes are properly documented."""
        features_with_breaking_changes = [f for f in self.features if f.breaking_changes]
        return all(len(f.breaking_changes) > 0 for f in features_with_breaking_changes)
    def _check_migrations(self) -> bool:
        """Check migration readiness."""
        features_with_migrations = [f for f in self.features if f.requires_migration]
        return all(f.status == ComponentStatus.READY for f in features_with_migrations)
