# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402
from schema_analyzer_p0 import NamingIssue  # noqa: F401,E501


class SchemaAnalyzerMixin5:
    def _check_table_naming(self, table_name: str) -> None:
        """Check table naming conventions."""
        if not self.table_naming_pattern.match(table_name):
            suggested_name = self._suggest_table_name(table_name)
            self.naming_issues.append(NamingIssue(
                table=table_name,
                column=None,
                issue="Invalid table naming convention",
                current_name=table_name,
                suggested_name=suggested_name
            ))
        
        # Check for plural naming
        if not table_name.endswith('s') and table_name not in ['data', 'information']:
            self.naming_issues.append(NamingIssue(
                table=table_name,
                column=None,
                issue="Table name should be plural",
                current_name=table_name,
                suggested_name=table_name + 's'
            ))
    def _check_column_naming(self, table_name: str, column_name: str) -> None:
        """Check column naming conventions."""
        if not self.column_naming_pattern.match(column_name):
            suggested_name = self._suggest_column_name(column_name)
            self.naming_issues.append(NamingIssue(
                table=table_name,
                column=column_name,
                issue="Invalid column naming convention",
                current_name=column_name,
                suggested_name=suggested_name
            ))
    def _suggest_table_name(self, table_name: str) -> str:
        """Suggest corrected table name."""
        # Convert to snake_case and make plural
        name = re.sub(r'([A-Z])', r'_\1', table_name).lower().strip('_')
        return name + 's' if not name.endswith('s') else name
    def _suggest_column_name(self, column_name: str) -> str:
        """Suggest corrected column name."""
        # Convert to snake_case
        return re.sub(r'([A-Z])', r'_\1', column_name).lower().strip('_')
    def check_missing_indexes(self) -> List[Dict[str, Any]]:
        """Check for missing indexes on foreign key columns."""
        missing_indexes = []
        
        for table_name, table in self.tables.items():
            existing_indexed_columns = set()
            
            # Collect existing indexed columns
            for index in table.indexes:
                existing_indexed_columns.update(index.columns)
            
            # Primary key columns are automatically indexed
            existing_indexed_columns.update(table.primary_key)
            
            # Check foreign key columns
            for column in table.columns:
                if column.foreign_key and column.name not in existing_indexed_columns:
                    missing_indexes.append({
                        'table': table_name,
                        'column': column.name,
                        'type': 'foreign_key',
                        'suggestion': f"CREATE INDEX idx_{table_name}_{column.name} ON {table_name} ({column.name});"
                    })
        
        return missing_indexes
    def generate_mermaid_erd(self) -> str:
        """Generate Mermaid ERD diagram."""
        erd_lines = ["erDiagram"]
        
        # Add table definitions
        for table_name, table in self.tables.items():
            erd_lines.append(f"    {table_name.upper()} {{")
            
            for column in table.columns:
                data_type = column.data_type
                constraints = []
                
                if column.primary_key:
                    constraints.append("PK")
                if column.foreign_key:
                    constraints.append("FK")
                if not column.nullable:
                    constraints.append("NOT NULL")
                if column.unique:
                    constraints.append("UNIQUE")
                
                constraint_str = " ".join(constraints)
                if constraint_str:
                    constraint_str = f" \"{constraint_str}\""
                
                erd_lines.append(f"        {data_type} {column.name}{constraint_str}")
            
            erd_lines.append("    }")
        
        # Add relationships
        relationships = set()
        for table_name, table in self.tables.items():
            for column in table.columns:
                if column.foreign_key:
                    ref_table = column.foreign_key.split('.')[0]
                    if ref_table in self.tables:
                        relationship = f"    {ref_table.upper()} ||--o{{ {table_name.upper()} : has"
                        relationships.add(relationship)
        
        erd_lines.extend(sorted(relationships))
        
        return "\n".join(erd_lines)
