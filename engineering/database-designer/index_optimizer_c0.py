# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import Column, Index, QueryPattern  # noqa: F401,E501
from index_optimizer_p1 import SelectivityEstimator  # noqa: F401,E501


class IndexOptimizerMixin0:
    def __init__(self):
        self.tables: Dict[str, Dict[str, Column]] = {}
        self.existing_indexes: Dict[str, List[Index]] = {}
        self.query_patterns: List[QueryPattern] = []
        self.selectivity_estimator = SelectivityEstimator()
        
        # Configuration
        self.max_composite_index_columns = 6
        self.min_selectivity_for_index = 0.1
        self.redundancy_overlap_threshold = 0.8
    def load_schema(self, schema_data: Dict[str, Any]) -> None:
        """Load schema definition."""
        if 'tables' not in schema_data:
            raise ValueError("Schema must contain 'tables' key")
        
        for table_name, table_def in schema_data['tables'].items():
            self.tables[table_name] = {}
            self.existing_indexes[table_name] = []
            
            # Load columns
            for col_name, col_def in table_def.get('columns', {}).items():
                column = Column(
                    name=col_name,
                    data_type=col_def.get('type', 'VARCHAR(255)'),
                    nullable=col_def.get('nullable', True),
                    unique=col_def.get('unique', False),
                    cardinality_estimate=col_def.get('cardinality_estimate')
                )
                self.tables[table_name][col_name] = column
            
            # Load existing indexes
            for idx_def in table_def.get('indexes', []):
                index = Index(
                    name=idx_def['name'],
                    table=table_name,
                    columns=idx_def['columns'],
                    unique=idx_def.get('unique', False),
                    index_type=idx_def.get('type', 'btree'),
                    partial_condition=idx_def.get('partial_condition'),
                    include_columns=idx_def.get('include_columns', [])
                )
                self.existing_indexes[table_name].append(index)
    def load_query_patterns(self, query_data: Dict[str, Any]) -> None:
        """Load query patterns for analysis."""
        if 'queries' not in query_data:
            raise ValueError("Query data must contain 'queries' key")
        
        for query_def in query_data['queries']:
            pattern = QueryPattern(
                query_id=query_def['id'],
                query_type=query_def.get('type', 'SELECT').upper(),
                table=query_def['table'],
                where_conditions=query_def.get('where_conditions', []),
                join_conditions=query_def.get('join_conditions', []),
                order_by=query_def.get('order_by', []),
                group_by=query_def.get('group_by', []),
                frequency=query_def.get('frequency', 1),
                avg_execution_time_ms=query_def.get('avg_execution_time_ms')
            )
            self.query_patterns.append(pattern)
