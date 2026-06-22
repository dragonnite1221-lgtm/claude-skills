# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from migration_planner_base import *  # noqa: F403,E402
from migration_planner_p0 import MigrationPhase  # noqa: F401,E501


class MigrationPlannerMixin1:
    def _calculate_complexity(self, spec: Dict[str, Any]) -> str:
        """Calculate migration complexity based on specification"""
        complexity_score = 0
        
        # Data volume complexity
        data_volume = spec.get("constraints", {}).get("data_volume_gb", 0)
        if data_volume > 10000:
            complexity_score += 3
        elif data_volume > 1000:
            complexity_score += 2
        elif data_volume > 100:
            complexity_score += 1
        
        # System dependencies
        dependencies = len(spec.get("constraints", {}).get("dependencies", []))
        if dependencies > 10:
            complexity_score += 3
        elif dependencies > 5:
            complexity_score += 2
        elif dependencies > 2:
            complexity_score += 1
        
        # Downtime constraints
        max_downtime = spec.get("constraints", {}).get("max_downtime_minutes", 480)
        if max_downtime < 60:
            complexity_score += 3
        elif max_downtime < 240:
            complexity_score += 2
        elif max_downtime < 480:
            complexity_score += 1
        
        # Special requirements
        special_reqs = spec.get("constraints", {}).get("special_requirements", [])
        complexity_score += len(special_reqs)
        
        if complexity_score >= 8:
            return "critical"
        elif complexity_score >= 5:
            return "high"
        elif complexity_score >= 3:
            return "medium"
        else:
            return "low"
    def _estimate_duration(self, migration_type: str, migration_pattern: str, complexity: str) -> int:
        """Estimate migration duration based on type, pattern, and complexity"""
        pattern_info = self.migration_patterns.get(migration_type, {}).get(migration_pattern, {})
        base_duration = pattern_info.get("base_duration", 48)
        multiplier = pattern_info.get("complexity_multiplier", {}).get(complexity, 1.5)
        
        return int(base_duration * multiplier)
    def _generate_phases(self, spec: Dict[str, Any]) -> List[MigrationPhase]:
        """Generate migration phases based on specification"""
        migration_type = spec.get("type")
        migration_pattern = spec.get("pattern", "")
        complexity = self._calculate_complexity(spec)
        
        pattern_info = self.migration_patterns.get(migration_type, {})
        if migration_pattern in pattern_info:
            phase_names = pattern_info[migration_pattern]["phases"]
        else:
            # Default phases based on migration type
            phase_names = {
                "database": ["preparation", "migration", "validation", "cutover"],
                "service": ["preparation", "deployment", "testing", "cutover"],
                "infrastructure": ["assessment", "preparation", "migration", "validation"]
            }.get(migration_type, ["preparation", "execution", "validation", "cleanup"])
        
        phases = []
        total_duration = self._estimate_duration(migration_type, migration_pattern, complexity)
        phase_duration = total_duration // len(phase_names)
        
        for i, phase_name in enumerate(phase_names):
            phase = self._create_phase(phase_name, phase_duration, complexity, i, phase_names)
            phases.append(phase)
        
        return phases
