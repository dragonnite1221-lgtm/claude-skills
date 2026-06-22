# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402
from schema_analyzer_p0 import Column, DataTypeIssue, NormalizationIssue, Table  # noqa: F401,E501


class SchemaAnalyzerMixin3:
    def _check_third_normal_form(self, table: Table) -> None:
        """Check Third Normal Form compliance."""
        # Look for transitive dependencies
        non_key_columns = [col for col in table.columns if col.name not in table.primary_key]
        
        # Group columns by potential entities they describe
        entity_groups = defaultdict(list)
        for column in non_key_columns:
            # Simple heuristic: group by prefix before underscore
            prefix = column.name.split('_')[0]
            if prefix != column.name:  # Has underscore
                entity_groups[prefix].append(column.name)
        
        for entity, columns in entity_groups.items():
            if len(columns) > 1 and entity != table.name.split('_')[0]:
                # Potential entity that should be in its own table
                id_column = f"{entity}_id"
                if id_column in [col.name for col in table.columns]:
                    self.normalization_issues.append(NormalizationIssue(
                        table=table.name,
                        issue_type="3NF_VIOLATION",
                        severity="MEDIUM",
                        description=f"Columns {columns} may have transitive dependency through '{id_column}'",
                        suggestion=f"Consider creating separate '{entity}' table with these columns",
                        columns_affected=columns + [id_column]
                    ))
    def _check_bcnf(self, table: Table) -> None:
        """Check Boyce-Codd Normal Form compliance."""
        # BCNF violations are complex to detect without functional dependencies
        # Provide general guidance for composite keys
        if len(table.primary_key) > 2:
            self.normalization_issues.append(NormalizationIssue(
                table=table.name,
                issue_type="BCNF_WARNING",
                severity="LOW",
                description=f"Table has composite primary key with {len(table.primary_key)} columns",
                suggestion="Review functional dependencies to ensure BCNF compliance",
                columns_affected=table.primary_key
            ))
    def analyze_data_types(self) -> None:
        """Analyze data type usage for antipatterns."""
        for table_name, table in self.tables.items():
            for column in table.columns:
                self._check_varchar_255_antipattern(table.name, column)
                self._check_inappropriate_types(table.name, column)
                self._check_size_optimization(table.name, column)
    def _check_varchar_255_antipattern(self, table_name: str, column: Column) -> None:
        """Check for VARCHAR(255) antipattern."""
        if self.varchar_255_pattern.match(column.data_type):
            self.datatype_issues.append(DataTypeIssue(
                table=table_name,
                column=column.name,
                current_type=column.data_type,
                issue="VARCHAR(255) antipattern",
                suggested_type="Appropriately sized VARCHAR or TEXT",
                rationale="VARCHAR(255) is often used as default without considering actual data length requirements"
            ))
    def _check_inappropriate_types(self, table_name: str, column: Column) -> None:
        """Check for inappropriate data types."""
        # Date/time stored as string
        if column.name.lower() in ['date', 'time', 'created', 'updated', 'modified', 'timestamp']:
            if column.data_type.upper().startswith(('VARCHAR', 'CHAR', 'TEXT')):
                self.datatype_issues.append(DataTypeIssue(
                    table=table_name,
                    column=column.name,
                    current_type=column.data_type,
                    issue="Date/time stored as string",
                    suggested_type="TIMESTAMP, DATE, or TIME",
                    rationale="Proper date/time types enable date arithmetic and indexing optimization"
                ))
        
        # Boolean stored as string/integer
        if column.name.lower() in ['active', 'enabled', 'deleted', 'visible', 'published']:
            if not column.data_type.upper().startswith('BOOL'):
                self.datatype_issues.append(DataTypeIssue(
                    table=table_name,
                    column=column.name,
                    current_type=column.data_type,
                    issue="Boolean value stored as non-boolean type",
                    suggested_type="BOOLEAN",
                    rationale="Boolean type is more explicit and can be more storage efficient"
                ))
        
        # Numeric IDs as VARCHAR
        if column.name.lower().endswith('_id') or column.name.lower() == 'id':
            if column.data_type.upper().startswith(('VARCHAR', 'CHAR')):
                self.datatype_issues.append(DataTypeIssue(
                    table=table_name,
                    column=column.name,
                    current_type=column.data_type,
                    issue="Numeric ID stored as string",
                    suggested_type="INTEGER, BIGINT, or UUID",
                    rationale="Numeric types are more efficient for ID columns and enable better indexing"
                ))
    def _check_size_optimization(self, table_name: str, column: Column) -> None:
        """Check for size optimization opportunities."""
        # Oversized integer types
        if column.data_type.upper() == 'BIGINT':
            if not any(keyword in column.name.lower() for keyword in ['timestamp', 'big', 'large', 'count']):
                self.datatype_issues.append(DataTypeIssue(
                    table=table_name,
                    column=column.name,
                    current_type=column.data_type,
                    issue="Potentially oversized integer type",
                    suggested_type="INTEGER",
                    rationale="INTEGER is sufficient for most ID and count fields unless very large values are expected"
                ))
