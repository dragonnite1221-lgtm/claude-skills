#!/usr/bin/env python3
"""
Release Planner

Takes a list of features/PRs/tickets planned for release and assesses release readiness.
Checks for required approvals, test coverage thresholds, breaking change documentation,
dependency updates, migration steps needed. Generates release checklist, communication
plan, and rollback procedures.

Input: release plan JSON (features, PRs, target date)
Output: release readiness report + checklist + rollback runbook + announcement draft
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for release components."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComponentStatus(Enum):
    """Status of release components."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class Feature:
    """Represents a feature in the release."""
    id: str
    title: str
    description: str
    type: str  # feature, bugfix, security, breaking_change, etc.
    assignee: str
    status: ComponentStatus
    pull_request_url: Optional[str] = None
    issue_url: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    test_coverage_required: float = 80.0
    test_coverage_actual: Optional[float] = None
    requires_migration: bool = False
    migration_complexity: str = "simple"  # simple, moderate, complex
    breaking_changes: List[str] = None
    dependencies: List[str] = None
    qa_approved: bool = False
    security_approved: bool = False
    pm_approved: bool = False
    
    def __post_init__(self):
        if self.breaking_changes is None:
            self.breaking_changes = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class QualityGate:
    """Quality gate requirements."""
    name: str
    required: bool
    status: ComponentStatus
    details: Optional[str] = None
    threshold: Optional[float] = None
    actual_value: Optional[float] = None


@dataclass
class Stakeholder:
    """Stakeholder for release communication."""
    name: str
    role: str
    contact: str
    notification_type: str  # email, slack, teams
    critical_path: bool = False


@dataclass
class RollbackStep:
    """Individual rollback step."""
    order: int
    description: str
    command: Optional[str] = None
    estimated_time: str = "5 minutes"
    risk_level: RiskLevel = RiskLevel.LOW
    verification: str = ""


class ReleasePlanner:
    """Main release planning and assessment logic."""
    
    def __init__(self):
        self.release_name: str = ""
        self.version: str = ""
        self.target_date: Optional[datetime] = None
        self.features: List[Feature] = []
        self.quality_gates: List[QualityGate] = []
        self.stakeholders: List[Stakeholder] = []
        self.rollback_steps: List[RollbackStep] = []
        
        # Configuration
        self.min_test_coverage = 80.0
        self.required_approvals = ['pm_approved', 'qa_approved']
        self.high_risk_approval_requirements = ['pm_approved', 'qa_approved', 'security_approved']
        
    def load_release_plan(self, plan_data: Union[str, Dict]):
        """Load release plan from JSON."""
        if isinstance(plan_data, str):
            data = json.loads(plan_data)
        else:
            data = plan_data
        
        self.release_name = data.get('release_name', 'Unnamed Release')
        self.version = data.get('version', '1.0.0')
        
        if 'target_date' in data:
            self.target_date = datetime.fromisoformat(data['target_date'].replace('Z', '+00:00'))
        
        # Load features
        self.features = []
        for feature_data in data.get('features', []):
            try:
                status = ComponentStatus(feature_data.get('status', 'pending'))
                risk_level = RiskLevel(feature_data.get('risk_level', 'medium'))
                
                feature = Feature(
                    id=feature_data['id'],
                    title=feature_data['title'],
                    description=feature_data.get('description', ''),
                    type=feature_data.get('type', 'feature'),
                    assignee=feature_data.get('assignee', ''),
                    status=status,
                    pull_request_url=feature_data.get('pull_request_url'),
                    issue_url=feature_data.get('issue_url'),
                    risk_level=risk_level,
                    test_coverage_required=feature_data.get('test_coverage_required', 80.0),
                    test_coverage_actual=feature_data.get('test_coverage_actual'),
                    requires_migration=feature_data.get('requires_migration', False),
                    migration_complexity=feature_data.get('migration_complexity', 'simple'),
                    breaking_changes=feature_data.get('breaking_changes', []),
                    dependencies=feature_data.get('dependencies', []),
                    qa_approved=feature_data.get('qa_approved', False),
                    security_approved=feature_data.get('security_approved', False),
                    pm_approved=feature_data.get('pm_approved', False)
                )
                self.features.append(feature)
            except Exception as e:
                print(f"Warning: Error parsing feature {feature_data.get('id', 'unknown')}: {e}", 
                      file=sys.stderr)
        
        # Load quality gates
        self.quality_gates = []
        for gate_data in data.get('quality_gates', []):
            try:
                status = ComponentStatus(gate_data.get('status', 'pending'))
                gate = QualityGate(
                    name=gate_data['name'],
                    required=gate_data.get('required', True),
                    status=status,
                    details=gate_data.get('details'),
                    threshold=gate_data.get('threshold'),
                    actual_value=gate_data.get('actual_value')
                )
                self.quality_gates.append(gate)
            except Exception as e:
                print(f"Warning: Error parsing quality gate {gate_data.get('name', 'unknown')}: {e}", 
                      file=sys.stderr)
        
        # Load stakeholders
        self.stakeholders = []
        for stakeholder_data in data.get('stakeholders', []):
            stakeholder = Stakeholder(
                name=stakeholder_data['name'],
                role=stakeholder_data['role'],
                contact=stakeholder_data['contact'],
                notification_type=stakeholder_data.get('notification_type', 'email'),
                critical_path=stakeholder_data.get('critical_path', False)
            )
            self.stakeholders.append(stakeholder)
        
        # Load or generate default quality gates if none provided
        if not self.quality_gates:
            self._generate_default_quality_gates()
        
        # Load or generate default rollback steps
        if 'rollback_steps' in data:
            self.rollback_steps = []
            for step_data in data['rollback_steps']:
                risk_level = RiskLevel(step_data.get('risk_level', 'low'))
                step = RollbackStep(
                    order=step_data['order'],
                    description=step_data['description'],
                    command=step_data.get('command'),
                    estimated_time=step_data.get('estimated_time', '5 minutes'),
                    risk_level=risk_level,
                    verification=step_data.get('verification', '')
                )
                self.rollback_steps.append(step)
        else:
            self._generate_default_rollback_steps()
    
    def _generate_default_quality_gates(self):
        """Generate default quality gates."""
        default_gates = [
            {
                'name': 'Unit Test Coverage',
                'required': True,
                'threshold': self.min_test_coverage,
                'details': f'Minimum {self.min_test_coverage}% code coverage required'
            },
            {
                'name': 'Integration Tests',
                'required': True,
                'details': 'All integration tests must pass'
            },
            {
                'name': 'Security Scan',
                'required': True,
                'details': 'No high or critical security vulnerabilities'
            },
            {
                'name': 'Performance Testing',
                'required': True,
                'details': 'Performance metrics within acceptable thresholds'
            },
            {
                'name': 'Documentation Review',
                'required': True,
                'details': 'API docs and user docs updated for new features'
            },
            {
                'name': 'Dependency Audit',
                'required': True,
                'details': 'All dependencies scanned for vulnerabilities'
            }
        ]
        
        self.quality_gates = []
        for gate_data in default_gates:
            gate = QualityGate(
                name=gate_data['name'],
                required=gate_data['required'],
                status=ComponentStatus.PENDING,
                details=gate_data['details'],
                threshold=gate_data.get('threshold')
            )
            self.quality_gates.append(gate)
    
    def _generate_default_rollback_steps(self):
        """Generate default rollback procedure."""
        default_steps = [
            {
                'order': 1,
                'description': 'Alert on-call team and stakeholders',
                'estimated_time': '2 minutes',
                'verification': 'Confirm team is aware and responding'
            },
            {
                'order': 2,
                'description': 'Switch load balancer to previous version',
                'command': 'kubectl patch service app --patch \'{"spec": {"selector": {"version": "previous"}}}\'',
                'estimated_time': '30 seconds',
                'verification': 'Check that traffic is routing to old version'
            },
            {
                'order': 3,
                'description': 'Verify application health after rollback',
                'estimated_time': '5 minutes',
                'verification': 'Check error rates, response times, and health endpoints'
            },
            {
                'order': 4,
                'description': 'Roll back database migrations if needed',
                'command': 'python manage.py migrate app 0001',
                'estimated_time': '10 minutes',
                'risk_level': 'high',
                'verification': 'Verify data integrity and application functionality'
            },
            {
                'order': 5,
                'description': 'Update monitoring dashboards and alerts',
                'estimated_time': '5 minutes',
                'verification': 'Confirm metrics reflect rollback state'
            },
            {
                'order': 6,
                'description': 'Notify stakeholders of successful rollback',
                'estimated_time': '5 minutes',
                'verification': 'All stakeholders acknowledge rollback completion'
            }
        ]
        
        self.rollback_steps = []
        for step_data in default_steps:
            risk_level = RiskLevel(step_data.get('risk_level', 'low'))
            step = RollbackStep(
                order=step_data['order'],
                description=step_data['description'],
                command=step_data.get('command'),
                estimated_time=step_data.get('estimated_time', '5 minutes'),
                risk_level=risk_level,
                verification=step_data.get('verification', '')
            )
            self.rollback_steps.append(step)
    
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
ß^´¶‰ËkºwµçHJBˆˆÈ^\›˜[›İYšXØ][ÛœÂˆ›ÜˆİZÙZÛ\ˆ[ˆ^\›˜[ÜİZÙZÛ\œÎ‚ˆ[–ÉÙ^\›˜[Û›İYšXØ][ÛœÉ×K˜\[™
Âˆ	Ü™XÚ\Y[	ÎˆİZÙZÛ\‹›˜[YKˆ	Ü›ÛIÎˆİZÙZÛ\‹œ›ÛKˆ	ÛY]Ù	ÎˆİZÙZÛ\‹››İYšXØ][Û—İ\Kˆ	ØÛÛ[İ\IÎˆ	İ\Ù\—Ù˜XÚ[™×ØÚ[™Ù\ÉËˆ	İ[Z[™ÉÎˆ	ÕM[™
ÌZ	ÂˆJBˆˆÈÛÛ[][šXØ][Ûˆ[Y[[™BˆYˆÙ[‹\™Ù]Ù]N‚ˆ[Y[[™WÚ][\ÈHÂˆ
[YY[J^\ÏKLŠK	ÔÙ[™™K\™[X\ÙH›İYšXØ][ÛˆÈ^\›˜[İZÙZÛ\œÉÊKˆ
[YY[J^\ÏKLJK	ÔÙ[™\Ş[Y[›İYšXØ][ÛˆÈ[\›˜[X[\ÉÊKˆ
[YY[Jİ\œÏKLŠK	Ñš[˜[ÛËÛ›ËYÛÈXÚ\Ú[Û‰ÊKˆ
[YY[Jİ\œÏL
K	Ğ™YÚ[ˆ\Ş[Y[	ÊKˆ
[YY[Jİ\œÏLJK	ÔÜİY\Ş[Y[İ]\È\]IÊKˆ
[YY[Jİ\œÏL
K	ÔÜİ\™[X\ÙHİ[[X\IÊBˆBˆˆ›Üˆ[K\ØÜš\[Ûˆ[ˆ[Y[[™WÚ][\Î‚ˆ›İYšXØ][Û—İ[YHHÙ[‹\™Ù]Ù]H
È[Bˆ[–Éİ[Y[[™I×K˜\[™
Âˆ	İ[YIÎˆ›İYšXØ][Û—İ[YKš\ÛÙ›Ü›X]

Kˆ	Ù\ØÜš\[Û‰Îˆ\ØÜš\[Û‹ˆ	Ü™XÚ\Y[ÉÎˆ	Ø[	ÈYˆ	Ø[	È[ˆ\ØÜš\[Û‹›İÙ\Š
H[ÙH	Ú[\›˜[	ÂˆJBˆˆÈÛÛ[][šXØ][ÛˆÚ[›™[ÂˆÚ[›™[ÈHßBˆ›ÜˆİZÙZÛ\ˆ[ˆÙ[‹œİZÙZÛ\œÎ‚ˆYˆİZÙZÛ\‹››İYšXØ][Û—İ\H›İ[ˆÚ[›™[Î‚ˆÚ[›™[ÖÜİZÙZÛ\‹››İYšXØ][Û—İ\WHH×BˆÚ[›™[ÖÜİZÙZÛ\‹››İYšXØ][Û—İ\WK˜\[™
İZÙZÛ\‹˜ÛÛXİ
Bˆ[–ÉØÚ[›™[É×HHÚ[›™[ÂˆˆÈY\ÜØYÙH[\]\Âˆ[–Éİ[\]\É×HHÙ[‹—ÙÙ[™\˜]WÛY\ÜØYÙWİ[\]\Ê
Bˆˆ™]\›ˆ[‚ˆˆYˆÙÙ[™\˜]WÛY\ÜØYÙWİ[\]\ÊÙ[ŠHOˆXİ‚ˆˆˆ‘Ù[™\˜]HY\ÜØYÙH[\]\È›ÜˆY™™\™[]YY[˜Ù\Ëˆˆˆ‚ˆœ™XZÚ[™×ØÚ[™Ù\ÈHÙˆ›Üˆˆ[ˆÙ[‹™™X]\™\ÈYˆ‹˜œ™XZÚ[™×ØÚ[™Ù\×Bˆ™]×Ù™X]\™\ÈHÙˆ›Üˆˆ[ˆÙ[‹™™X]\™\ÈYˆ‹\HOH	Ù™X]\™I×BˆY×Ùš^\ÈHÙˆ›Üˆˆ[ˆÙ[‹™™X]\™\ÈYˆ‹\HOH	ØYÙš^	×Bˆˆ[\]\ÈHÂˆ	Ú[\›˜[Ü™WÜ™[X\ÙIÎˆÂˆ	ÜİXš™Xİ	Îˆ‰Ô™[X\ÙHÜÙ[‹™\œÚ[ÛŸHH™KY\Ş[Y[›İYšXØ][Û‰Ëˆ	Ø›ÙIÎˆˆˆˆ•X[K‚•ÙH\™H™\\š[™ÈÈ\ŞHÜÙ[‹œ™[X\ÙWÛ˜[Y_H™\œÚ[ÛˆÜÙ[‹™\œÚ[ÛŸHÛˆÜÙ[‹\™Ù]Ù]Kœİ™[YJ	ÉVKI[KIY	R‰SHUÉÊHYˆÙ[‹\™Ù]Ù]H[ÙH	Õ‘	ßK‚‚’Ù^HÚ[™Ù\Î‚‹HÛ[Š™]×Ù™X]\™\Ê_H™]È™X]\™\Â‹HÛ[ŠY×Ùš^\Ê_HYÈš^\Â‹HÛ[Šœ™XZÚ[™×ØÚ[™Ù\Ê_Hœ™XZÚ[™ÈÚ[™Ù\Â‚”X\ÙH™]šY]ÈH™[X\ÙH›İ\È[™™\\™H›Üˆ[H™YYYİ\ÜXİ]š]Y\Ë‚‚”›Û˜XÚÈ[ˆ]˜Z[X›H[ˆ™[X\ÙHØİ[Y[][Û‚“Û‹XØ[ˆX\ÙH™H]˜Z[X›H\š[™È\Ş[Y[Ú[™İÂ‚™\İ™YØ\™Ë”™[X\ÙHX[Hˆˆ‚ˆKˆ	Ù^\›˜[İ\Ù\—Û›İYšXØ][Û‰ÎˆÂˆ	ÜİXš™Xİ	Îˆ‰Ô›ÙXİ\]HH™\œÚ[ÛˆÜÙ[‹™\œÚ[ÛŸH›İÈ]˜Z[X›IËˆ	Ø›ÙIÎˆˆˆˆ‘X\ˆ\Ù\œË‚•ÙIÜ™H^Ú]YÈ[››İ[˜ÙH™\œÚ[ÛˆÜÙ[‹™\œÚ[ÛŸHÙˆÜÙ[‹œ™[X\ÙWÛ˜[Y_H\È›İÈ]˜Z[X›HB‚•Ú]	ÜÈ™]Î‚ØÚŠL
Kš›Ú[Šˆ‹HÙ‹]_Hˆ›Üˆˆ[ˆ™]×Ù™X]\™\ÖÎWJ_B‚YÈš^\Î‚ØÚŠL
Kš›Ú[Šˆ‹HÙ‹]_Hˆ›Üˆˆ[ˆY×Ùš^\ÖÎŒ×J_B‚ÉÒ[\Ü[ˆ\È™[X\ÙH[˜ÛY\Èœ™XZÚ[™ÈÚ[™Ù\ËˆX\ÙH™]šY]ÈHZYÜ˜][ÛˆİZYK‰ÈYˆœ™XZÚ[™×ØÚ[™Ù\È[ÙH	ÉßB‚‘›Üˆ[™[X\ÙH›İ\È[™ZYÜ˜][Ûˆ[œİXİ[ÛœËš\Ú]İ\ˆØİ[Y[][Û‹‚‚•[šÈ[İH›Üˆ\Ú[™Èİ\ˆ›ÙXİB‚•H]™[ÜY[X[Hˆˆ‚ˆKˆ	Ü›Û˜XÚ×Û›İYšXØ][Û‰ÎˆÂˆ	ÜİXš™Xİ	Îˆ‰ÕT‘ÑS•ˆ™[X\ÙHÜÙ[‹™\œÚ[ÛŸH›Û˜XÚÈ[š]X]Y	Ëˆ	Ø›ÙIÎˆˆˆˆUS•SÓˆ™[X\ÙH›Û˜XÚÈ[ˆ›ÙÜ™\ÜË‚‚”™[X\ÙNˆÜÙ[‹™\œÚ[ÛŸB”™X\ÛÛˆÕÈ‘H’SQB”›Û˜XÚÈ[š]X]YˆÙ]][YK››İÊ
Kœİ™[YJ	ÉVKI[KIY	R‰SHUÉÊ_B‘\İ[X]YÛÛ\][ÛˆÕÈ‘H’SQB‚İ\œ™[İ]\Îˆ›Û[™È˜XÚÈÈ™]š[İ\ÈİX›H™\œÚ[Û‚’[\XİˆÕÈ‘H’SQB‚•ÙHÚ[›İšYH\]\È]™\HMHZ[]\È[[›Û˜XÚÈ\ÈÛÛ\]K‚‚’[˜ÚY[ÛÛ[X[™\ˆÕÈ‘H’SQB”İ]\ÈYÙNˆÕÈ‘H’SQHˆˆ‚ˆBˆBˆˆ™]\›ˆ[\]\ÂˆˆYˆÙ[™\˜]WÜ›Û˜XÚ×Ü[˜›ÛÚÊÙ[ŠHOˆXİ‚ˆˆˆ‘Ù[™\˜]H]Z[Y›Û˜XÚÈ[˜›ÛÚËˆˆˆ‚ˆ[˜›ÛÚÈHÂˆ	Ûİ™\šY]ÉÎˆÂˆ	Ü\œÜÙIÎˆ‰Ñ[Y\™Ù[˜ŞH›Û˜XÚÈ›ØÙY\™H›ÜˆÜÙ[‹œ™[X\ÙWÛ˜[Y_HÜÙ[‹™\œÚ[ÛŸIËˆ	İšYÙÙ\œÉÎˆÂˆ	Ñ\œ›Üˆ˜]HÜZÙH
Œ˜\Ù[[™H›ÜˆŒMHZ[]\ÊIËˆ	ĞÜš]XØ[[˜İ[Û˜[]H˜Z[\™IËˆ	ÔÙXİ\š]H[˜ÚY[	Ëˆ	Ñ]HÛÜœ\[Ûˆ]XİY	Ëˆ	Ô\™›Ü›X[˜ÙHYÜ˜Y][Ûˆ
L	H][˜ŞH[˜Ü™X\ÙJIËˆ	ÓX[X[XÚ\Ú[ÛˆH[˜ÚY[ÛÛ[X[™\‰ÂˆKˆ	ÙXÚ\Ú[Û—ÛXZÙ\œÉÎˆÉÓÛ‹XØ[[™Ú[™Y\‰Ë	Ñ[™Ú[™Y\š[™ÈXY	Ë	Ò[˜ÚY[ÛÛ[X[™\‰×Kˆ	Ù\İ[X]Yİİ[İ[YIÎˆÙ[‹—ØØ[İ[]WÜ›Û˜XÚ×İ[YJ
BˆKˆ	Ü™\™\]Z\Ú]\ÉÎˆÂˆ	ĞÛÛ™š\›H›Û˜XÚÈ\È™XÙ\ÜØ\H
ÚXÚÈÚ][˜ÚY[ÛÛ[X[™\ŠIËˆ	Ó›İYHİZÙZÛ\œÈÙˆ›Û˜XÚÈXÚ\Ú[Û‰Ëˆ	Ñ[œİ\™H]X˜\ÙH˜XÚİ\È\™H]˜Z[X›IËˆ	Õ™\šYH[Ûš]Üš[™ÈŞ\İ[\È\™HÜ\˜][Û˜[	Ëˆ	Ò]™HÛÛ[][šXØ][ÛˆÚ[›™[È™XYIÂˆKˆ	Üİ\ÉÎˆ×Kˆ	İ™\šYšXØ][Û‰ÎˆÂˆ	ÚX[ØÚXÚÜÉÎˆÂˆ	Ğ\XØ][Ûˆ™\ÜÛ™ÈÈX[[™Ú[	Ëˆ	Ñ]X˜\ÙHÛÛ›™Xİ]š]HÛÛ™š\›YY	Ëˆ	Ğ]][XØ][ÛˆŞ\İ[H[˜İ[Û˜[	Ëˆ	ĞÛÜ™H\Ù\ˆÛÜšÙ›İÜÈÛÜšÚ[™ÉËˆ	Ñ\œ›Üˆ˜]\È˜XÚÈÈ˜\Ù[[™IËˆ	Ô\™›Ü›X[˜ÙHY]šXÜÈÚ][ˆ›Ü›X[˜[™ÙIÂˆKˆ	Ü›Û˜XÚ×ØÛÛ™š\›X][Û‰ÎˆÂˆ	Ô™]š[İ\È™\œÚ[Ûˆ[H\ŞYY	Ëˆ	Ñ]X˜\ÙH[ˆÛÛœÚ\İ[İ]IËˆ	Ğ[Ù\šXÙ\ÈÛÛ[][šXØ][™È›Ü\›IËˆ	Ó[Ûš]Üš[™ÈÚİÜÈİX›HY]šXÜÉËˆ	ÔØ[\H\Ù\ˆÛÜšÙ›İÜÈ\İY	ÂˆBˆKˆ	ÜÜİÜ›Û˜XÚÉÎˆÂˆ	Õ\]Hİ]\ÈYÙHÚ]™\ÛÛ][Û‰Ëˆ	Ó›İYH[İZÙZÛ\œÈÙˆİXØÙ\ÜÙ[›Û˜XÚÉËˆ	ÔØÚY[HÜİZ[˜ÚY[™]šY]ÉËˆ	ÑØİ[Y[\ÜİY\È[˜Ûİ[\™Y\š[™È›Û˜XÚÉËˆ	Ô[ˆ[™\İYØ][ÛˆÙˆ›ÛİØ]\ÙIËˆ	Ñ]\›Z[™H[Y[[™H›Üˆ™^™[X\ÙH][\	ÂˆKˆ	Ù[Y\™Ù[˜ŞWØÛÛXİÉÎˆ×BˆBˆˆÈÛÛ™\›Û˜XÚÈİ\ÈÈ]Z[Y›Ü›X]ˆ›Üˆİ\[ˆÛÜY
Ù[‹œ›Û˜XÚ×Üİ\ËÙ^O[[X™Hˆ›Ü™\ŠN‚ˆİ\Ù]HHÂˆ	ÛÜ™\‰Îˆİ\›Ü™\‹ˆ	İ]IÎˆİ\™\ØÜš\[Û‹ˆ	Ù\İ[X]Yİ[YIÎˆİ\™\İ[X]Yİ[YKˆ	Üš\Ú×Û]™[	Îˆİ\œš\Ú×Û]™[˜[YKˆ	Ú[œİXİ[ÛœÉÎˆİ\™\ØÜš\[Û‹ˆ	ØÛÛ[X[™	Îˆİ\˜ÛÛ[X[™ˆ	İ™\šYšXØ][Û‰Îˆİ\™\šYšXØ][Û‹ˆ	Ü›Û˜XÚ×ÜÜÜÚX›IÎˆİ\œš\Ú×Û]™[OHš\ÚÓ]™[Ô’UPĞSˆBˆ[˜›ÛÚÖÉÜİ\É×K˜\[™
İ\Ù]JBˆˆÈY[Y\™Ù[˜ŞHÛÛXİÂˆÜš]XØ[ÜİZÙZÛ\œÈHÜÈ›ÜˆÈ[ˆÙ[‹œİZÙZÛ\œÈYˆË˜Üš]XØ[Ü]Bˆ›ÜˆİZÙZÛ\ˆ[ˆÜš]XØ[ÜİZÙZÛ\œÎ‚ˆ[˜›ÛÚÖÉÙ[Y\™Ù[˜ŞWØÛÛXİÉ×K˜\[™
Âˆ	Û˜[YIÎˆİZÙZÛ\‹›˜[YKˆ	Ü›ÛIÎˆİZÙZÛ\‹œ›ÛKˆ	ØÛÛXİ	ÎˆİZÙZÛ\‹˜ÛÛXİˆ	ÛY]Ù	ÎˆİZÙZÛ\‹››İYšXØ][Û—İ\BˆJBˆˆ™]\›ˆ[˜›ÛÚÂˆˆYˆØØ[İ[]WÜ›Û˜XÚ×İ[YJÙ[ŠHOˆİ‚ˆˆˆØ[İ[]H\İ[X]Yİ[›Û˜XÚÈ[YKˆˆˆ‚ˆİ[ÛZ[]\ÈHˆ›Üˆİ\[ˆÙ[‹œ›Û˜XÚ×Üİ\Î‚ˆÈ\œÙH[YH\İ[X]\ÈZÙHHZ[]\È‹ŒÌÙXÛÛ™È‹ŒHİ\ˆ‚ˆ[YWÜİˆHİ\™\İ[X]Yİ[YK›İÙ\Š
BˆYˆ	ÛZ[]IÈ[ˆ[YWÜİ‚ˆZ[]\ÈH[
™KœÙX\˜Ú
‰Ê
ÊIË[YWÜİŠK™Ü›İ\
JJBˆİ[ÛZ[]\È
ÏHZ[]\Âˆ[Yˆ	Úİ\‰È[ˆ[YWÜİ‚ˆİ\œÈH[
™KœÙX\˜Ú
‰Ê
ÊIË[YWÜİŠK™Ü›İ\
JJBˆİ[ÛZ[]\È
ÏHİ\œÈ
ˆŒˆ[Yˆ	ÜÙXÛÛ™	È[ˆ[YWÜİ‚ˆÈ›İ[™\ÙXÛÛ™ÈÈZ[]\Âˆİ[ÛZ[]\È
ÏHBˆˆYˆİ[ÛZ[]\ÈŒ‚ˆ™]\›ˆˆİİ[ÛZ[]\ßHZ[]\È‚ˆ[ÙN‚ˆİ\œÈHİ[ÛZ[]\ÈËÈŒˆZ[]\ÈHİ[ÛZ[]\È	HŒˆ™]\›ˆˆÚİ\œßZÛZ[]\ß[H‚‚‚™YˆXZ[Š
N‚ˆˆˆ“XZ[ˆÓH[HÚ[ˆˆˆ‚ˆ\œÙ\ˆH\™Ü\œÙK\™İ[Y[\œÙ\Š\ØÜš\[ÛH\ÜÙ\ÜÈ™[X\ÙH™XY[™\ÜÈ[™Ù[™\˜]H™[X\ÙH[œÈŠBˆ\œÙ\‹˜YØ\™İ[Y[
	ËKZ[œ]	Ë	ËZIË™\]Z\™YUYKˆ[IÔ™[X\ÙH[ˆ”ÓÓˆš[IÊBˆ\œÙ\‹˜YØ\™İ[Y[
	ËK[İ]]Y›Ü›X]	Ë	ËY‰ËˆÚÚXÙ\ÏVÉÚœÛÛ‰Ë	ÛX\šÙİÛ‰Ë	İ^	×KˆY˜][Iİ^	Ë[IÓİ]]›Ü›X]	ÊBˆ\œÙ\‹˜YØ\™İ[Y[
	ËK[İ]]	Ë	Ë[ÉË\O\İ‹ˆ[IÓİ]]š[H
Y˜][ˆİİ]
IÊBˆ\œÙ\‹˜YØ\™İ[Y[
	ËKZ[˜ÛYKXÚXÚÛ\İ	ËXİ[ÛIÜİÜ™WİYIËˆ[IÒ[˜ÛYH™[X\ÙHÚXÚÛ\İ[ˆİ]]	ÊBˆ\œÙ\‹˜YØ\™İ[Y[
	ËKZ[˜ÛYKXÛÛ[][šXØ][Û‰ËXİ[ÛIÜİÜ™WİYIËˆ[IÒ[˜ÛYHÛÛ[][šXØ][Ûˆ[‰ÊBˆ\œÙ\‹˜YØ\™İ[Y[
	ËKZ[˜ÛYK\›Û˜XÚÉËXİ[ÛIÜİÜ™WİYIËˆ[IÒ[˜ÛYH›Û˜XÚÈ[˜›ÛÚÉÊBˆ\œÙ\‹˜YØ\™İ[Y[
	ËK[Z[‹XÛİ™\˜YÙIË\OY›Ø]Y˜][NŒˆ[IÓZ[š[][H\İÛİ™\˜YÙH™\ÚÛ	ÊBˆˆ\™ÜÈH\œÙ\‹œ\œÙWØ\™ÜÊ
BˆˆÈØY™[X\ÙH[‚ˆN‚ˆÚ]Ü[Š\™ÜËš[œ]	Ü‰Ë[˜ÛÙ[™ÏIİ]‹N	ÊH\È‚ˆ[—Ù]HH‹œ™XY

Bˆ^Ù\^Ù\[Ûˆ\ÈN‚ˆš[
ˆ‘\œ›Üˆ™XY[™È[œ]š[NˆÙ_H‹š[O\Ş\Ëœİ\œŠBˆŞ\Ë™^]
JBˆˆÈ[š]X[^™H[›™\‚ˆ[›™\ˆH™[X\ÙT[›™\Š
Bˆ[›™\‹›Z[—İ\İØÛİ™\˜YÙHH\™ÜË›Z[—ØÛİ™\˜YÙBˆˆN‚ˆ[›™\‹›ØYÜ™[X\ÙWÜ[Š[—Ù]JBˆ^Ù\^Ù\[Ûˆ\ÈN‚ˆš[
ˆ‘\œ›ÜˆØY[™È™[X\ÙH[ˆÙ_H‹š[O\Ş\Ëœİ\œŠBˆŞ\Ë™^]
JBˆˆÈÙ[™\˜]H\ÜÙ\ÜÛY[ˆ\ÜÙ\ÜÛY[H[›™\‹˜\ÜÙ\Ü×Ü™[X\ÙWÜ™XY[™\ÜÊ
BˆˆÈÙ[™\˜]HÜ[Û˜[ÛÛ\Û™[ÂˆÚXÚÛ\İH[›™\‹™Ù[™\˜]WÜ™[X\ÙWØÚXÚÛ\İ

HYˆ\™ÜËš[˜ÛYWØÚXÚÛ\İ[ÙH›Û™BˆÛÛ[][šXØ][ÛˆH[›™\‹™Ù[™\˜]WØÛÛ[][šXØ][Û—Ü[Š
HYˆ\™ÜËš[˜ÛYWØÛÛ[][šXØ][Ûˆ[ÙH›Û™Bˆ›Û˜XÚÈH[›™\‹™Ù[™\˜]WÜ›Û˜XÚ×Ü[˜›ÛÚÊ
HYˆ\™ÜËš[˜ÛYWÜ›Û˜XÚÈ[ÙH›Û™BˆˆÈÙ[™\˜]Hİ]]ˆYˆ\™ÜË›İ]]Ù›Ü›X]OH	ÚœÛÛ‰Î‚ˆİ]]Ù]HHÂˆ	Ø\ÜÙ\ÜÛY[	Îˆ\ÜÙ\ÜÛY[ˆ	ØÚXÚÛ\İ	ÎˆÚXÚÛ\İˆ	ØÛÛ[][šXØ][Û—Ü[‰ÎˆÛÛ[][šXØ][Û‹ˆ	Ü›Û˜XÚ×Ü[˜›ÛÚÉÎˆ›Û˜XÚÂˆBˆİ]]İ^HœÛÛ‹™[\Êİ]]Ù]K[™[L‹Y˜][\İŠBˆˆ[Yˆ\™ÜË›İ]]Ù›Ü›X]OH	ÛX\šÙİÛ‰Î‚ˆİ]]Û[™\ÈHÂˆˆˆÈ™[X\ÙH™XY[™\ÜÈ™\ÜHÜ[›™\‹œ™[X\ÙWÛ˜[Y_HÜ[›™\‹™\œÚ[ÛŸH‹ˆˆ‹ˆˆŠŠ“İ™\˜[İ]\ÎŠŠˆØ\ÜÙ\ÜÛY[ÉÛİ™\˜[Üİ]\É×K\\Š
_H‹ˆˆŠŠ”™XY[™\ÜÈØÛÜ™NŠŠˆØ\ÜÙ\ÜÛY[ÉÜ™XY[™\Ü×ÜØÛÜ™I×N‹ŒYŸIH‹ˆˆ‚ˆBˆˆYˆ\ÜÙ\ÜÛY[ÉØ›ØÚÚ[™×Ú\ÜİY\É×N‚ˆİ]]Û[™\Ë™^[™
ÂˆˆÈÈ<'æªÈ›ØÚÚ[™È\ÜİY\È‹ˆˆ‚ˆJBˆ›Üˆ\ÜİYH[ˆ\ÜÙ\ÜÛY[ÉØ›ØÚÚ[™×Ú\ÜİY\É×N‚ˆİ]]Û[™\Ë˜\[™
ˆ‹HÚ\ÜİY_HŠBˆİ]]Û[™\Ë˜\[™
ˆŠBˆˆYˆ\ÜÙ\ÜÛY[ÉİØ\›š[™ÜÉ×N‚ˆİ]]Û[™\Ë™^[™
ÂˆˆÈÈ8¦¨;î#ÈØ\›š[™ÜÈ‹ˆˆ‚ˆJBˆ›ÜˆØ\›š[™È[ˆ\ÜÙ\ÜÛY[ÉİØ\›š[™ÜÉ×N‚ˆİ]]Û[™\Ë˜\[™
ˆ‹HİØ\›š[™ßHŠBˆİ]]Û[™\Ë˜\[™
ˆŠBˆˆÈ™X]\™Hİ[[X\BˆœÈH\ÜÙ\ÜÛY[ÉÙ™X]\™WÜİ[[X\I×Bˆİ]]Û[™\Ë™^[™
ÂˆˆÈÈ™X]\™\Èİ[[X\H‹ˆˆ‹ˆˆ‹H
Š•İ[ŠŠˆÙœÖÉİİ[	×_H‹ˆˆ‹H
Š”™XYNŠŠˆÙœÖÉÜ™XYI×_H‹ˆˆ‹H
Š’[ˆ›ÙÜ™\ÜÎŠŠˆÙœÖÉÚ[—Ü›ÙÜ™\ÜÉ×_H‹ˆˆ‹H
Š›ØÚÙYŠŠˆÙœÖÉØ›ØÚÙY	×_H‹ˆˆ‹H
Šœ™XZÚ[™ÈÚ[™Ù\ÎŠŠˆÙœÖÉØœ™XZÚ[™×ØÚ[™Ù\É×_H‹ˆˆ‚ˆJBˆˆYˆÚXÚÛ\İ‚ˆİ]]Û[™\Ë™^[™
ÂˆˆÈÈ™[X\ÙHÚXÚÛ\İ‹ˆˆ‚ˆJBˆİ\œ™[ØØ]YÛÜHHˆ‚ˆ›Üˆ][H[ˆÚXÚÛ\İ‚ˆYˆ][VÉØØ]YÛÜI×HOHİ\œ™[ØØ]YÛÜN‚ˆİ\œ™[ØØ]YÛÜHH][VÉØØ]YÛÜI×Bˆİ]]Û[™\Ë˜\[™
ˆˆÈÈÈØİ\œ™[ØØ]YÛÜ_HŠBˆİ]]Û[™\Ë˜\[™
ˆŠBˆˆİ]\×ÚXÛÛˆH¸§!HˆYˆ][VÉÜİ]\É×HOH	Ü™XYIÈ[ÙH¸§cˆYˆ][VÉÜİ]\É×HOH	Ù˜Z[Y	È[ÙH¸£ìÈ‚ˆİ]]Û[™\Ë˜\[™
ˆ‹HÜİ]\×ÚXÛÛŸHÚ][VÉÚ][I×_HŠBˆİ]]Û[™\Ë˜\[™
ˆŠBˆˆİ]]İ^H	×‰Ëš›Ú[Šİ]]Û[™\ÊBˆˆ[ÙNˆÈ^›Ü›X]ˆİ]]Û[™\ÈHÂˆˆ”™[X\ÙH™XY[™\ÜÈ™\Ü‹ˆˆOOOOOOOOOOOOOOOOOOOOOOOH‹ˆˆ”™[X\ÙNˆÜ[›™\‹œ™[X\ÙWÛ˜[Y_HÜ[›™\‹™\œÚ[ÛŸH‹ˆˆ”İ]\ÎˆØ\ÜÙ\ÜÛY[ÉÛİ™\˜[Üİ]\É×K\\Š
_H‹ˆˆ”™XY[™\ÜÈØÛÜ™NˆØ\ÜÙ\ÜÛY[ÉÜ™XY[™\Ü×ÜØÛÜ™I×N‹ŒYŸIH‹ˆˆ‚ˆBˆˆYˆ\ÜÙ\ÜÛY[ÉØ›ØÚÚ[™×Ú\ÜİY\É×N‚ˆİ]]Û[™\Ë™^[™
È“ĞÒÒS‘ÈTÔÕQTÎˆ‹ˆ—JBˆ›Üˆ\ÜİYH[ˆ\ÜÙ\ÜÛY[ÉØ›ØÚÚ[™×Ú\ÜİY\É×N‚ˆİ]]Û[™\Ë˜\[™
ˆˆ8§cÚ\ÜİY_HŠBˆİ]]Û[™\Ë˜\[™
ˆŠBˆˆYˆ\ÜÙ\ÜÛY[ÉİØ\›š[™ÜÉ×N‚ˆİ]]Û[™\Ë™^[™
È•ĞT“’S‘ÔÎˆ‹ˆ—JBˆ›ÜˆØ\›š[™È[ˆ\ÜÙ\ÜÛY[ÉİØ\›š[™ÜÉ×N‚ˆİ]]Û[™\Ë˜\[™
ˆˆ8¦¨;î#ÈİØ\›š[™ßHŠBˆİ]]Û[™\Ë˜\[™
ˆŠBˆˆYˆ\ÜÙ\ÜÛY[ÉÜ™XÛÛ[Y[™][ÛœÉ×N‚ˆİ]]Û[™\Ë™^[™
È”‘PÓÓSQS‘USÓ”Îˆ‹ˆ—JBˆ›Üˆ™XÈ[ˆ\ÜÙ\ÜÛY[ÉÜ™XÛÛ[Y[™][ÛœÉ×N‚ˆİ]]Û[™\Ë˜\[™
ˆˆ<'ä¨HÜ™XßHŠBˆİ]]Û[™\Ë˜\[™
ˆŠBˆˆÈİ[[X\Hİ]ÂˆœÈH\ÜÙ\ÜÛY[ÉÙ™X]\™WÜİ[[X\I×BˆÜÈH\ÜÙ\ÜÛY[ÉÜ]X[]WÙØ]WÜİ[[X\I×Bˆˆİ]]Û[™\Ë™^[™
Âˆˆ‘‘PUT‘HÕSSPT–Nˆ‹ˆˆˆİ[ˆÙœÖÉİİ[	×_H™XYNˆÙœÖÉÜ™XYI×_H›ØÚÙYˆÙœÖÉØ›ØÚÙY	×_H‹ˆˆˆœ™XZÚ[™ÈÚ[™Ù\ÎˆÙœÖÉØœ™XZÚ[™×ØÚ[™Ù\É×_HZ\ÜÚ[™È\›İ˜[ÎˆÙœÖÉÛZ\ÜÚ[™×Ø\›İ˜[É×_H‹ˆˆ‹ˆˆ”UPSUHĞUTÎˆ‹ˆˆˆİ[ˆÙÜÖÉİİ[	×_H\ÜÙYˆÙÜÖÉÜ\ÜÙY	×_H˜Z[YˆÙÜÖÉÙ˜Z[Y	×_H‹ˆˆ‚ˆJBˆˆİ]]İ^H	×‰Ëš›Ú[Šİ]]Û[™\ÊBˆˆÈÜš]Hİ]]ˆYˆ\™ÜË›İ]]‚ˆÚ]Ü[Š\™ÜË›İ]]	İÉË[˜ÛÙ[™ÏIİ]‹N	ÊH\È‚ˆ‹Üš]Jİ]]İ^
Bˆ[ÙN‚ˆš[
İ]]İ^
B‚‚šYˆ×Û˜[YW×ÈOH	××ÛXZ[—×ÉÎ‚ˆXZ[Š
B