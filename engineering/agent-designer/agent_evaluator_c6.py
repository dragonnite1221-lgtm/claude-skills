# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import ExecutionLog  # noqa: F401,E501


class AgentEvaluatorMixin6:
    def _get_agent_workflows(self, agent_id: str, logs: List[ExecutionLog]) -> List[str]:
        """Get workflows affected by a specific agent"""
        workflows = set()
        for log in logs:
            if log.agent_id == agent_id:
                workflows.add(log.task_type)
        return list(workflows)
    def _analyze_tool_usage(self, logs: List[ExecutionLog]) -> Dict[str, Dict[str, Any]]:
        """Analyze tool usage patterns"""
        tool_stats = defaultdict(lambda: {
            "usage_count": 0,
            "error_count": 0,
            "total_duration": 0,
            "affected_workflows": set(),
            "retry_count": 0
        })
        
        for log in logs:
            for tool in log.tools_used:
                stats = tool_stats[tool]
                stats["usage_count"] += 1
                stats["total_duration"] += log.duration_ms
                stats["affected_workflows"].add(log.task_type)
                
                if log.error_details:
                    stats["error_count"] += 1
                if log.retry_count > 0:
                    stats["retry_count"] += log.retry_count
        
        # Calculate derived metrics
        result = {}
        for tool, stats in tool_stats.items():
            result[tool] = {
                "usage_count": stats["usage_count"],
                "error_rate": stats["error_count"] / stats["usage_count"] if stats["usage_count"] > 0 else 0,
                "avg_duration": stats["total_duration"] / stats["usage_count"] if stats["usage_count"] > 0 else 0,
                "affected_workflows": list(stats["affected_workflows"]),
                "retry_count": stats["retry_count"]
            }
        
        return result
    def _analyze_communication_patterns(self, logs: List[ExecutionLog]) -> Dict[str, Any]:
        """Analyze communication patterns between agents"""
        # This is a simplified analysis - in a real system, you'd have more detailed communication logs
        communication_actions = []
        for log in logs:
            for action in log.actions:
                if action.get("type") in ["message", "delegate", "coordinate", "respond"]:
                    communication_actions.append({
                        "duration": action.get("duration_ms", 0),
                        "success": action.get("success", True),
                        "workflow": log.task_type
                    })
        
        if not communication_actions:
            return {}
        
        avg_latency = sum(action["duration"] for action in communication_actions) / len(communication_actions)
        high_latency_count = sum(1 for action in communication_actions if action["duration"] > 5000)
        
        return {
            "total_communications": len(communication_actions),
            "avg_communication_latency": avg_latency,
            "high_latency_communications": high_latency_count,
            "affected_workflows": list(set(action["workflow"] for action in communication_actions))
        }
    def _analyze_resource_usage(self, logs: List[ExecutionLog]) -> Dict[str, Any]:
        """Analyze resource usage patterns"""
        token_usage = [log.tokens_used.get("total_tokens", 0) for log in logs]
        
        if not token_usage:
            return {}
        
        avg_tokens = sum(token_usage) / len(token_usage)
        high_usage_threshold = avg_tokens * 2
        high_usage_tasks = sum(1 for tokens in token_usage if tokens > high_usage_threshold)
        
        # Estimate excess cost
        excess_tokens = sum(max(0, tokens - avg_tokens) for tokens in token_usage)
        excess_cost = excess_tokens * 0.00002  # Rough estimate
        
        return {
            "avg_token_usage": avg_tokens,
            "high_token_usage_tasks": high_usage_tasks,
            "excess_token_cost": excess_cost,
            "token_processing_overhead": high_usage_tasks * 500,  # Estimated overhead in ms
            "high_usage_workflows": [log.task_type for log in logs 
                                   if log.tokens_used.get("total_tokens", 0) > high_usage_threshold]
        }
