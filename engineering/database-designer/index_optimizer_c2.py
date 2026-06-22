# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import Index, IndexRecommendation, QueryPattern  # noqa: F401,E501


class IndexOptimizerMixin2:
    def _create_single_column_recommendation(
        self, 
        table_name: str, 
        column: str, 
        pattern: QueryPattern,
        operator: str
    ) -> Optional[IndexRecommendation]:
        """Create recommendation for single-column index."""
        column_obj = self.tables[table_name][column]
        selectivity = self.selectivity_estimator.estimate_selectivity(column_obj)
        
        # Skip very low selectivity columns unless frequently used
        if selectivity < self.min_selectivity_for_index and pattern.frequency < 100:
            return None
        
        index_name = f"idx_{table_name}_{column}"
        index = Index(
            name=index_name,
            table=table_name,
            columns=[column],
            unique=column_obj.unique,
            index_type="btree"
        )
        
        reason = f"Optimize WHERE {column} {operator} queries"
        if pattern.frequency > 10:
            reason += f" (used {pattern.frequency} times)"
        
        return IndexRecommendation(
            recommendation_id=self._generate_recommendation_id(table_name, [column]),
            table=table_name,
            recommended_index=index,
            reason=reason,
            query_patterns_helped=[pattern.query_id],
            estimated_benefit=self._estimate_benefit(selectivity, pattern.frequency),
            estimated_overhead="Low (single column)",
            priority=self._calculate_priority(selectivity, pattern.frequency, 1),
            sql_statement=f"CREATE INDEX {index_name} ON {table_name} ({column});",
            selectivity_analysis={
                "column_selectivity": selectivity,
                "estimated_reduction": f"{int(selectivity * 100)}%"
            }
        )
    def _create_composite_recommendation(
        self, 
        table_name: str, 
        columns: List[str], 
        pattern: QueryPattern
    ) -> Optional[IndexRecommendation]:
        """Create recommendation for composite index."""
        if len(columns) > self.max_composite_index_columns:
            columns = columns[:self.max_composite_index_columns]
        
        # Order columns by selectivity (most selective first)
        column_selectivities = []
        for col in columns:
            col_obj = self.tables[table_name][col]
            selectivity = self.selectivity_estimator.estimate_selectivity(col_obj)
            column_selectivities.append((col, selectivity))
        
        # Sort by selectivity descending
        column_selectivities.sort(key=lambda x: x[1], reverse=True)
        ordered_columns = [col for col, _ in column_selectivities]
        
        # Calculate combined selectivity
        combined_selectivity = min(sum(sel for _, sel in column_selectivities) / len(columns), 0.95)
        
        index_name = f"idx_{table_name}_{'_'.join(ordered_columns)}"
        if len(index_name) > 63:  # PostgreSQL limit
            index_name = f"idx_{table_name}_composite_{abs(hash('_'.join(ordered_columns))) % 10000}"
        
        index = Index(
            name=index_name,
            table=table_name,
            columns=ordered_columns,
            index_type="btree"
        )
        
        reason = f"Optimize multi-column WHERE conditions: {', '.join(ordered_columns)}"
        
        return IndexRecommendation(
            recommendation_id=self._generate_recommendation_id(table_name, ordered_columns),
            table=table_name,
            recommended_index=index,
            reason=reason,
            query_patterns_helped=[pattern.query_id],
            estimated_benefit=self._estimate_benefit(combined_selectivity, pattern.frequency),
            estimated_overhead=f"Medium (composite index with {len(ordered_columns)} columns)",
            priority=self._calculate_priority(combined_selectivity, pattern.frequency, len(ordered_columns)),
            sql_statement=f"CREATE INDEX {index_name} ON {table_name} ({', '.join(ordered_columns)});",
            selectivity_analysis={
                "column_selectivities": {col: sel for col, sel in column_selectivities},
                "combined_selectivity": combined_selectivity,
                "column_order_rationale": "Ordered by selectivity (most selective first)"
            }
        )
