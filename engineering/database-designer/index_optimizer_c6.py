# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import IndexRecommendation  # noqa: F401,E501


class IndexOptimizerMixin6:
    def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        recommendations = self.analyze_missing_indexes()
        redundancy_issues = self.analyze_redundant_indexes()
        size_estimates = self.estimate_index_sizes()
        
        # Calculate statistics
        total_existing_indexes = sum(len(indexes) for indexes in self.existing_indexes.values())
        tables_analyzed = len(self.tables)
        query_patterns_analyzed = len(self.query_patterns)
        
        # Categorize recommendations by priority
        high_priority = [r for r in recommendations if r.priority <= 2]
        medium_priority = [r for r in recommendations if r.priority == 3]
        low_priority = [r for r in recommendations if r.priority >= 4]
        
        return {
            "analysis_summary": {
                "tables_analyzed": tables_analyzed,
                "query_patterns_analyzed": query_patterns_analyzed,
                "existing_indexes": total_existing_indexes,
                "total_recommendations": len(recommendations),
                "high_priority_recommendations": len(high_priority),
                "redundancy_issues_found": len(redundancy_issues)
            },
            "index_recommendations": {
                "high_priority": [asdict(r) for r in high_priority],
                "medium_priority": [asdict(r) for r in medium_priority],
                "low_priority": [asdict(r) for r in low_priority]
            },
            "redundancy_analysis": [asdict(issue) for issue in redundancy_issues],
            "size_estimates": size_estimates,
            "sql_statements": {
                "create_indexes": [rec.sql_statement for rec in recommendations],
                "drop_redundant": [
                    stmt for issue in redundancy_issues 
                    for stmt in issue.sql_statements
                ]
            },
            "performance_impact": self._generate_performance_impact_analysis(recommendations)
        }
    def _generate_performance_impact_analysis(self, recommendations: List[IndexRecommendation]) -> Dict[str, Any]:
        """Generate performance impact analysis."""
        impact_analysis = {
            "query_optimization": {},
            "write_overhead": {},
            "storage_impact": {}
        }
        
        # Analyze query optimization impact
        query_benefits = defaultdict(list)
        for rec in recommendations:
            for query_id in rec.query_patterns_helped:
                query_benefits[query_id].append(rec.estimated_benefit)
        
        impact_analysis["query_optimization"] = {
            "queries_improved": len(query_benefits),
            "high_impact_queries": len([q for q, benefits in query_benefits.items() 
                                      if any("High" in benefit for benefit in benefits)]),
            "benefit_distribution": dict(Counter(
                rec.estimated_benefit for rec in recommendations
            ))
        }
        
        # Analyze write overhead
        impact_analysis["write_overhead"] = {
            "total_new_indexes": len(recommendations),
            "estimated_insert_overhead": f"{len(recommendations) * 5}%",  # Rough estimate
            "tables_most_affected": list(Counter(rec.table for rec in recommendations).most_common(3))
        }
        
        return impact_analysis
