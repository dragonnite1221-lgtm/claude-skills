# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402


class IndexOptimizerMixin7:
    def format_text_report(self, analysis: Dict[str, Any]) -> str:
        """Format analysis as human-readable text report."""
        lines = []
        lines.append("DATABASE INDEX OPTIMIZATION REPORT")
        lines.append("=" * 50)
        lines.append("")
        
        # Summary
        summary = analysis["analysis_summary"]
        lines.append("ANALYSIS SUMMARY")
        lines.append("-" * 16)
        lines.append(f"Tables Analyzed: {summary['tables_analyzed']}")
        lines.append(f"Query Patterns: {summary['query_patterns_analyzed']}")
        lines.append(f"Existing Indexes: {summary['existing_indexes']}")
        lines.append(f"New Recommendations: {summary['total_recommendations']}")
        lines.append(f"High Priority: {summary['high_priority_recommendations']}")
        lines.append(f"Redundancy Issues: {summary['redundancy_issues_found']}")
        lines.append("")
        
        # High Priority Recommendations
        high_priority = analysis["index_recommendations"]["high_priority"]
        if high_priority:
            lines.append(f"HIGH PRIORITY RECOMMENDATIONS ({len(high_priority)})")
            lines.append("-" * 35)
            for i, rec in enumerate(high_priority[:10], 1):  # Show top 10
                lines.append(f"{i}. {rec['table']}: {rec['reason']}")
                lines.append(f"   Columns: {', '.join(rec['recommended_index']['columns'])}")
                lines.append(f"   Benefit: {rec['estimated_benefit']}")
                lines.append(f"   SQL: {rec['sql_statement']}")
                lines.append("")
        
        # Redundancy Issues
        redundancy = analysis["redundancy_analysis"]
        if redundancy:
            lines.append(f"REDUNDANCY ISSUES ({len(redundancy)})")
            lines.append("-" * 20)
            for issue in redundancy[:5]:  # Show first 5
                lines.append(f"• {issue['issue_type']}: {issue['description']}")
                lines.append(f"  Recommendation: {issue['recommendation']}")
                if issue['sql_statements']:
                    lines.append(f"  SQL: {issue['sql_statements'][0]}")
                lines.append("")
        
        # Performance Impact
        perf_impact = analysis["performance_impact"]
        lines.append("PERFORMANCE IMPACT ANALYSIS")
        lines.append("-" * 30)
        query_opt = perf_impact["query_optimization"]
        lines.append(f"Queries to be optimized: {query_opt['queries_improved']}")
        lines.append(f"High impact optimizations: {query_opt['high_impact_queries']}")
        
        write_overhead = perf_impact["write_overhead"]
        lines.append(f"Estimated insert overhead: {write_overhead['estimated_insert_overhead']}")
        lines.append("")
        
        # SQL Statements Summary
        sql_statements = analysis["sql_statements"]
        create_statements = sql_statements["create_indexes"]
        if create_statements:
            lines.append("RECOMMENDED CREATE INDEX STATEMENTS")
            lines.append("-" * 36)
            for i, stmt in enumerate(create_statements[:10], 1):
                lines.append(f"{i}. {stmt}")
            
            if len(create_statements) > 10:
                lines.append(f"... and {len(create_statements) - 10} more")
            lines.append("")
        
        return "\n".join(lines)
