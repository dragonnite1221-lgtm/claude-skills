# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import ValidationResult  # noqa: F401,E501
from data_quality_validator_p1 import TypeDetector  # noqa: F401,E501


class DataContractValidator:
    """Validate data against a data contract"""

    def load_contract(self, contract_path: str) -> Dict:
        """Load a data contract from file"""
        with open(contract_path, 'r') as f:
            content = f.read()

        # Support both YAML and JSON
        if contract_path.endswith('.yaml') or contract_path.endswith('.yml'):
            # Simple YAML parsing (for basic contracts)
            contract = self._parse_simple_yaml(content)
        else:
            contract = json.loads(content)

        return contract

    def _parse_simple_yaml(self, content: str) -> Dict:
        """Parse simple YAML-like format"""
        result = {}
        current_section = result
        section_stack = [(result, -1)]

        for line in content.split('\n'):
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            line = line.strip()

            # Pop sections with greater or equal indentation
            while section_stack and section_stack[-1][1] >= indent:
                section_stack.pop()

            current_section = section_stack[-1][0]

            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                if value:
                    # Handle lists
                    if value.startswith('[') and value.endswith(']'):
                        current_section[key] = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                    elif value.lower() in ('true', 'false'):
                        current_section[key] = value.lower() == 'true'
                    elif value.isdigit():
                        current_section[key] = int(value)
                    else:
                        current_section[key] = value.strip('"\'')
                else:
                    current_section[key] = {}
                    section_stack.append((current_section[key], indent))
            elif line.startswith('- '):
                # List item
                if not isinstance(current_section, list):
                    # Convert to list
                    parent = section_stack[-2][0] if len(section_stack) > 1 else result
                    for k, v in parent.items():
                        if v is current_section:
                            parent[k] = [current_section] if current_section else []
                            current_section = parent[k]
                            section_stack[-1] = (current_section, section_stack[-1][1])
                            break
                current_section.append(line[2:].strip())

        return result

    def validate_contract(self, data: List[Dict], contract: Dict) -> List[ValidationResult]:
        """Validate data against contract"""
        results = []

        # Validate schema section
        if 'schema' in contract:
            schema_def = contract['schema']
            columns = schema_def.get('columns', schema_def.get('fields', []))

            for col_def in columns:
                col_name = col_def.get('name', col_def.get('column', ''))
                if not col_name:
                    continue

                # Check column exists
                if data and col_name not in data[0]:
                    results.append(ValidationResult(
                        check_name="contract_column_exists",
                        column=col_name,
                        passed=False,
                        expected="column present",
                        actual="column missing",
                        severity="error",
                        message=f"Contract requires column '{col_name}' but it's missing"
                    ))
                    continue

                # Check data type
                expected_type = col_def.get('type', col_def.get('data_type', 'string'))
                values = [row.get(col_name) for row in data]
                non_null = [str(v) for v in values if v is not None and v != '']

                if non_null:
                    detected_type = TypeDetector.detect_type(non_null[:1000])
                    type_compatible = self._types_compatible(detected_type, expected_type)

                    if not type_compatible:
                        results.append(ValidationResult(
                            check_name="contract_data_type",
                            column=col_name,
                            passed=False,
                            expected=expected_type,
                            actual=detected_type,
                            severity="error",
                            message=f"Contract expects type '{expected_type}' but detected '{detected_type}'"
                        ))

                # Check nullable
                if not col_def.get('nullable', True):
                    null_count = sum(1 for v in values if v is None or v == '')
                    if null_count > 0:
                        results.append(ValidationResult(
                            check_name="contract_not_null",
                            column=col_name,
                            passed=False,
                            expected="no nulls",
                            actual=f"{null_count} nulls",
                            severity="error",
                            message=f"Contract requires non-null but found {null_count} nulls"
                        ))

        # Validate SLA section
        if 'sla' in contract:
            sla = contract['sla']

            # Row count bounds
            min_rows = sla.get('min_rows', sla.get('minimum_records'))
            max_rows = sla.get('max_rows', sla.get('maximum_records'))

            row_count = len(data)
            if min_rows and row_count < min_rows:
                results.append(ValidationResult(
                    check_name="contract_min_rows",
                    column=None,
                    passed=False,
                    expected=f">= {min_rows} rows",
                    actual=f"{row_count} rows",
                    severity="error",
                    message=f"Contract requires at least {min_rows} rows"
                ))

            if max_rows and row_count > max_rows:
                results.append(ValidationResult(
                    check_name="contract_max_rows",
                    column=None,
                    passed=False,
                    expected=f"<= {max_rows} rows",
                    actual=f"{row_count} rows",
                    severity="warning",
                    message=f"Contract allows at most {max_rows} rows"
                ))

        return results

    def _types_compatible(self, detected: str, expected: str) -> bool:
        """Check if detected type is compatible with expected type"""
        expected = expected.lower()
        detected = detected.lower()

        type_groups = {
            'numeric': ['integer', 'int', 'float', 'double', 'decimal', 'number'],
            'string': ['string', 'varchar', 'char', 'text'],
            'boolean': ['boolean', 'bool'],
            'date': ['date', 'date_iso'],
            'datetime': ['datetime', 'datetime_iso', 'timestamp'],
        }

        for group, types in type_groups.items():
            if expected in types and detected in types:
                return True

        return detected == expected
