# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from regulatory_pathway_analyzer_base import *  # noqa: F403,E402
from regulatory_pathway_analyzer_p0 import DeviceProfile, PathwayOption  # noqa: F401,E501


class RegulatoryPathwayAnalyzerMixin1:
    def _get_fda_risks(self, pathway: str, device: DeviceProfile) -> List[str]:
        risks = []
        if "510(k)" in pathway:
            risks.extend([
                "Predicate device may be challenged",
                "SE determination can be subjective"
            ])
            if device.software_component:
                risks.append("Software documentation requirements increasing (Cybersecurity, AI/ML)")
        elif "De Novo" in pathway:
            risks.extend([
                "Less predictable than 510(k)",
                "May require more clinical data than expected",
                "New special controls may be imposed"
            ])
        elif "PMA" in pathway:
            risks.extend([
                "Very expensive and time-consuming",
                "Clinical trial risks and delays",
                "Post-approval study requirements"
            ])
        if device.ai_ml_component:
            risks.append("AI/ML components face evolving regulatory requirements")
        return risks
    def _get_eu_advantages(self, pathway: str, device: DeviceProfile) -> List[str]:
        advantages = ["Access to entire EU/EEA market (27+ countries)"]
        if "Self-declaration" in pathway:
            advantages.extend([
                "No Notified Body involvement required",
                "Fastest path to EU market",
                "Lowest cost option"
            ])
        elif "IIa" in pathway:
            advantages.append("Moderate regulatory burden with broad market access")
        elif "IIb" in pathway or "III" in pathway:
            advantages.extend([
                "Strong market credibility with NB certification",
                "Recognized globally for regulatory quality"
            ])
        return advantages
    def _get_eu_risks(self, pathway: str, device: DeviceProfile) -> List[str]:
        risks = []
        if "Self-declaration" not in pathway:
            risks.extend([
                "Limited Notified Body capacity - long wait times",
                "Notified Body costs increasing under MDR"
            ])
        risks.append("MDR transition still creating uncertainty")
        if device.software_component:
            risks.append("EU AI Act may apply to AI/ML medical devices")
        return risks
    def determine_optimal_sequence(self, pathways: List[PathwayOption], device: DeviceProfile) -> List[str]:
        """Determine optimal submission sequence across markets."""
        # General principle: Start with fastest/cheapest, use data for subsequent submissions
        sequence = []

        # Sort by timeline (fastest first)
        sorted_pathways = sorted(pathways, key=lambda p: p.estimated_timeline_months[0])

        # FDA first if 510(k) - well recognized globally
        fda_pathway = next((p for p in pathways if p.market == "US-FDA"), None)
        eu_pathway = next((p for p in pathways if p.market == "EU-MDR"), None)

        if fda_pathway and "510(k)" in fda_pathway.pathway_name:
            sequence.append("1. US-FDA 510(k) first - clearance recognized globally, data reusable")
            if eu_pathway:
                sequence.append("2. EU-MDR - use FDA data in clinical evaluation")
        elif eu_pathway and "Self-declaration" in eu_pathway.pathway_name:
            sequence.append("1. EU-MDR (Class I self-declaration) - fastest market entry")
            if fda_pathway:
                sequence.append("2. US-FDA - use EU experience and data")
        else:
            for i, p in enumerate(sorted_pathways, 1):
                sequence.append(f"{i}. {p.market} ({p.pathway_name})")

        return sequence
