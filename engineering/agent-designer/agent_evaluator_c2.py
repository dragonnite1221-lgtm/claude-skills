# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import ExecutionLog, PerformanceMetrics  # noqa: F401,E501


class AgentEvaluatorMixin2:
    def calculate_performance_metrics(self, logs: List[ExecutionLog]) -> PerformanceMetrics:
        """Calculate performance metrics from execution logs"""
        if not logs:
            return PerformanceMetrics(
                total_tasks=0, successful_tasks=0, failed_tasks=0, partial_tasks=0,
                timeout_tasks=0, success_rate=0.0, failure_rate=0.0,
                average_duration_ms=0.0, median_duration_ms=0.0, percentile_95_duration_ms=0.0,
                min_duration_ms=0, max_duration_ms=0, total_tokens_used=0,
                average_tokens_per_task=0.0, total_cost_usd=0.0, average_cost_per_task=0.0,
                cost_per_token=0.0, throughput_tasks_per_hour=0.0, error_rate=0.0, retry_rate=0.0
            )
        
        total_tasks = len(logs)
        successful_tasks = sum(1 for log in logs if log.status == "success")
        failed_tasks = sum(1 for log in logs if log.status == "failure")
        partial_tasks = sum(1 for log in logs if log.status == "partial")
        timeout_tasks = sum(1 for log in logs if log.status == "timeout")
        
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0.0
        failure_rate = (failed_tasks + timeout_tasks) / total_tasks if total_tasks > 0 else 0.0
        
        durations = [log.duration_ms for log in logs if log.duration_ms > 0]
        if durations:
            average_duration_ms = statistics.mean(durations)
            median_duration_ms = statistics.median(durations)
            percentile_95_duration_ms = self._percentile(durations, 95)
            min_duration_ms = min(durations)
            max_duration_ms = max(durations)
        else:
            average_duration_ms = median_duration_ms = percentile_95_duration_ms = 0.0
            min_duration_ms = max_duration_ms = 0
        
        total_tokens = sum(log.tokens_used.get("total_tokens", 0) for log in logs)
        average_tokens_per_task = total_tokens / total_tasks if total_tasks > 0 else 0.0
        
        total_cost = sum(log.cost_usd for log in logs)
        average_cost_per_task = total_cost / total_tasks if total_tasks > 0 else 0.0
        cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0.0
        
        # Calculate throughput (tasks per hour)
        if logs and len(logs) > 1:
            start_time = min(log.start_time for log in logs if log.start_time)
            end_time = max(log.end_time for log in logs if log.end_time)
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                    time_diff_hours = (end_dt - start_dt).total_seconds() / 3600
                    throughput_tasks_per_hour = total_tasks / time_diff_hours if time_diff_hours > 0 else 0.0
                except:
                    throughput_tasks_per_hour = 0.0
            else:
                throughput_tasks_per_hour = 0.0
        else:
            throughput_tasks_per_hour = 0.0
        
        error_rate = sum(1 for log in logs if log.error_details) / total_tasks if total_tasks > 0 else 0.0
        retry_rate = sum(1 for log in logs if log.retry_count > 0) / total_tasks if total_tasks > 0 else 0.0
        
        return PerformanceMetrics(
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            partial_tasks=partial_tasks,
            timeout_tasks=timeout_tasks,
            success_rate=success_rate,
            failure_rate=failure_rate,
            average_duration_ms=average_duration_ms,
            median_duration_ms=median_duration_ms,
            percentile_95_duration_ms=percentile_95_duration_ms,
            min_duration_ms=min_duration_ms,
            max_duration_ms=max_duration_ms,
            total_tokens_used=total_tokens,
            average_tokens_per_task=average_tokens_per_task,
            total_cost_usd=total_cost,
            average_cost_per_task=average_cost_per_task,
            cost_per_token=cost_per_token,
            throughput_tasks_per_hour=throughput_tasks_per_hour,
            error_rate=error_rate,
            retry_rate=retry_rate
        )
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value from data"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
