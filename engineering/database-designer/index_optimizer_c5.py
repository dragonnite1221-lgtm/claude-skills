# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import Index, RedundancyIssue  # noqa: F401,E501


class IndexOptimizerMixin5:
    def _find_overlapping_indexes(self, table_name: str, indexes: List[Index]) -> List[RedundancyIssue]:
        """Find overlapping indexes that might be redundant."""
        issues = []
        
        for i, index1 in enumerate(indexes):
            for index2 in indexes[i+1:]:
                overlap_ratio = self._calculate_overlap_ratio(index1, index2)
                
                if overlap_ratio >= self.redundancy_overlap_threshold:
                    # Determine which index to keep
                    if len(index1.columns) <= len(index2.columns):
                        redundant_index = index1
                        keep_index = index2
                    else:
                        redundant_index = index2
                        keep_index = index1
                    
                    issues.append(RedundancyIssue(
                        issue_type="OVERLAPPING",
                        affected_indexes=[index1.name, index2.name],
                        table=table_name,
                        description=f"Index '{redundant_index.name}' overlaps {int(overlap_ratio * 100)}% "
                                   f"with '{keep_index.name}'",
                        recommendation=f"Consider dropping '{redundant_index.name}' as it's largely "
                                     f"covered by '{keep_index.name}'",
                        sql_statements=[f"DROP INDEX {redundant_index.name};"]
                    ))
        
        return issues
    def _calculate_overlap_ratio(self, index1: Index, index2: Index) -> float:
        """Calculate overlap ratio between two indexes."""
        cols1 = set(index1.columns)
        cols2 = set(index2.columns)
        
        if not cols1 or not cols2:
            return 0.0
        
        intersection = len(cols1.intersection(cols2))
        union = len(cols1.union(cols2))
        
        return intersection / union if union > 0 else 0.0
    def _find_unused_indexes(self, table_name: str, indexes: List[Index]) -> List[RedundancyIssue]:
        """Find potentially unused indexes based on query patterns."""
        issues = []
        
        # Collect all columns used in query patterns for this table
        used_columns = set()
        table_patterns = [p for p in self.query_patterns if p.table == table_name]
        
        for pattern in table_patterns:
            # Add WHERE condition columns
            for condition in pattern.where_conditions:
                if condition.get('column'):
                    used_columns.add(condition['column'])
            
            # Add JOIN columns
            for join in pattern.join_conditions:
                if join.get('local_column'):
                    used_columns.add(join['local_column'])
            
            # Add ORDER BY columns
            for order in pattern.order_by:
                if order.get('column'):
                    used_columns.add(order['column'])
            
            # Add GROUP BY columns
            used_columns.update(pattern.group_by)
        
        if not used_columns:
            return issues  # Can't determine usage without query patterns
        
        for index in indexes:
            index_columns = set(index.columns)
            if not index_columns.intersection(used_columns):
                issues.append(RedundancyIssue(
                    issue_type="UNUSED",
                    affected_indexes=[index.name],
                    table=table_name,
                    description=f"Index '{index.name}' columns {index.columns} are not used in any query patterns",
                    recommendation="Consider dropping this index if it's truly unused (verify with query logs)",
                    sql_statements=[f"-- Review usage before dropping\n-- DROP INDEX {index.name};"]
                ))
        
        return issues
    def estimate_index_sizes(self) -> Dict[str, Dict[str, Any]]:
        """Estimate storage requirements for recommended indexes."""
        size_estimates = {}
        
        # This is a simplified estimation - in practice, would need actual table statistics
        for table_name in self.tables:
            size_estimates[table_name] = {
                "estimated_table_rows": 10000,  # Default estimate
                "existing_indexes_size_mb": len(self.existing_indexes.get(table_name, [])) * 5,  # Rough estimate
                "index_overhead_per_column_mb": 2  # Rough estimate per column
            }
        
        return size_estimates
