# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import BottleneckAnalysis, ErrorAnalysis, PerformanceMetrics  # noqa: F401,E501


class AgentEvaluatorMixin10:
    def _assess_overall_health(self, metrics: PerformanceMetrics) -> str:
        """Assess overall system health"""
        health_score = 0
        
        # Success rate contribution (40%)
        if metrics.success_rate >= 0.95:
            health_score += 40
        elif metrics.success_rate >= 0.90:
            health_score += 30
        elif metrics.success_rate >= 0.80:
            health_score += 20
        else:
            health_score += 10
        
        # Performance contribution (30%)
        if metrics.average_duration_ms <= 5000:
            health_score += 30
        elif metrics.average_duration_ms <= 10000:
            health_score += 20
        elif metrics.average_duration_ms <= 30000:
            health_score += 15
        else:
            health_score += 5
        
        # Error rate contribution (20%)
        if metrics.error_rate <= 0.02:
            health_score += 20
        elif metrics.error_rate <= 0.05:
            health_score += 15
        elif metrics.error_rate <= 0.10:
            health_score += 10
        else:
            health_score += 0
        
        # Cost efficiency contribution (10%)
        if metrics.cost_per_token <= 0.00005:
            health_score += 10
        elif metrics.cost_per_token <= 0.0001:
            health_score += 7
        else:
            health_score += 3
        
        if health_score >= 85:
            return "excellent"
        elif health_score >= 70:
            return "good"
        elif health_score >= 50:
            return "fair"
        else:
            return "poor"
    def _extract_key_findings(self, metrics: PerformanceMetrics, 
                            errors: List[ErrorAnalysis],
                            bottlenecks: List[BottleneckAnalysis]) -> List[str]:
        """Extract key findings from analysis"""
        findings = []
        
        # Performance findings
        if metrics.success_rate < 0.9:
            findings.append(f"Success rate ({metrics.success_rate:.1%}) below target")
        
        if metrics.average_duration_ms > 15000:
            findings.append(f"High average latency ({metrics.average_duration_ms/1000:.1f}s)")
        
        # Error findings
        high_impact_errors = [e for e in errors if e.impact_level == "high"]
        if high_impact_errors:
            findings.append(f"{len(high_impact_errors)} high-impact error patterns identified")
        
        # Bottleneck findings
        critical_bottlenecks = [b for b in bottlenecks if b.severity == "critical"]
        if critical_bottlenecks:
            findings.append(f"{len(critical_bottlenecks)} critical bottlenecks found")
        
        # Cost findings
        if metrics.cost_per_token > 0.0001:
            findings.append("Token usage costs above optimal range")
        
        return findings
