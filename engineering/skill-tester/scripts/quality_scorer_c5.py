# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityScorerMixin5:
    def _score_completeness(self, weight: float = 0.25):
        """Score completeness"""
        self.log_verbose("Scoring completeness...")
        
        dimension = QualityDimension("Completeness", weight, "Completeness of required components and assets")
        
        # Score directory structure
        self._score_directory_structure(dimension)
        
        # Score asset availability
        self._score_assets(dimension)
        
        # Score expected outputs
        self._score_expected_outputs(dimension)
        
        # Score test coverage
        self._score_test_coverage(dimension)
        
        dimension.calculate_final_score()
        self.report.add_dimension(dimension)
    def _score_directory_structure(self, dimension: QualityDimension):
        """Score directory structure completeness"""
        required_dirs = ["scripts"]
        recommended_dirs = ["assets", "references", "expected_outputs"]
        
        score = 0
        
        # Required directories (15 points)
        for dir_name in required_dirs:
            if (self.skill_path / dir_name).exists():
                score += 15 / len(required_dirs)
                
        # Recommended directories (10 points)
        present_recommended = 0
        for dir_name in recommended_dirs:
            if (self.skill_path / dir_name).exists():
                present_recommended += 1
                
        score += (present_recommended / len(recommended_dirs)) * 10
        
        dimension.add_score("directory_structure", score, 25,
                           f"Directory structure completeness")
                           
        missing_recommended = [d for d in recommended_dirs if not (self.skill_path / d).exists()]
        if missing_recommended:
            dimension.add_suggestion(f"Add recommended directories: {', '.join(missing_recommended)}")
    def _score_assets(self, dimension: QualityDimension):
        """Score asset availability and quality"""
        assets_dir = self.skill_path / "assets"
        
        if not assets_dir.exists():
            dimension.add_score("assets_existence", 5, 25, "Assets directory missing")
            dimension.add_suggestion("Create assets directory with sample data")
            return
            
        asset_files = [f for f in assets_dir.rglob("*") if f.is_file()]
        
        if not asset_files:
            dimension.add_score("assets_content", 10, 25, "Assets directory empty")
            dimension.add_suggestion("Add sample data files to assets directory")
            return
            
        # Score based on number and diversity of assets
        score = min(len(asset_files) * 3, 20)  # Up to 20 points for multiple assets
        
        # Bonus for diverse file types
        extensions = set(f.suffix.lower() for f in asset_files if f.suffix)
        if len(extensions) >= 3:
            score += 5  # Bonus for file type diversity
            
        dimension.add_score("assets_quality", score, 25,
                           f"Assets: {len(asset_files)} files, {len(extensions)} types")
    def _score_expected_outputs(self, dimension: QualityDimension):
        """Score expected outputs availability"""
        expected_dir = self.skill_path / "expected_outputs"
        
        if not expected_dir.exists():
            dimension.add_score("expected_outputs", 10, 25, "Expected outputs directory missing")
            dimension.add_suggestion("Add expected_outputs directory with sample results")
            return
            
        output_files = [f for f in expected_dir.rglob("*") if f.is_file()]
        
        if len(output_files) >= 3:
            score = 25
        elif len(output_files) >= 2:
            score = 20
        elif len(output_files) >= 1:
            score = 15
        else:
            score = 10
            dimension.add_suggestion("Add expected output files for testing")
            
        dimension.add_score("expected_outputs", score, 25,
                           f"Expected outputs: {len(output_files)} files")
