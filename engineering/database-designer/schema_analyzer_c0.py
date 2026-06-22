# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402
from schema_analyzer_p0 import ConstraintIssue, DataTypeIssue, NamingIssue, NormalizationIssue, Table  # noqa: F401,E501


class SchemaAnalyzerMixin0:
    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self.normalization_issues: List[NormalizationIssue] = []
        self.datatype_issues: List[DataTypeIssue] = []
        self.constraint_issues: List[ConstraintIssue] = []
        self.naming_issues: List[NamingIssue] = []
        
        # Data type antipatterns
        self.varchar_255_pattern = re.compile(r'VARCHAR\(255\)', re.IGNORECASE)
        self.bad_datetime_patterns = [
            re.compile(r'VARCHAR\(\d+\)', re.IGNORECASE),
            re.compile(r'CHAR\(\d+\)', re.IGNORECASE)
        ]
        
        # Naming conventions
        self.table_naming_pattern = re.compile(r'^[a-z][a-z0-9_]*[a-z0-9]$')
        self.column_naming_pattern = re.compile(r'^[a-z][a-z0-9_]*[a-z0-9]$')
    def parse_sql_ddl(self, ddl_content: str) -> None:
        """Parse SQL DDL statements and extract schema information."""
        # Remove comments and normalize whitespace
        ddl_content = re.sub(r'--.*$', '', ddl_content, flags=re.MULTILINE)
        ddl_content = re.sub(r'/\*.*?\*/', '', ddl_content, flags=re.DOTALL)
        ddl_content = re.sub(r'\s+', ' ', ddl_content.strip())
        
        # Extract CREATE TABLE statements
        create_table_pattern = re.compile(
            r'CREATE\s+TABLE\s+(\w+)\s*\(\s*(.*?)\s*\)',
            re.IGNORECASE | re.DOTALL
        )
        
        for match in create_table_pattern.finditer(ddl_content):
            table_name = match.group(1).lower()
            table_definition = match.group(2)
            
            table = self._parse_table_definition(table_name, table_definition)
            self.tables[table_name] = table
            
        # Extract CREATE INDEX statements
        self._parse_indexes(ddl_content)
    def _parse_table_definition(self, table_name: str, definition: str) -> Table:
        """Parse individual table definition."""
        columns = []
        primary_key = []
        foreign_keys = []
        unique_constraints = []
        check_constraints = {}
        
        # Split by commas, but handle nested parentheses
        parts = self._split_table_parts(definition)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if part.upper().startswith('PRIMARY KEY'):
                primary_key = self._parse_primary_key(part)
            elif part.upper().startswith('FOREIGN KEY'):
                fk = self._parse_foreign_key(part)
                if fk:
                    foreign_keys.append(fk)
            elif part.upper().startswith('UNIQUE'):
                unique = self._parse_unique_constraint(part)
                if unique:
                    unique_constraints.append(unique)
            elif part.upper().startswith('CHECK'):
                check = self._parse_check_constraint(part)
                if check:
                    check_constraints.update(check)
            else:
                # Column definition
                column = self._parse_column_definition(part)
                if column:
                    columns.append(column)
                    if column.primary_key:
                        primary_key.append(column.name)
        
        return Table(
            name=table_name,
            columns=columns,
            primary_key=primary_key,
            foreign_keys=foreign_keys,
            unique_constraints=unique_constraints,
            check_constraints=check_constraints,
            indexes=[]
        )
    def _split_table_parts(self, definition: str) -> List[str]:
        """Split table definition by commas, respecting nested parentheses."""
        parts = []
        current_part = ""
        paren_count = 0
        
        for char in definition:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                parts.append(current_part.strip())
                current_part = ""
                continue
            
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
            
        return parts
