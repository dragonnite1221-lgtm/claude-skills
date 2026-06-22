# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import ExecutionLog  # noqa: F401,E501


class AgentEvaluatorMixin1:
    def parse_execution_logs(self, logs_data: List[Dict[str, Any]]) -> List[ExecutionLog]:
        """Parse raw execution logs into structured format"""
        logs = []
        
        for log_entry in logs_data:
            try:
                log = ExecutionLog(
                    task_id=log_entry.get("task_id", ""),
                    agent_id=log_entry.get("agent_id", ""),
                    task_type=log_entry.get("task_type", "unknown"),
                    task_description=log_entry.get("task_description", ""),
                    start_time=log_entry.get("start_time", ""),
                    end_time=log_entry.get("end_time", ""),
                    duration_ms=log_entry.get("duration_ms", 0),
                    status=log_entry.get("status", "unknown"),
                    actions=log_entry.get("actions", []),
                    results=log_entry.get("results", {}),
                    tokens_used=log_entry.get("tokens_used", {"total_tokens": 0}),
                    cost_usd=log_entry.get("cost_usd", 0.0),
                    error_details=log_entry.get("error_details"),
                    tools_used=log_entry.get("tools_used", []),
                    retry_count=log_entry.get("retry_count", 0),
                    metadata=log_entry.get("metadata", {})
                )
                logs.append(log)
            except Exception as e:
                print(f"Warning: Failed to parse log entry: {e}", file=sys.stderr)
                continue
        
        return logs
