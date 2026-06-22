# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import Index, IndexRecommendation, QueryPattern  # noqa: F401,E501


class IndexOptimizerMixin3:
    def _create_covering_index_recommendation(
        self, 
        table_name: str, 
        where_columns: List[str], 
        pattern: QueryPattern
    ) -> Optional[IndexRecommendation]:
        """Create recommendation for covering index."""
        order_columns = [col['column'] for col in pattern.order_by if col['column'] in self.tables[table_name]]
        
        # Combine WHERE and ORDER BY columns
        index_columns = where_columns.copy()
        include_columns = []
        
        # Add ORDER BY columns to index columns
        for col in order_columns:
            if col not in index_columns:
                index_columns.append(col)
        
        # Limit index columns
        if len(index_columns) > self.max_composite_index_columns:
            include_columns = index_columns[self.max_composite_index_columns:]
            index_columns = index_columns[:self.max_composite_index_columns]
        
        index_name = f"idx_{table_name}_covering_{'_'.join(index_columns[:3])}"
        if len(index_name) > 63:
            index_name = f"idx_{table_name}_covering_{abs(hash('_'.join(index_columns))) % 10000}"
        
        index = Index(
            name=index_name,
            table=table_name,
            columns=index_columns,
            include_columns=include_columns,
            index_type="btree"
        )
        
        reason = f"Covering index for WHERE + ORDER BY optimization"
        
        # Calculate selectivity for main columns
        main_selectivity = 0.5  # Default for covering indexes
        if where_columns:
            selectivities = [
                self.selectivity_estimator.estimate_selectivity(self.tables[table_name][col])
                for col in where_columns[:2]  # Consider first 2 columns
            ]
            main_selectivity = max(selectivities)
        
        sql_parts = [f"CREATE INDEX {index_name} ON {table_name} ({', '.join(index_columns)})"]
        if include_columns:
            sql_parts.append(f" INCLUDE ({', '.join(include_columns)})")
        sql_statement = ''.join(sql_parts) + ";"
        
        return IndexRecommendation(
            recommendation_id=self._generate_recommendation_id(table_name, index_columns, "covering"),
            table=table_name,
            recommended_index=index,
            reason=reason,
            query_patterns_helped=[pattern.query_id],
            estimated_benefit="High (eliminates table lookups for SELECT)",
            estimated_overhead=f"High (covering index with {len(index_columns)} columns)",
            priority=self._calculate_priority(main_selectivity, pattern.frequency, len(index_columns)),
            sql_statement=sql_statement,
            selectivity_analysis={
                "main_columns_selectivity": main_selectivity,
                "covering_benefit": "Eliminates table lookup for SELECT queries"
            }
        )
    def _create_join_index_recommendation(
        self, 
        table_name: str, 
        column: str, 
        pattern: QueryPattern,
        join_condition: Dict[str, Any]
    ) -> Optional[IndexRecommendation]:
        """Create recommendation for JOIN optimization index."""
        column_obj = self.tables[table_name][column]
        selectivity = self.selectivity_estimator.estimate_selectivity(column_obj)
        
        index_name = f"idx_{table_name}_{column}_join"
        index = Index(
            name=index_name,
            table=table_name,
            columns=[column],
            index_type="btree"
        )
        
        foreign_table = join_condition.get('foreign_table', 'unknown')
        reason = f"Optimize JOIN with {foreign_table} table on {column}"
        
        return IndexRecommendation(
            recommendation_id=self._generate_recommendation_id(table_name, [column], "join"),
            table=table_name,
            recommended_index=index,
            reason=reason,
            query_patterns_helped=[pattern.query_id],
            estimated_benefit=self._estimate_join_benefit(pattern.frequency),
            estimated_overhead="Low (single column for JOIN)",
            priority=2,  # JOINs are generally high priority
            sql_statement=f"CREATE INDEX {index_name} ON {table_name} ({column});",
            selectivity_analysis={
                "column_selectivity": selectivity,
                "join_optimization": True
            }
        )
    def _generate_recommendation_id(self, table: str, columns: List[str], suffix: str = "") -> str:
        """Generate unique recommendation ID."""
        content = f"{table}_{'_'.join(sorted(columns))}_{suffix}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
