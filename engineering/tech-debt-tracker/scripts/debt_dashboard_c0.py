# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402


class DebtDashboardMixin0:
    """Main dashboard class for debt trend analysis and reporting."""
    def __init__(self, team_size: int = 5):
        self.team_size = team_size
        self.historical_data = []
        self.processed_snapshots = []
        self.trend_analyses = {}
        self.health_history = []
        self.velocity_history = []
        
        # Configuration for health scoring
        self.health_weights = {
            "debt_density": 0.25,
            "complexity_score": 0.20,
            "test_coverage_proxy": 0.15,
            "documentation_proxy": 0.10,
            "security_score": 0.15,
            "maintainability": 0.15
        }
        
        # Thresholds for categorization
        self.thresholds = {
            "excellent": 85,
            "good": 70,
            "fair": 55,
            "poor": 40
        }
    def load_historical_data(self, file_paths: List[str]) -> bool:
        """Load multiple debt inventory files for historical analysis."""
        self.historical_data = []
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Normalize data format
                if isinstance(data, dict) and 'debt_items' in data:
                    # Scanner output format
                    snapshot = {
                        "file_path": file_path,
                        "scan_date": data.get("scan_metadata", {}).get("scan_date", 
                                               self._extract_date_from_filename(file_path)),
                        "debt_items": data["debt_items"],
                        "summary": data.get("summary", {}),
                        "file_statistics": data.get("file_statistics", {})
                    }
                elif isinstance(data, dict) and 'prioritized_backlog' in data:
                    # Prioritizer output format
                    snapshot = {
                        "file_path": file_path,
                        "scan_date": data.get("metadata", {}).get("analysis_date",
                                               self._extract_date_from_filename(file_path)),
                        "debt_items": data["prioritized_backlog"],
                        "summary": data.get("insights", {}),
                        "file_statistics": {}
                    }
                elif isinstance(data, list):
                    # Raw debt items array
                    snapshot = {
                        "file_path": file_path,
                        "scan_date": self._extract_date_from_filename(file_path),
                        "debt_items": data,
                        "summary": {},
                        "file_statistics": {}
                    }
                else:
                    raise ValueError(f"Unrecognized data format in {file_path}")
                
                self.historical_data.append(snapshot)
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        if not self.historical_data:
            print("No valid data files loaded.")
            return False
        
        # Sort by date
        self.historical_data.sort(key=lambda x: x["scan_date"])
        print(f"Loaded {len(self.historical_data)} historical snapshots")
        return True
    def load_from_directory(self, directory_path: str, pattern: str = "*.json") -> bool:
        """Load all JSON files from a directory."""
        directory = Path(directory_path)
        if not directory.exists():
            print(f"Directory does not exist: {directory_path}")
            return False
        
        file_paths = []
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                file_paths.append(str(file_path))
        
        if not file_paths:
            print(f"No matching files found in {directory_path}")
            return False
        
        return self.load_historical_data(file_paths)
