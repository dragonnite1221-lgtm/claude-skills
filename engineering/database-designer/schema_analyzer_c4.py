# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from schema_analyzer_base import *  # noqa: F403,E402
from schema_analyzer_p0 import ConstraintIssue, Table  # noqa: F401,E501


class SchemaAnalyzerMixin4:
    def analyze_constraints(self) -> None:
        """Analyze missing constraints."""
        for table_name, table in self.tables.items():
            self._check_missing_primary_key(table)
            self._check_missing_foreign_key_constraints(table)
            self._check_missing_not_null_constraints(table)
            self._check_missing_unique_constraints(table)
            self._check_missing_check_constraints(table)
    def _check_missing_primary_key(self, table: Table) -> None:
        """Check for missing primary key."""
        if not table.primary_key:
            self.constraint_issues.append(ConstraintIssue(
                table=table.name,
                issue_type="MISSING_PRIMARY_KEY",
                severity="HIGH",
                description="Table has no primary key defined",
                suggestion="Add a primary key column (e.g., 'id' with auto-increment)",
                columns_affected=[]
            ))
    def _check_missing_foreign_key_constraints(self, table: Table) -> None:
        """Check for missing foreign key constraints."""
        for column in table.columns:
            if column.name.endswith('_id') and column.name != 'id':
                # Potential foreign key column
                if not column.foreign_key:
                    referenced_table = column.name[:-3]  # Remove '_id' suffix
                    if referenced_table in self.tables or referenced_table + 's' in self.tables:
                        self.constraint_issues.append(ConstraintIssue(
                            table=table.name,
                            issue_type="MISSING_FOREIGN_KEY",
                            severity="MEDIUM",
                            description=f"Column '{column.name}' appears to be a foreign key but has no constraint",
                            suggestion=f"Add foreign key constraint referencing {referenced_table} table",
                            columns_affected=[column.name]
                        ))
    def _check_missing_not_null_constraints(self, table: Table) -> None:
        """Check for missing NOT NULL constraints."""
        for column in table.columns:
            if column.nullable and column.name in ['email', 'name', 'title', 'status']:
                self.constraint_issues.append(ConstraintIssue(
                    table=table.name,
                    issue_type="MISSING_NOT_NULL",
                    severity="LOW",
                    description=f"Column '{column.name}' allows NULL but typically should not",
                    suggestion=f"Consider adding NOT NULL constraint to '{column.name}'",
                    columns_affected=[column.name]
                ))
    def _check_missing_unique_constraints(self, table: Table) -> None:
        """Check for missing unique constraints."""
        for column in table.columns:
            if column.name in ['email', 'username', 'slug', 'code'] and not column.unique:
                if column.name not in table.primary_key:
                    self.constraint_issues.append(ConstraintIssue(
                        table=table.name,
                        issue_type="MISSING_UNIQUE",
                        severity="MEDIUM",
                        description=f"Column '{column.name}' should likely have UNIQUE constraint",
                        suggestion=f"Add UNIQUE constraint to '{column.name}'",
                        columns_affected=[column.name]
                    ))
    def _check_missing_check_constraints(self, table: Table) -> None:
        """Check for missing check constraints."""
        for column in table.columns:
            # Email format validation
            if column.name == 'email' and 'email' not in str(table.check_constraints):
                self.constraint_issues.append(ConstraintIssue(
                    table=table.name,
                    issue_type="MISSING_CHECK_CONSTRAINT",
                    severity="LOW",
                    description=f"Email column lacks format validation",
                    suggestion="Add CHECK constraint for email format validation",
                    columns_affected=[column.name]
                ))
            
            # Positive values for counts, prices, etc.
            if column.name.lower() in ['price', 'amount', 'count', 'quantity', 'age']:
                if column.name not in str(table.check_constraints):
                    self.constraint_issues.append(ConstraintIssue(
                        table=table.name,
                        issue_type="MISSING_CHECK_CONSTRAINT",
                        severity="LOW",
                        description=f"Column '{column.name}' should validate positive values",
                        suggestion=f"Add CHECK constraint: {column.name} > 0",
                        columns_affected=[column.name]
                    ))
    def analyze_naming_conventions(self) -> None:
        """Analyze naming convention compliance."""
        for table_name, table in self.tables.items():
            self._check_table_naming(table_name)
            for column in table.columns:
                self._check_column_naming(table_name, column.name)
