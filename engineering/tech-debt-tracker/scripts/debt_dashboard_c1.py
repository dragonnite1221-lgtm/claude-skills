# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from debt_dashboard_base import *  # noqa: F403,E402


class DebtDashboardMixin1:
    def _extract_date_from_filename(self, file_path: str) -> str:
        """Extract date from filename if possible, otherwise use current date."""
        filename = Path(file_path).name
        
        # Try to find date patterns in filename
        date_patterns = [
            r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
            r"(\d{4}\d{2}\d{2})",    # YYYYMMDD
            r"(\d{2}-\d{2}-\d{4})",  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                try:
                    if len(date_str) == 8:  # YYYYMMDD
                        date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                    datetime.strptime(date_str, "%Y-%m-%d")
                    return date_str + "T12:00:00"
                except ValueError:
                    continue
        
        # Fallback to file modification time
        try:
            mtime = os.path.getmtime(file_path)
            return datetime.fromtimestamp(mtime).isoformat()
        except:
            return datetime.now().isoformat()
    def generate_dashboard(self, period: str = "monthly") -> Dict[str, Any]:
        """
        Generate comprehensive debt dashboard.
        
        Args:
            period: Analysis period ("weekly", "monthly", "quarterly")
            
        Returns:
            Dictionary containing dashboard data and analysis
        """
        print(f"Generating debt dashboard for {len(self.historical_data)} snapshots...")
        print(f"Analysis period: {period}")
        print("=" * 50)
        
        # Step 1: Process historical snapshots
        self._process_snapshots()
        
        # Step 2: Calculate health metrics for each snapshot
        self._calculate_health_metrics()
        
        # Step 3: Analyze trends
        self._analyze_trends(period)
        
        # Step 4: Calculate debt velocity
        self._calculate_debt_velocity(period)
        
        # Step 5: Generate forecasts
        forecasts = self._generate_forecasts()
        
        # Step 6: Create executive summary
        executive_summary = self._generate_executive_summary()
        
        # Step 7: Generate recommendations
        recommendations = self._generate_strategic_recommendations()
        
        # Step 8: Create visualizations data
        visualizations = self._generate_visualization_data()
        
        dashboard_data = {
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "analysis_period": period,
                "snapshots_analyzed": len(self.historical_data),
                "date_range": {
                    "start": self.historical_data[0]["scan_date"] if self.historical_data else None,
                    "end": self.historical_data[-1]["scan_date"] if self.historical_data else None
                },
                "team_size": self.team_size
            },
            "executive_summary": executive_summary,
            "current_health": self.health_history[-1] if self.health_history else None,
            "trend_analysis": {name: asdict(trend) for name, trend in self.trend_analyses.items()},
            "debt_velocity": [asdict(v) for v in self.velocity_history],
            "forecasts": forecasts,
            "recommendations": recommendations,
            "visualizations": visualizations,
            "detailed_metrics": self._get_detailed_metrics()
        }
        
        return dashboard_data
    def _process_snapshots(self):
        """Process raw snapshots into standardized format."""
        self.processed_snapshots = []
        
        for snapshot in self.historical_data:
            processed = {
                "date": snapshot["scan_date"],
                "total_debt_items": len(snapshot["debt_items"]),
                "debt_by_type": Counter(item.get("type", "unknown") for item in snapshot["debt_items"]),
                "debt_by_severity": Counter(item.get("severity", "medium") for item in snapshot["debt_items"]),
                "debt_by_category": Counter(self._categorize_debt_item(item) for item in snapshot["debt_items"]),
                "total_files": snapshot["summary"].get("total_files_scanned", 
                                                     len(snapshot["file_statistics"])),
                "total_effort_estimate": self._calculate_total_effort(snapshot["debt_items"]),
                "high_priority_count": len([item for item in snapshot["debt_items"] 
                                          if self._is_high_priority(item)]),
                "security_debt_count": len([item for item in snapshot["debt_items"]
                                          if self._is_security_related(item)]),
                "raw_data": snapshot
            }
            self.processed_snapshots.append(processed)
