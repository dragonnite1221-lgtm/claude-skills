# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import IndexRecommendation  # noqa: F401,E501


class IndexOptimizerMixin1:
    def analyze_missing_indexes(self) -> List[IndexRecommendation]:
        """Identify missing indexes based on query patterns."""
        recommendations = []
        
        for pattern in self.query_patterns:
            table_name = pattern.table
            if table_name not in self.tables:
                continue
            
            # Analyze WHERE conditions for single-column indexes
            for condition in pattern.where_conditions:
                column = condition.get('column')
                operator = condition.get('operator', '=')
                
                if column and column in self.tables[table_name]:
                    if not self._has_covering_index(table_name, [column]):
                        recommendation = self._create_single_column_recommendation(
                            table_name, column, pattern, operator
                        )
                        if recommendation:
                            recommendations.append(recommendation)
            
            # Analyze composite indexes for multi-column WHERE conditions
            where_columns = [cond.get('column') for cond in pattern.where_conditions 
                           if cond.get('column') and cond.get('column') in self.tables[table_name]]
            
            if len(where_columns) > 1:
                composite_recommendation = self._create_composite_recommendation(
                    table_name, where_columns, pattern
                )
                if composite_recommendation:
                    recommendations.append(composite_recommendation)
            
            # Analyze covering indexes for SELECT with ORDER BY
            if pattern.order_by and where_columns:
                covering_recommendation = self._create_covering_index_recommendation(
                    table_name, where_columns, pattern
                )
                if covering_recommendation:
                    recommendations.append(covering_recommendation)
            
            # Analyze JOIN conditions
            for join_condition in pattern.join_conditions:
                local_column = join_condition.get('local_column')
                if local_column and local_column in self.tables[table_name]:
                    if not self._has_covering_index(table_name, [local_column]):
                        recommendation = self._create_join_index_recommendation(
                            table_name, local_column, pattern, join_condition
                        )
                        if recommendation:
                            recommendations.append(recommendation)
        
        # Remove duplicates and prioritize
        recommendations = self._deduplicate_recommendations(recommendations)
        recommendations = self._prioritize_recommendations(recommendations)
        
        return recommendations
    def _has_covering_index(self, table_name: str, columns: List[str]) -> bool:
        """Check if existing indexes cover the specified columns."""
        if table_name not in self.existing_indexes:
            return False
        
        for index in self.existing_indexes[table_name]:
            # Check if index starts with required columns (prefix match for composite)
            if len(index.columns) >= len(columns):
                if index.columns[:len(columns)] == columns:
                    return True
        
        return False
