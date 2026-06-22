# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from regulatory_pathway_analyzer_base import *  # noqa: F403,E402
from regulatory_pathway_analyzer_p0 import DeviceProfile, PathwayAnalysis  # noqa: F401,E501


class RegulatoryPathwayAnalyzerMixin2:
    def analyze(self, device: DeviceProfile) -> PathwayAnalysis:
        """Perform complete pathway analysis."""
        self.analysis_warnings = []
        pathways = []

        for market in device.target_markets:
            if "FDA" in market or "US" in market:
                pathways.append(self.analyze_fda_pathway(device))
            elif "MDR" in market or "EU" in market:
                pathways.append(self.analyze_eu_mdr_pathway(device))
            # Additional markets can be added here

        sequence = self.determine_optimal_sequence(pathways, device)

        total_timeline_min = sum(p.estimated_timeline_months[0] for p in pathways)
        total_timeline_max = sum(p.estimated_timeline_months[1] for p in pathways)
        total_cost_min = sum(p.estimated_cost_usd[0] for p in pathways)
        total_cost_max = sum(p.estimated_cost_usd[1] for p in pathways)

        csf = [
            "Early engagement with regulators (Pre-Sub/Scientific Advice)",
            "Robust QMS (ISO 13485) in place before submissions",
            "Clinical evidence strategy aligned with target markets",
            "Cybersecurity and software documentation (if applicable)"
        ]

        if device.ai_ml_component:
            csf.append("AI/ML transparency and bias documentation")

        return PathwayAnalysis(
            device=device,
            recommended_pathways=pathways,
            optimal_sequence=sequence,
            total_timeline_months=(total_timeline_min, total_timeline_max),
            total_estimated_cost=(total_cost_min, total_cost_max),
            critical_success_factors=csf,
            warnings=self.analysis_warnings
        )
