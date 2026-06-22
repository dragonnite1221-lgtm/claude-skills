# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import EvaluationReport, ExecutionLog  # noqa: F401,E501


class AgentEvaluatorMixin8:
    def generate_report(self, logs: List[ExecutionLog]) -> EvaluationReport:
        """Generate complete evaluation report"""
        
        # Calculate system metrics
        system_metrics = self.calculate_performance_metrics(logs)
        
        # Calculate per-agent metrics
        agents = set(log.agent_id for log in logs)
        agent_metrics = {}
        for agent_id in agents:
            agent_logs = [log for log in logs if log.agent_id == agent_id]
            agent_metrics[agent_id] = self.calculate_performance_metrics(agent_logs)
        
        # Calculate per-task-type metrics
        task_types = set(log.task_type for log in logs)
        task_type_metrics = {}
        for task_type in task_types:
            task_logs = [log for log in logs if log.task_type == task_type]
            task_type_metrics[task_type] = self.calculate_performance_metrics(task_logs)
        
        # Analyze tool usage
        tool_usage_analysis = self._analyze_tool_usage(logs)
        
        # Analyze errors
        error_analysis = self.analyze_errors(logs)
        
        # Identify bottlenecks
        bottleneck_analysis = self.identify_bottlenecks(logs, agent_metrics)
        
        # Generate optimization recommendations
        optimization_recommendations = self.generate_optimization_recommendations(
            system_metrics, error_analysis, bottleneck_analysis)
        
        # Generate trends analysis (simplified)
        trends_analysis = self._generate_trends_analysis(logs)
        
        # Generate cost breakdown
        cost_breakdown = self._generate_cost_breakdown(logs, agent_metrics)
        
        # Check SLA compliance
        sla_compliance = self._check_sla_compliance(system_metrics)
        
        # Create summary
        summary = {
            "evaluation_period": {
                "start_time": min(log.start_time for log in logs if log.start_time) if logs else None,
                "end_time": max(log.end_time for log in logs if log.end_time) if logs else None,
                "total_duration_hours": system_metrics.total_tasks / system_metrics.throughput_tasks_per_hour if system_metrics.throughput_tasks_per_hour > 0 else 0
            },
            "overall_health": self._assess_overall_health(system_metrics),
            "key_findings": self._extract_key_findings(system_metrics, error_analysis, bottleneck_analysis),
            "critical_issues": len([b for b in bottleneck_analysis if b.severity == "critical"]),
            "improvement_opportunities": len(optimization_recommendations)
        }
        
        # Create metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "evaluator_version": "1.0",
            "total_logs_processed": len(logs),
            "agents_analyzed": len(agents),
            "task_types_analyzed": len(task_types),
            "analysis_completeness": "full"
        }
        
        return EvaluationReport(
            summary=summary,
            system_metrics=system_metrics,
            agent_metrics=agent_metrics,
            task_type_metrics=task_type_metrics,
            tool_usage_analysis=tool_usage_analysis,
            error_analysis=error_analysis,
            bottleneck_analysis=bottleneck_analysis,
            optimization_recommendations=optimization_recommendations,
            trends_analysis=trends_analysis,
            cost_breakdown=cost_breakdown,
            sla_compliance=sla_compliance,
            metadata=metadata
        )
