# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402
from schema_analyzer_p0 import Column, NormalizationIssue, Table  # noqa: F401,E501


class SchemaAnalyzerMixin2:
    def parse_json_schema(self, json_content: str) -> None:
        """Parse JSON schema definition."""
        try:
            schema = json.loads(json_content)
            
            if 'tables' not in schema:
                raise ValueError("JSON schema must contain 'tables' key")
            
            for table_name, table_def in schema['tables'].items():
                table = self._parse_json_table(table_name.lower(), table_def)
                self.tables[table_name.lower()] = table
                
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    def _parse_json_table(self, table_name: str, table_def: Dict[str, Any]) -> Table:
        """Parse JSON table definition."""
        columns = []
        primary_key = table_def.get('primary_key', [])
        foreign_keys = []
        unique_constraints = table_def.get('unique_constraints', [])
        check_constraints = table_def.get('check_constraints', {})
        
        for col_name, col_def in table_def.get('columns', {}).items():
            column = Column(
                name=col_name.lower(),
                data_type=col_def.get('type', 'VARCHAR(255)').upper(),
                nullable=col_def.get('nullable', True),
                primary_key=col_name.lower() in [pk.lower() for pk in primary_key],
                unique=col_def.get('unique', False),
                foreign_key=col_def.get('foreign_key'),
                default_value=col_def.get('default')
            )
            
            columns.append(column)
            
            if column.foreign_key:
                foreign_keys.append((column.name, column.foreign_key))
        
        return Table(
            name=table_name,
            columns=columns,
            primary_key=[pk.lower() for pk in primary_key],
            foreign_keys=foreign_keys,
            unique_constraints=unique_constraints,
            check_constraints=check_constraints,
            indexes=[]
        )
    def analyze_normalization(self) -> None:
        """Analyze normalization compliance."""
        for table_name, table in self.tables.items():
            self._check_first_normal_form(table)
            self._check_second_normal_form(table)
            self._check_third_normal_form(table)
            self._check_bcnf(table)
    def _check_first_normal_form(self, table: Table) -> None:
        """Check First Normal Form compliance."""
        # Check for atomic values (no arrays or delimited strings)
        for column in table.columns:
            if any(pattern in column.data_type.upper() for pattern in ['ARRAY', 'JSON', 'TEXT']):
                if 'JSON' in column.data_type.upper():
                    # JSON columns can violate 1NF if storing arrays
                    self.normalization_issues.append(NormalizationIssue(
                        table=table.name,
                        issue_type="1NF_VIOLATION",
                        severity="WARNING",
                        description=f"Column '{column.name}' uses JSON type which may contain non-atomic values",
                        suggestion="Consider normalizing JSON arrays into separate tables",
                        columns_affected=[column.name]
                    ))
            
            # Check for potential delimited values in VARCHAR/TEXT
            if column.data_type.upper().startswith(('VARCHAR', 'CHAR', 'TEXT')):
                if any(delimiter in column.name.lower() for delimiter in ['list', 'array', 'tags', 'items']):
                    self.normalization_issues.append(NormalizationIssue(
                        table=table.name,
                        issue_type="1NF_VIOLATION",
                        severity="HIGH",
                        description=f"Column '{column.name}' appears to store delimited values",
                        suggestion="Create separate table for individual values with foreign key relationship",
                        columns_affected=[column.name]
                    ))
    def _check_second_normal_form(self, table: Table) -> None:
        """Check Second Normal Form compliance."""
        if len(table.primary_key) <= 1:
            return  # 2NF only applies to tables with composite primary keys
        
        # Look for potential partial dependencies
        non_key_columns = [col for col in table.columns if col.name not in table.primary_key]
        
        for column in non_key_columns:
            # Heuristic: columns that seem related to only part of the composite key
            for pk_part in table.primary_key:
                if pk_part in column.name or column.name.startswith(pk_part.split('_')[0]):
                    self.normalization_issues.append(NormalizationIssue(
                        table=table.name,
                        issue_type="2NF_VIOLATION",
                        severity="MEDIUM",
                        description=f"Column '{column.name}' may have partial dependency on '{pk_part}'",
                        suggestion=f"Consider moving '{column.name}' to a separate table related to '{pk_part}'",
                        columns_affected=[column.name, pk_part]
                    ))
                    break
