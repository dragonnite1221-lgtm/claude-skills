# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from regulatory_pathway_analyzer_base import *  # noqa: F403,E402
from regulatory_pathway_analyzer_p0 import DeviceProfile, PathwayOption  # noqa: F401,E501


class RegulatoryPathwayAnalyzerMixin0:
    """Analyzes and recommends regulatory pathways for medical devices."""
    FDA_PATHWAYS = {
        "I": {
            "pathway": "510(k) Exempt / Registration & Listing",
            "timeline": (1, 3),
            "cost": (5000, 15000),
            "requirements": ["Establishment registration", "Device listing", "GMP compliance (if non-exempt)"]
        },
        "II": {
            "pathway": "510(k)",
            "timeline": (6, 12),
            "cost": (50000, 250000),
            "requirements": ["Predicate device identification", "Substantial equivalence demonstration", "Performance testing", "Biocompatibility (if applicable)", "Software documentation (if applicable)"]
        },
        "II-novel": {
            "pathway": "De Novo",
            "timeline": (12, 18),
            "cost": (150000, 400000),
            "requirements": ["Risk-based classification request", "Special controls development", "Performance testing", "Clinical data (potentially)"]
        },
        "III": {
            "pathway": "PMA",
            "timeline": (18, 36),
            "cost": (500000, 2000000),
            "requirements": ["Clinical investigations", "Manufacturing information", "Performance testing", "Risk-benefit analysis", "Post-approval studies"]
        },
        "III-breakthrough": {
            "pathway": "Breakthrough Device Program + PMA",
            "timeline": (12, 24),
            "cost": (500000, 2000000),
            "requirements": ["Breakthrough designation request", "More flexible clinical evidence", "Iterative FDA engagement", "Post-market data collection"]
        }
    }
    EU_MDR_PATHWAYS = {
        "I": {
            "pathway": "Self-declaration (Class I)",
            "timeline": (2, 4),
            "cost": (10000, 30000),
            "requirements": ["Technical documentation", "EU Declaration of Conformity", "UDI assignment", "EUDAMED registration", "Authorized Representative (if non-EU)"]
        },
        "IIa": {
            "pathway": "Notified Body assessment (Class IIa)",
            "timeline": (12, 18),
            "cost": (80000, 200000),
            "requirements": ["QMS certification (ISO 13485)", "Technical documentation", "Clinical evaluation", "Notified Body audit", "Post-market surveillance plan"]
        },
        "IIb": {
            "pathway": "Notified Body assessment (Class IIb)",
            "timeline": (15, 24),
            "cost": (150000, 400000),
            "requirements": ["Full QMS certification", "Comprehensive technical documentation", "Clinical evaluation (may need clinical investigation)", "Type examination or product verification", "Notified Body scrutiny"]
        },
        "III": {
            "pathway": "Notified Body assessment (Class III)",
            "timeline": (18, 30),
            "cost": (300000, 800000),
            "requirements": ["Full QMS certification", "Complete technical documentation", "Clinical investigation (typically required)", "Notified Body clinical evaluation review", "Scrutiny procedure (possible)", "PMCF plan"]
        }
    }
    def __init__(self):
        self.analysis_warnings = []
    def analyze_fda_pathway(self, device: DeviceProfile) -> PathwayOption:
        """Determine optimal FDA pathway."""
        device_class = device.device_class.upper().replace("IIA", "II").replace("IIB", "II")

        if device_class == "I":
            pathway_data = self.FDA_PATHWAYS["I"]
            return PathwayOption(
                pathway_name=pathway_data["pathway"],
                market="US-FDA",
                estimated_timeline_months=pathway_data["timeline"],
                estimated_cost_usd=pathway_data["cost"],
                key_requirements=pathway_data["requirements"],
                advantages=["Fastest path to market", "Minimal regulatory burden", "No premarket submission required (if exempt)"],
                risks=["Limited to exempt product codes", "Still requires GMP compliance"],
                recommendation_level="Recommended"
            )

        elif device_class == "III" or device.implantable or device.life_sustaining:
            if device.novel_technology:
                pathway_data = self.FDA_PATHWAYS["III-breakthrough"]
                rec_level = "Recommended" if device.novel_technology else "Alternative"
            else:
                pathway_data = self.FDA_PATHWAYS["III"]
                rec_level = "Recommended"
        else:  # Class II
            if device.predicate_available and not device.novel_technology:
                pathway_data = self.FDA_PATHWAYS["II"]
                rec_level = "Recommended"
            else:
                pathway_data = self.FDA_PATHWAYS["II-novel"]
                rec_level = "Recommended"

        return PathwayOption(
            pathway_name=pathway_data["pathway"],
            market="US-FDA",
            estimated_timeline_months=pathway_data["timeline"],
            estimated_cost_usd=pathway_data["cost"],
            key_requirements=pathway_data["requirements"],
            advantages=self._get_fda_advantages(pathway_data["pathway"], device),
            risks=self._get_fda_risks(pathway_data["pathway"], device),
            recommendation_level=rec_level
        )
    def analyze_eu_mdr_pathway(self, device: DeviceProfile) -> PathwayOption:
        """Determine optimal EU MDR pathway."""
        device_class = device.device_class.lower().replace("iia", "IIa").replace("iib", "IIb")

        if device_class in ["i", "1"]:
            pathway_data = self.EU_MDR_PATHWAYS["I"]
            class_key = "I"
        elif device_class in ["iia", "2a"]:
            pathway_data = self.EU_MDR_PATHWAYS["IIa"]
            class_key = "IIa"
        elif device_class in ["iib", "2b"]:
            pathway_data = self.EU_MDR_PATHWAYS["IIb"]
            class_key = "IIb"
        else:
            pathway_data = self.EU_MDR_PATHWAYS["III"]
            class_key = "III"

        # Adjust for implantables
        if device.implantable and class_key in ["IIa", "IIb"]:
            pathway_data = self.EU_MDR_PATHWAYS["III"]
            self.analysis_warnings.append(
                f"Implantable devices are typically upclassified to Class III under EU MDR"
            )

        return PathwayOption(
            pathway_name=pathway_data["pathway"],
            market="EU-MDR",
            estimated_timeline_months=pathway_data["timeline"],
            estimated_cost_usd=pathway_data["cost"],
            key_requirements=pathway_data["requirements"],
            advantages=self._get_eu_advantages(pathway_data["pathway"], device),
            risks=self._get_eu_risks(pathway_data["pathway"], device),
            recommendation_level="Recommended"
        )
    def _get_fda_advantages(self, pathway: str, device: DeviceProfile) -> List[str]:
        advantages = []
        if "510(k)" in pathway:
            advantages.extend([
                "Well-established pathway with clear guidance",
                "Predictable review timeline",
                "Lower clinical evidence requirements vs PMA"
            ])
            if device.predicate_available:
                advantages.append("Predicate device identified - streamlined review")
        elif "De Novo" in pathway:
            advantages.extend([
                "Creates new predicate for future 510(k) submissions",
                "Appropriate for novel low-moderate risk devices",
                "Can result in Class I or II classification"
            ])
        elif "PMA" in pathway:
            advantages.extend([
                "Strongest FDA approval - highest market credibility",
                "Difficult for competitors to challenge",
                "May qualify for breakthrough device benefits"
            ])
        elif "Breakthrough" in pathway:
            advantages.extend([
                "Priority review and interactive FDA engagement",
                "Flexible clinical evidence requirements",
                "Faster iterative development with FDA feedback"
            ])
        return advantages
