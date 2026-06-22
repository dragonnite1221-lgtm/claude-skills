# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from agent_evaluator_base import *  # noqa: F403,E402
from agent_evaluator_p0 import ErrorAnalysis, ExecutionLog  # noqa: F401,E501


class AgentEvaluatorMixin3:
    def analyze_errors(self, logs: List[ExecutionLog]) -> List[ErrorAnalysis]:
        """Analyze error patterns in execution logs"""
        error_analyses = []
        
        # Collect all errors
        errors = []
        for log in logs:
            if log.error_details:
                errors.append({
                    "error": log.error_details,
                    "agent_id": log.agent_id,
                    "task_type": log.task_type,
                    "task_id": log.task_id
                })
        
        if not errors:
            return error_analyses
        
        # Group errors by pattern
        error_groups = defaultdict(list)
        unclassified_errors = []
        
        for error in errors:
            error_message = str(error.get("error", {})).lower()
            classified = False
            
            for pattern_name, pattern_info in self.error_patterns.items():
                for pattern in pattern_info["patterns"]:
                    if re.search(pattern, error_message):
                        error_groups[pattern_name].append(error)
                        classified = True
                        break
                if classified:
                    break
            
            if not classified:
                unclassified_errors.append(error)
        
        # Analyze each error group
        total_errors = len(errors)
        
        for error_type, error_list in error_groups.items():
            count = len(error_list)
            percentage = (count / total_errors) * 100 if total_errors > 0 else 0.0
            
            affected_agents = list(set(error["agent_id"] for error in error_list))
            affected_task_types = list(set(error["task_type"] for error in error_list))
            
            # Extract common patterns from error messages
            common_patterns = self._extract_common_patterns([str(e["error"]) for e in error_list])
            
            # Get suggested fixes
            pattern_info = self.error_patterns.get(error_type, {})
            suggested_fixes = pattern_info.get("common_fixes", [])
            
            # Determine impact level
            if percentage > 20 or pattern_info.get("severity") == "critical":
                impact_level = "high"
            elif percentage > 10 or pattern_info.get("severity") == "high":
                impact_level = "medium"
            else:
                impact_level = "low"
            
            error_analysis = ErrorAnalysis(
                error_type=error_type,
                count=count,
                percentage=percentage,
                affected_agents=affected_agents,
                affected_task_types=affected_task_types,
                common_patterns=common_patterns,
                suggested_fixes=suggested_fixes,
                impact_level=impact_level
            )
            
            error_analyses.append(error_analysis)
        
        # Handle unclassified errors
        if unclassified_errors:
            count = len(unclassified_errors)
            percentage = (count / total_errors) * 100
            
            error_analysis = ErrorAnalysis(
                error_type="unclassified",
                count=count,
                percentage=percentage,
                affected_agents=list(set(error["agent_id"] for error in unclassified_errors)),
                affected_task_types=list(set(error["task_type"] for error in unclassified_errors)),
                common_patterns=self._extract_common_patterns([str(e["error"]) for e in unclassified_errors]),
                suggested_fixes=["Review and classify error patterns", "Add specific error handling"],
                impact_level="medium" if percentage > 10 else "low"
            )
            
            error_analyses.append(error_analysis)
        
        # Sort by impact and count
        error_analyses.sort(key=lambda x: (x.impact_level == "high", x.count), reverse=True)
        
        return error_analyses
