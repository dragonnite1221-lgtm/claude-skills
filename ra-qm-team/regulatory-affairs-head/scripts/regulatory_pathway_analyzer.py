# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from regulatory_pathway_analyzer_base import *  # noqa: F403,E402
from regulatory_pathway_analyzer_p0 import DeviceProfile, MarketRegion, PathwayAnalysis, PathwayOption, RiskClass  # noqa: F401,E501
from regulatory_pathway_analyzer_p1 import format_analysis_text, interactive_mode  # noqa: F401,E501
from regulatory_pathway_analyzer_p2 import main  # noqa: F401,E501
from regulatory_pathway_analyzer_c0 import RegulatoryPathwayAnalyzerMixin0  # noqa: F401
from regulatory_pathway_analyzer_c1 import RegulatoryPathwayAnalyzerMixin1  # noqa: F401
from regulatory_pathway_analyzer_c2 import RegulatoryPathwayAnalyzerMixin2  # noqa: F401


class RegulatoryPathwayAnalyzer(RegulatoryPathwayAnalyzerMixin0, RegulatoryPathwayAnalyzerMixin1, RegulatoryPathwayAnalyzerMixin2):
    pass


if __name__ == "__main__":
    main()
