# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import BottleneckAnalysis, ErrorAnalysis, OptimizationRecommendation, PerformanceMetrics  # noqa: F401,E501


class AgentEvaluatorMixin7:
    def generate_optimization_recommendations(self, 
                                            system_metrics: PerformanceMetrics,
                                            error_analyses: List[ErrorAnalysis],
                                            bottlenecks: List[BottleneckAnalysis]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        
        # Performance optimization recommendations
        if system_metrics.success_rate < 0.9:
            recommendations.append(OptimizationRecommendation(
                category="reliability",
                priority="high",
                title="Improve System Reliability",
                description=f"System success rate is {system_metrics.success_rate:.1%}, below target of 90%",
                implementation_effort="medium",
                expected_impact={
                    "success_rate_improvement": min(0.1, 0.95 - system_metrics.success_rate),
                    "cost_reduction": system_metrics.average_cost_per_task * 0.15
                },
                estimated_cost_savings=system_metrics.total_cost_usd * 0.1,
                estimated_performance_gain=1.2,
                implementation_steps=[
                    "Identify and fix top error patterns",
                    "Implement better error handling and retries",
                    "Add comprehensive monitoring and alerting",
                    "Implement graceful degradation patterns"
                ],
                risks=["Temporary increase in complexity", "Potential initial performance overhead"],
                prerequisites=["Error analysis completion", "Monitoring infrastructure"]
            ))
        
        # Cost optimization recommendations
        if system_metrics.average_cost_per_task > 0.1:
            recommendations.append(OptimizationRecommendation(
                category="cost",
                priority="medium",
                title="Optimize Token Usage and Costs",
                description=f"Average cost per task (${system_metrics.average_cost_per_task:.3f}) is above optimal range",
                implementation_effort="low",
                expected_impact={
                    "cost_reduction": system_metrics.average_cost_per_task * 0.3,
                    "efficiency_improvement": 1.15
                },
                estimated_cost_savings=system_metrics.total_cost_usd * 0.3,
                estimated_performance_gain=1.05,
                implementation_steps=[
                    "Implement prompt optimization",
                    "Add response caching for repeated queries",
                    "Use smaller models for simple tasks",
                    "Implement token usage monitoring and alerts"
                ],
                risks=["Potential quality reduction with smaller models"],
                prerequisites=["Token usage analysis", "Caching infrastructure"]
            ))
        
        # Performance optimization recommendations
        if system_metrics.average_duration_ms > 10000:
            recommendations.append(OptimizationRecommendation(
                category="performance",
                priority="high",
                title="Reduce Task Latency",
                description=f"Average task duration ({system_metrics.average_duration_ms/1000:.1f}s) exceeds target",
                implementation_effort="high",
                expected_impact={
                    "latency_reduction": min(0.5, (system_metrics.average_duration_ms - 5000) / system_metrics.average_duration_ms),
                    "throughput_improvement": 1.5
                },
                estimated_performance_gain=1.4,
                implementation_steps=[
                    "Profile and optimize slow operations",
                    "Implement parallel processing where possible",
                    "Add caching for expensive operations",
                    "Optimize API calls and reduce round trips"
                ],
                risks=["Increased system complexity", "Potential resource usage increase"],
                prerequisites=["Performance profiling tools", "Caching infrastructure"]
            ))
        
        # Error-based recommendations
        high_impact_errors = [ea for ea in error_analyses if ea.impact_level == "high"]
        if high_impact_errors:
            for error_analysis in high_impact_errors[:3]:  # Top 3 high impact errors
                recommendations.append(OptimizationRecommendation(
                    category="reliability",
                    priority="high",
                    title=f"Address {error_analysis.error_type.title()} Errors",
                    description=f"{error_analysis.error_type.title()} errors occur in {error_analysis.percentage:.1f}% of cases",
                    implementation_effort="medium",
                    expected_impact={
                        "error_reduction": error_analysis.percentage / 100,
                        "reliability_improvement": 1.1
                    },
                    estimated_cost_savings=system_metrics.total_cost_usd * (error_analysis.percentage / 100) * 0.5,
                    implementation_steps=error_analysis.suggested_fixes,
                    risks=["May require significant code changes"],
                    prerequisites=["Root cause analysis", "Testing framework"]
                ))
        
        # Bottleneck-based recommendations
        critical_bottlenecks = [b for b in bottlenecks if b.severity in ["critical", "high"]]
        for bottleneck in critical_bottlenecks[:2]:  # Top 2 critical bottlenecks
            recommendations.append(OptimizationRecommendation(
                category="performance",
                priority="high" if bottleneck.severity == "critical" else "medium",
                title=f"Address {bottleneck.bottleneck_type.title()} Bottleneck",
                description=bottleneck.description,
                implementation_effort="medium",
                expected_impact=bottleneck.estimated_improvement,
                estimated_performance_gain=list(bottleneck.estimated_improvement.values())[0] if bottleneck.estimated_improvement else 1.1,
                implementation_steps=bottleneck.optimization_suggestions,
                risks=["System downtime during implementation", "Potential cascade effects"],
                prerequisites=["Impact assessment", "Rollback plan"]
            ))
        
        # Scalability recommendations
        if system_metrics.throughput_tasks_per_hour < 20:
            recommendations.append(OptimizationRecommendation(
                category="scalability",
                priority="medium",
                title="Improve System Scalability",
                description="Current throughput indicates potential scalability issues",
                implementation_effort="high",
                expected_impact={
                    "throughput_improvement": 2.0,
                    "scalability_headroom": 5.0
                },
                estimated_performance_gain=2.0,
                implementation_steps=[
                    "Implement horizontal scaling for agents",
                    "Add load balancing and resource pooling",
                    "Optimize resource allocation algorithms",
                    "Implement auto-scaling policies"
                ],
                risks=["High implementation complexity", "Increased operational overhead"],
                prerequisites=["Infrastructure scaling capability", "Monitoring and metrics"]
            ))
        
        # Sort recommendations by priority and impact
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: (
            priority_order[x.priority],
            -x.estimated_performance_gain if x.estimated_performance_gain else 0,
            -x.estimated_cost_savings if x.estimated_cost_savings else 0
        ))
        
        return recommendations
