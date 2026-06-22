# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import BottleneckAnalysis, ExecutionLog, PerformanceMetrics  # noqa: F401,E501


class AgentEvaluatorMixin5:
    def identify_bottlenecks(self, logs: List[ExecutionLog], 
                           agent_metrics: Dict[str, PerformanceMetrics]) -> List[BottleneckAnalysis]:
        """Identify system bottlenecks"""
        bottlenecks = []
        
        # Agent performance bottlenecks
        for agent_id, metrics in agent_metrics.items():
            if metrics.success_rate < 0.8:
                severity = "critical" if metrics.success_rate < 0.5 else "high"
                bottlenecks.append(BottleneckAnalysis(
                    bottleneck_type="agent",
                    location=agent_id,
                    severity=severity,
                    description=f"Agent {agent_id} has low success rate ({metrics.success_rate:.1%})",
                    impact_on_performance={
                        "success_rate_impact": (0.95 - metrics.success_rate) * 100,
                        "cost_impact": metrics.average_cost_per_task * metrics.failed_tasks
                    },
                    affected_workflows=self._get_agent_workflows(agent_id, logs),
                    optimization_suggestions=[
                        "Review and improve agent logic",
                        "Add better error handling",
                        "Optimize tool usage",
                        "Consider agent specialization"
                    ],
                    estimated_improvement={
                        "success_rate_gain": min(0.15, 0.95 - metrics.success_rate),
                        "cost_reduction": metrics.average_cost_per_task * 0.2
                    }
                ))
            
            if metrics.average_duration_ms > 30000:  # 30 seconds
                severity = "high" if metrics.average_duration_ms > 60000 else "medium"
                bottlenecks.append(BottleneckAnalysis(
                    bottleneck_type="agent",
                    location=agent_id,
                    severity=severity,
                    description=f"Agent {agent_id} has high latency ({metrics.average_duration_ms/1000:.1f}s avg)",
                    impact_on_performance={
                        "latency_impact": metrics.average_duration_ms - 10000,
                        "throughput_impact": max(0, 50 - metrics.total_tasks)
                    },
                    affected_workflows=self._get_agent_workflows(agent_id, logs),
                    optimization_suggestions=[
                        "Profile and optimize slow operations",
                        "Implement caching strategies",
                        "Parallelize independent tasks",
                        "Optimize API calls"
                    ],
                    estimated_improvement={
                        "latency_reduction": min(0.5, (metrics.average_duration_ms - 10000) / metrics.average_duration_ms),
                        "throughput_gain": 1.3
                    }
                ))
        
        # Tool usage bottlenecks
        tool_usage = self._analyze_tool_usage(logs)
        for tool, usage_stats in tool_usage.items():
            if usage_stats.get("error_rate", 0) > 0.2:
                bottlenecks.append(BottleneckAnalysis(
                    bottleneck_type="tool",
                    location=tool,
                    severity="high" if usage_stats["error_rate"] > 0.4 else "medium",
                    description=f"Tool {tool} has high error rate ({usage_stats['error_rate']:.1%})",
                    impact_on_performance={
                        "reliability_impact": usage_stats["error_rate"] * usage_stats["usage_count"],
                        "retry_overhead": usage_stats.get("retry_count", 0) * 1000  # ms
                    },
                    affected_workflows=usage_stats.get("affected_workflows", []),
                    optimization_suggestions=[
                        "Review tool implementation",
                        "Add better error handling for tool",
                        "Implement tool fallbacks",
                        "Consider alternative tools"
                    ],
                    estimated_improvement={
                        "error_reduction": usage_stats["error_rate"] * 0.7,
                        "performance_gain": 1.2
                    }
                ))
        
        # Communication bottlenecks
        communication_analysis = self._analyze_communication_patterns(logs)
        if communication_analysis.get("high_latency_communications", 0) > 5:
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type="communication",
                location="inter_agent_communication",
                severity="medium",
                description="High latency in inter-agent communications detected",
                impact_on_performance={
                    "communication_overhead": communication_analysis.get("avg_communication_latency", 0),
                    "coordination_efficiency": 0.8  # Assumed impact
                },
                affected_workflows=communication_analysis.get("affected_workflows", []),
                optimization_suggestions=[
                    "Optimize message serialization",
                    "Implement message batching",
                    "Add communication caching",
                    "Consider direct communication patterns"
                ],
                estimated_improvement={
                    "communication_latency_reduction": 0.4,
                    "overall_efficiency_gain": 1.15
                }
            ))
        
        # Resource bottlenecks
        resource_analysis = self._analyze_resource_usage(logs)
        if resource_analysis.get("high_token_usage_tasks", 0) > 10:
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type="resource",
                location="token_usage",
                severity="medium",
                description="High token usage detected in multiple tasks",
                impact_on_performance={
                    "cost_impact": resource_analysis.get("excess_token_cost", 0),
                    "latency_impact": resource_analysis.get("token_processing_overhead", 0)
                },
                affected_workflows=resource_analysis.get("high_usage_workflows", []),
                optimization_suggestions=[
                    "Optimize prompt engineering",
                    "Implement response caching",
                    "Use more efficient models for simple tasks",
                    "Add token usage monitoring"
                ],
                estimated_improvement={
                    "cost_reduction": 0.3,
                    "efficiency_gain": 1.1
                }
            ))
        
        # Sort bottlenecks by severity and impact
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        bottlenecks.sort(key=lambda x: (severity_order[x.severity], 
                                       -sum(x.impact_on_performance.values())))
        
        return bottlenecks
