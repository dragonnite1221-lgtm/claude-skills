# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import Index, IndexRecommendation, RedundancyIssue  # noqa: F401,E501


class IndexOptimizerMixin4:
    def _estimate_benefit(self, selectivity: float, frequency: int) -> str:
        """Estimate performance benefit of index."""
        if selectivity > 0.8 and frequency > 50:
            return "Very High"
        elif selectivity > 0.6 and frequency > 20:
            return "High"
        elif selectivity > 0.4 or frequency > 10:
            return "Medium"
        else:
            return "Low"
    def _estimate_join_benefit(self, frequency: int) -> str:
        """Estimate benefit for JOIN indexes."""
        if frequency > 50:
            return "Very High (frequent JOINs)"
        elif frequency > 20:
            return "High (regular JOINs)"
        elif frequency > 5:
            return "Medium (occasional JOINs)"
        else:
            return "Low (rare JOINs)"
    def _calculate_priority(self, selectivity: float, frequency: int, column_count: int) -> int:
        """Calculate priority score (1 = highest priority)."""
        # Base score calculation
        score = 0
        
        # Selectivity contribution (0-50 points)
        score += int(selectivity * 50)
        
        # Frequency contribution (0-30 points)
        score += min(frequency, 30)
        
        # Penalty for complex indexes (subtract points)
        score -= (column_count - 1) * 5
        
        # Convert to priority levels
        if score >= 70:
            return 1  # Highest
        elif score >= 50:
            return 2  # High
        elif score >= 30:
            return 3  # Medium
        else:
            return 4  # Low
    def _deduplicate_recommendations(self, recommendations: List[IndexRecommendation]) -> List[IndexRecommendation]:
        """Remove duplicate recommendations."""
        seen_indexes = set()
        unique_recommendations = []
        
        for rec in recommendations:
            index_signature = (rec.table, tuple(rec.recommended_index.columns))
            if index_signature not in seen_indexes:
                seen_indexes.add(index_signature)
                unique_recommendations.append(rec)
            else:
                # Merge query patterns helped
                for existing_rec in unique_recommendations:
                    if (existing_rec.table == rec.table and 
                        existing_rec.recommended_index.columns == rec.recommended_index.columns):
                        existing_rec.query_patterns_helped.extend(rec.query_patterns_helped)
                        break
        
        return unique_recommendations
    def _prioritize_recommendations(self, recommendations: List[IndexRecommendation]) -> List[IndexRecommendation]:
        """Sort recommendations by priority."""
        return sorted(recommendations, key=lambda x: (x.priority, -len(x.query_patterns_helped)))
    def analyze_redundant_indexes(self) -> List[RedundancyIssue]:
        """Identify redundant, overlapping, and potentially unused indexes."""
        redundancy_issues = []
        
        for table_name, indexes in self.existing_indexes.items():
            if len(indexes) < 2:
                continue
            
            # Find duplicate indexes
            duplicates = self._find_duplicate_indexes(table_name, indexes)
            redundancy_issues.extend(duplicates)
            
            # Find overlapping indexes
            overlapping = self._find_overlapping_indexes(table_name, indexes)
            redundancy_issues.extend(overlapping)
            
            # Find potentially unused indexes
            unused = self._find_unused_indexes(table_name, indexes)
            redundancy_issues.extend(unused)
        
        return redundancy_issues
    def _find_duplicate_indexes(self, table_name: str, indexes: List[Index]) -> List[RedundancyIssue]:
        """Find exactly duplicate indexes."""
        issues = []
        seen_signatures = {}
        
        for index in indexes:
            signature = (tuple(index.columns), index.unique, index.partial_condition)
            if signature in seen_signatures:
                existing_index = seen_signatures[signature]
                issues.append(RedundancyIssue(
                    issue_type="DUPLICATE",
                    affected_indexes=[existing_index.name, index.name],
                    table=table_name,
                    description=f"Indexes '{existing_index.name}' and '{index.name}' are identical",
                    recommendation=f"Drop one of the duplicate indexes",
                    sql_statements=[f"DROP INDEX {index.name};"]
                ))
            else:
                seen_signatures[signature] = index
        
        return issues
