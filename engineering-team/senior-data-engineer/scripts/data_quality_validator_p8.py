# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import ColumnSchema, DataSchema  # noqa: F401,E501


class DataLoader:
    """Load data from various formats"""

    @staticmethod
    def load(file_path: str) -> List[Dict]:
        """Load data from file"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()

        if suffix == '.csv':
            return DataLoader._load_csv(file_path)
        elif suffix == '.json':
            return DataLoader._load_json(file_path)
        elif suffix == '.jsonl':
            return DataLoader._load_jsonl(file_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    @staticmethod
    def _load_csv(file_path: str) -> List[Dict]:
        """Load CSV file"""
        data = []
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data

    @staticmethod
    def _load_json(file_path: str) -> List[Dict]:
        """Load JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        if isinstance(content, list):
            return content
        elif isinstance(content, dict):
            # Check for common data keys
            for key in ['data', 'records', 'rows', 'items']:
                if key in content and isinstance(content[key], list):
                    return content[key]
            return [content]
        else:
            raise ValueError("JSON must contain array or object with data key")

    @staticmethod
    def _load_jsonl(file_path: str) -> List[Dict]:
        """Load JSON Lines file"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
        return data


class SchemaLoader:
    """Load schema definitions"""

    @staticmethod
    def load(file_path: str) -> DataSchema:
        """Load schema from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            schema_dict = json.load(f)

        columns = []
        for col_def in schema_dict.get('columns', []):
            columns.append(ColumnSchema(
                name=col_def['name'],
                data_type=col_def.get('type', col_def.get('data_type', 'string')),
                nullable=col_def.get('nullable', True),
                unique=col_def.get('unique', False),
                min_value=col_def.get('min_value'),
                max_value=col_def.get('max_value'),
                min_length=col_def.get('min_length'),
                max_length=col_def.get('max_length'),
                pattern=col_def.get('pattern'),
                allowed_values=col_def.get('allowed_values'),
                description=col_def.get('description', '')
            ))

        return DataSchema(
            name=schema_dict.get('name', 'unknown'),
            version=schema_dict.get('version', '1.0'),
            columns=columns,
            primary_key=schema_dict.get('primary_key'),
            row_count_min=schema_dict.get('row_count_min'),
            row_count_max=schema_dict.get('row_count_max')
        )
