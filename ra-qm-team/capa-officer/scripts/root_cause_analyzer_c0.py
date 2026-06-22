# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from root_cause_analyzer_base import *  # noqa: F403,E402
from root_cause_analyzer_p0 import FaultEvent, FishboneCause, RootCauseCategory, WhyStep  # noqa: F401,E501


class RootCauseAnalyzerMixin0:
    """Performs structured root cause analysis."""
    def __init__(self):
        self.analysis_steps = []
        self.findings = []
    def analyze_5why(self, problem: str, whys: List[Dict] = None) -> Dict:
        """Perform 5-Why analysis."""
        steps = []
        if whys:
            for i, w in enumerate(whys, 1):
                steps.append(WhyStep(
                    level=i,
                    question=w.get("question", f"Why did this occur? (Level {i})"),
                    answer=w.get("answer", ""),
                    evidence=w.get("evidence", ""),
                    verified=w.get("verified", False)
                ))

        # Analyze depth and quality
        depth = len(steps)
        has_root = any(
            s.answer and ("system" in s.answer.lower() or "policy" in s.answer.lower() or "process" in s.answer.lower())
            for s in steps
        )

        return {
            "method": "5-Why Analysis",
            "steps": [asdict(s) for s in steps],
            "depth": depth,
            "reached_systemic_cause": has_root,
            "quality_score": min(100, depth * 20 + (20 if has_root else 0))
        }
    def analyze_fishbone(self, problem: str, causes: List[Dict] = None) -> Dict:
        """Perform fishbone (Ishikawa) analysis."""
        categories = {}
        fishbone_causes = []

        if causes:
            for c in causes:
                cat = c.get("category", "Method")
                cause = c.get("cause", "")
                sub = c.get("sub_causes", [])

                if cat not in categories:
                    categories[cat] = []
                categories[cat].append({
                    "cause": cause,
                    "sub_causes": sub,
                    "is_root": c.get("is_root", False),
                    "evidence": c.get("evidence", "")
                })
                fishbone_causes.append(FishboneCause(
                    category=cat,
                    cause=cause,
                    sub_causes=sub,
                    is_root=c.get("is_root", False),
                    evidence=c.get("evidence", "")
                ))

        root_causes = [fc for fc in fishbone_causes if fc.is_root]

        return {
            "method": "Fishbone (Ishikawa) Analysis",
            "problem": problem,
            "categories": categories,
            "total_causes": len(fishbone_causes),
            "root_causes_identified": len(root_causes),
            "categories_covered": list(categories.keys()),
            "recommended_categories": [c.value for c in RootCauseCategory],
            "missing_categories": [c.value for c in RootCauseCategory if c.value.split(" (")[0] not in categories]
        }
    def analyze_fault_tree(self, top_event: str, events: List[Dict] = None) -> Dict:
        """Perform fault tree analysis."""
        fault_events = {}
        if events:
            for e in events:
                fault_events[e["event_id"]] = FaultEvent(
                    event_id=e["event_id"],
                    description=e.get("description", ""),
                    is_basic=e.get("is_basic", True),
                    gate_type=e.get("gate_type", "OR"),
                    children=e.get("children", []),
                    probability=e.get("probability")
                )

        # Find basic events (root causes)
        basic_events = {eid: ev for eid, ev in fault_events.items() if ev.is_basic}
        intermediate_events = {eid: ev for eid, ev in fault_events.items() if not ev.is_basic}

        return {
            "method": "Fault Tree Analysis",
            "top_event": top_event,
            "total_events": len(fault_events),
            "basic_events": len(basic_events),
            "intermediate_events": len(intermediate_events),
            "basic_event_details": [asdict(e) for e in basic_events.values()],
            "cut_sets": self._find_cut_sets(fault_events)
        }
    def _find_cut_sets(self, events: Dict[str, FaultEvent]) -> List[List[str]]:
        """Find minimal cut sets (combinations of basic events that cause top event)."""
        # Simplified cut set analysis
        cut_sets = []
        for eid, event in events.items():
            if not event.is_basic and event.gate_type == "AND":
                cut_sets.append(event.children)
        return cut_sets[:5]  # Return top 5
