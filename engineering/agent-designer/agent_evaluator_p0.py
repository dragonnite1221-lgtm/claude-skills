# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402


@dataclass
class ExecutionLog:
    """Single execution log entry"""
    task_id: str
    agent_id: str
    task_type: str
    task_description: str
    start_time: str
    end_time: str
    duration_ms: int
    status: str  # success, failure, partial, timeout
    actions: List[Dict[str, Any]]
    results: Dict[str, Any]
    tokens_used: Dict[str, int]  # input_tokens, output_tokens, total_tokens
    cost_usd: float
    error_details: Optional[Dict[str, Any]]
    tools_used: List[str]
    retry_count: int
    metadata: Dict[str, Any]


@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent or system"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    partial_tasks: int
    timeout_tasks: int
    success_rate: float
    failure_rate: float
    average_duration_ms: float
    median_duration_ms: float
    percentile_95_duration_ms: float
    min_duration_ms: int
    max_duration_ms: int
    total_tokens_used: int
    average_tokens_per_task: float
    total_cost_usd: float
    average_cost_per_task: float
    cost_per_token: float
    throughput_tasks_per_hour: float
    error_rate: float
    retry_rate: float


@dataclass
class ErrorAnalysis:
    """Error pattern analysis"""
    error_type: str
    count: int
    percentage: float
    affected_agents: List[str]
    affected_task_types: List[str]
    common_patterns: List[str]
    suggested_fixes: List[str]
    impact_level: str  # high, medium, low


@dataclass
class BottleneckAnalysis:
    """System bottleneck analysis"""
    bottleneck_type: str  # agent, tool, communication, resource
    location: str
    severity: str  # critical, high, medium, low
    description: str
    impact_on_performance: Dict[str, float]
    affected_workflows: List[str]
    optimization_suggestions: List[str]
    estimated_improvement: Dict[str, float]


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    category: str  # performance, cost, reliability, scalability
    priority: str  # high, medium, low
    title: str
    description: str
    implementation_effort: str  # low, medium, high
    expected_impact: Dict[str, Any]
    estimated_cost_savings: Optional[float]
    estimated_performance_gain: Optional[float]
    implementation_steps: List[str]
    risks: List[str]
    prerequisites: List[str]


@dataclass
class EvaluationReport:
    """Complete evaluation report"""
    summary: Dict[str, Any]
    system_metrics: PerformanceMetrics
    agent_metrics: Dict[str, PerformanceMetrics]
    task_type_metrics: Dict[str, PerformanceMetrics]
    tool_usage_analysis: Dict[str, Any]
    error_analysis: List[ErrorAnalysis]
    bottleneck_analysis: List[BottleneckAnalysis]
    optimization_recommendations: List[OptimizationRecommendation]
    trends_analysis: Dict[str, Any]
    cost_breakdown: Dict[str, Any]
    sla_compliance: Dict[str, Any]
    metadata: Dict[str, Any]
