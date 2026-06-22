# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402
from schema_analyzer_p0 import Column, Index  # noqa: F401,E501


class SchemaAnalyzerMixin1:
    def _parse_column_definition(self, definition: str) -> Optional[Column]:
        """Parse individual column definition."""
        # Pattern for column definition
        pattern = re.compile(
            r'(\w+)\s+([A-Z]+(?:\(\d+(?:,\d+)?\))?)\s*(.*)',
            re.IGNORECASE
        )
        
        match = pattern.match(definition.strip())
        if not match:
            return None
            
        column_name = match.group(1).lower()
        data_type = match.group(2).upper()
        constraints = match.group(3).upper() if match.group(3) else ""
        
        column = Column(
            name=column_name,
            data_type=data_type,
            nullable='NOT NULL' not in constraints,
            primary_key='PRIMARY KEY' in constraints,
            unique='UNIQUE' in constraints
        )
        
        # Parse foreign key reference
        fk_pattern = re.compile(r'REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', re.IGNORECASE)
        fk_match = fk_pattern.search(constraints)
        if fk_match:
            column.foreign_key = f"{fk_match.group(1).lower()}.{fk_match.group(2).lower()}"
        
        # Parse default value
        default_pattern = re.compile(r'DEFAULT\s+([^,\s]+)', re.IGNORECASE)
        default_match = default_pattern.search(constraints)
        if default_match:
            column.default_value = default_match.group(1)
        
        return column
    def _parse_primary_key(self, definition: str) -> List[str]:
        """Parse PRIMARY KEY constraint."""
        pattern = re.compile(r'PRIMARY\s+KEY\s*\(\s*(.*?)\s*\)', re.IGNORECASE)
        match = pattern.search(definition)
        if match:
            columns = [col.strip().lower() for col in match.group(1).split(',')]
            return columns
        return []
    def _parse_foreign_key(self, definition: str) -> Optional[Tuple[str, str]]:
        """Parse FOREIGN KEY constraint."""
        pattern = re.compile(
            r'FOREIGN\s+KEY\s*\(\s*(\w+)\s*\)\s+REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)',
            re.IGNORECASE
        )
        match = pattern.search(definition)
        if match:
            column = match.group(1).lower()
            ref_table = match.group(2).lower()
            ref_column = match.group(3).lower()
            return (column, f"{ref_table}.{ref_column}")
        return None
    def _parse_unique_constraint(self, definition: str) -> Optional[List[str]]:
        """Parse UNIQUE constraint."""
        pattern = re.compile(r'UNIQUE\s*\(\s*(.*?)\s*\)', re.IGNORECASE)
        match = pattern.search(definition)
        if match:
            columns = [col.strip().lower() for col in match.group(1).split(',')]
            return columns
        return None
    def _parse_check_constraint(self, definition: str) -> Optional[Dict[str, str]]:
        """Parse CHECK constraint."""
        pattern = re.compile(r'CHECK\s*\(\s*(.*?)\s*\)', re.IGNORECASE)
        match = pattern.search(definition)
        if match:
            constraint_name = f"check_constraint_{len(self.tables)}"
            return {constraint_name: match.group(1)}
        return None
    def _parse_indexes(self, ddl_content: str) -> None:
        """Parse CREATE INDEX statements."""
        index_pattern = re.compile(
            r'CREATE\s+(?:(UNIQUE)\s+)?INDEX\s+(\w+)\s+ON\s+(\w+)\s*\(\s*(.*?)\s*\)',
            re.IGNORECASE
        )
        
        for match in index_pattern.finditer(ddl_content):
            unique = match.group(1) is not None
            index_name = match.group(2).lower()
            table_name = match.group(3).lower()
            columns_str = match.group(4)
            
            columns = [col.strip().lower() for col in columns_str.split(',')]
            
            index = Index(
                name=index_name,
                table=table_name,
                columns=columns,
                unique=unique
            )
            
            if table_name in self.tables:
                self.tables[table_name].indexes.append(index)
