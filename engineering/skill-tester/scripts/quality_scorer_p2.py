# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p1 import QualityReport  # noqa: F401,E501


class QualityReportFormatter:
    """Formats quality reports for output"""
    
    @staticmethod
    def format_json(report: QualityReport) -> str:
        """Format report as JSON"""
        return json.dumps({
            "skill_path": report.skill_path,
            "timestamp": report.timestamp,
            "overall_score": round(report.overall_score, 1),
            "letter_grade": report.letter_grade,
            "tier_recommendation": report.tier_recommendation,
            "summary_stats": report.summary_stats,
            "dimensions": {
                name: {
                    "name": dim.name,
                    "weight": dim.weight,
                    "score": round(dim.score, 1),
                    "description": dim.description,
                    "details": dim.details,
                    "suggestions": dim.suggestions
                }
                for name, dim in report.dimensions.items()
            },
            "improvement_roadmap": report.improvement_roadmap
        }, indent=2)
        
    @staticmethod
    def format_human_readable(report: QualityReport, detailed: bool = False) -> str:
        """Format report as human-readable text"""
        lines = []
        lines.append("=" * 70)
        lines.append("SKILL QUALITY ASSESSMENT REPORT")
        lines.append("=" * 70)
        lines.append(f"Skill: {report.skill_path}")
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append(f"Overall Score: {report.overall_score:.1f}/100 ({report.letter_grade})")
        lines.append(f"Recommended Tier: {report.tier_recommendation}")
        lines.append("")
        
        # Dimension scores
        lines.append("QUALITY DIMENSIONS:")
        for name, dimension in report.dimensions.items():
            lines.append(f"  {name}: {dimension.score:.1f}/100 ({dimension.weight * 100:.0f}% weight)")
            if detailed and dimension.details:
                for component, details in dimension.details.items():
                    lines.append(f"    • {component}: {details['score']:.1f}/{details['max_score']} - {details['details']}")
            lines.append("")
            
        # Summary statistics
        if report.summary_stats:
            lines.append("SUMMARY STATISTICS:")
            lines.append(f"  Highest Dimension: {report.summary_stats['highest_dimension']}")
            lines.append(f"  Lowest Dimension: {report.summary_stats['lowest_dimension']}")
            lines.append(f"  Dimensions Above 70%: {report.summary_stats['dimensions_above_70']}")
            lines.append(f"  Dimensions Below 50%: {report.summary_stats['dimensions_below_50']}")
            lines.append("")
            
        # Improvement roadmap
        if report.improvement_roadmap:
            lines.append("IMPROVEMENT ROADMAP:")
            for i, item in enumerate(report.improvement_roadmap[:5], 1):
                priority_symbol = "🔴" if item["priority"] == "HIGH" else "🟡" if item["priority"] == "MEDIUM" else "🟢"
                lines.append(f"  {i}. {priority_symbol} [{item['dimension']}] {item['suggestion']}")
            lines.append("")
            
        return "\n".join(lines)
