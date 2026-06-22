# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from root_cause_analyzer_base import *  # noqa: F403,E402
from root_cause_analyzer_p0 import RootCauseAnalysis, RootCauseFinding  # noqa: F401,E501


class RootCauseAnalyzerMixin2:
    def full_analysis(
        self,
        problem: str,
        method: str = "5-Why",
        analysis_data: Dict = None
    ) -> RootCauseAnalysis:
        """Perform complete root cause analysis."""
        investigation_id = f"RCA-{datetime.now().strftime('%Y%m%d-%H%M')}"
        analysis_details = {}
        root_causes = []

        if method == "5-Why" and analysis_data:
            analysis_details = self.analyze_5why(problem, analysis_data.get("whys", []))
            # Extract root cause from deepest why
            steps = analysis_details.get("steps", [])
            if steps:
                last_step = steps[-1]
                root_causes.append(RootCauseFinding(
                    cause_id="RC-001",
                    description=last_step.get("answer", "Unknown"),
                    category="Systemic",
                    evidence=[s.get("evidence", "") for s in steps if s.get("evidence")],
                    systemic=analysis_details.get("reached_systemic_cause", False)
                ))

        elif method == "Fishbone" and analysis_data:
            analysis_details = self.analyze_fishbone(problem, analysis_data.get("causes", []))
            for i, cat in enumerate(analysis_data.get("causes", [])):
                if cat.get("is_root"):
                    root_causes.append(RootCauseFinding(
                        cause_id=f"RC-{i+1:03d}",
                        description=cat.get("cause", ""),
                        category=cat.get("category", ""),
                        evidence=[cat.get("evidence", "")] if cat.get("evidence") else [],
                        sub_causes=cat.get("sub_causes", []),
                        systemic=True
                    ))

        recommendations = self.generate_recommendations(root_causes, problem)

        # Confidence based on evidence and method
        confidence = 0.7
        if root_causes and any(rc.evidence for rc in root_causes):
            confidence = 0.85
        if len(root_causes) > 1:
            confidence = min(0.95, confidence + 0.05)

        return RootCauseAnalysis(
            investigation_id=investigation_id,
            problem_statement=problem,
            analysis_method=method,
            root_causes=root_causes,
            recommendations=recommendations,
            analysis_details=analysis_details,
            confidence_level=confidence
        )
