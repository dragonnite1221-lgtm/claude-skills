# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from index_optimizer_base import *  # noqa: F403,E402
from index_optimizer_p0 import Column  # noqa: F401,E501


class SelectivityEstimator:
    """Estimates column selectivity based on naming patterns and data types."""
    
    def __init__(self):
        # Selectivity patterns based on common column names and types
        self.high_selectivity_patterns = [
            r'.*_id$', r'^id$', r'uuid', r'guid', r'email', r'username', r'ssn',
            r'account.*number', r'transaction.*id', r'reference.*number'
        ]
        
        self.medium_selectivity_patterns = [
            r'name$', r'title$', r'description$', r'address', r'phone', r'zip',
            r'postal.*code', r'serial.*number', r'sku', r'product.*code'
        ]
        
        self.low_selectivity_patterns = [
            r'status$', r'type$', r'category', r'state$', r'flag$', r'active$',
            r'enabled$', r'deleted$', r'visible$', r'gender$', r'priority$'
        ]
        
        self.very_low_selectivity_patterns = [
            r'is_.*', r'has_.*', r'can_.*', r'boolean', r'bool'
        ]
    
    def estimate_selectivity(self, column: Column, table_size_estimate: int = 10000) -> float:
        """Estimate column selectivity (0.0 = all same values, 1.0 = all unique values)."""
        column_name_lower = column.name.lower()
        
        # Primary key or unique columns
        if column.unique or column.name.lower() in ['id', 'uuid', 'guid']:
            return 1.0
        
        # Check cardinality estimate if available
        if column.cardinality_estimate:
            return min(column.cardinality_estimate / table_size_estimate, 1.0)
        
        # Pattern-based estimation
        for pattern in self.high_selectivity_patterns:
            if re.search(pattern, column_name_lower):
                return 0.9  # Very high selectivity
        
        for pattern in self.medium_selectivity_patterns:
            if re.search(pattern, column_name_lower):
                return 0.7  # Good selectivity
        
        for pattern in self.low_selectivity_patterns:
            if re.search(pattern, column_name_lower):
                return 0.2  # Poor selectivity
        
        for pattern in self.very_low_selectivity_patterns:
            if re.search(pattern, column_name_lower):
                return 0.1  # Very poor selectivity
        
        # Data type based estimation
        data_type_upper = column.data_type.upper()
        if data_type_upper.startswith('BOOL'):
            return 0.1
        elif data_type_upper.startswith(('TINYINT', 'SMALLINT')):
            return 0.3
        elif data_type_upper.startswith('INT'):
            return 0.8
        elif data_type_upper.startswith(('VARCHAR', 'TEXT')):
            # Estimate based on column name
            if 'name' in column_name_lower:
                return 0.7
            elif 'description' in column_name_lower or 'comment' in column_name_lower:
                return 0.9
            else:
                return 0.6
        
        # Default moderate selectivity
        return 0.5
