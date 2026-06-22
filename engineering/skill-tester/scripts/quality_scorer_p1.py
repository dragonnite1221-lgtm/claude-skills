# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_scorer_base import *  # noqa: F403,E402
from quality_scorer_p0 import QualityDimension  # noqa: F401,E501


class QualityReport:
    """Container for quality assessment results"""
    
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.dimensions = {}
        self.overall_score = 0.0
        self.letter_grade = "F"
        self.tier_recommendation = "BASIC"
        self.improvement_roadmap = []
        self.summary_stats = {}
        
    def add_dimension(self, dimension: QualityDimension):
        """Add a quality dimension"""
        self.dimensions[dimension.name] = dimension
        
    def calculate_overall_score(self):
        """Calculate overall weighted score"""
        if not self.dimensions:
            return
            
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for dimension in self.dimensions.values():
            total_weighted_score += dimension.score * dimension.weight
            total_weight += dimension.weight
            
        self.overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Calculate letter grade
        if self.overall_score >= 95:
            self.letter_grade = "A+"
        elif self.overall_score >= 90:
            self.letter_grade = "A"
        elif self.overall_score >= 85:
            self.letter_grade = "A-"
        elif self.overall_score >= 80:
            self.letter_grade = "B+"
        elif self.overall_score >= 75:
            self.letter_grade = "B"
        elif self.overall_score >= 70:
            self.letter_grade = "B-"
        elif self.overall_score >= 65:
            self.letter_grade = "C+"
        elif self.overall_score >= 60:
            self.letter_grade = "C"
        elif self.overall_score >= 55:
            self.letter_grade = "C-"
        elif self.overall_score >= 50:
            self.letter_grade = "D"
        else:
            self.letter_grade = "F"
            
        # Recommend tier based on overall score and specific criteria
        self._calculate_tier_recommendation()
        
        # Generate improvement roadmap
        self._generate_improvement_roadmap()
        
        # Calculate summary statistics
        self._calculate_summary_stats()
        
    def _calculate_tier_recommendation(self):
        """Calculate recommended tier based on quality scores"""
        doc_score = self.dimensions.get("Documentation", QualityDimension("", 0, "")).score
        code_score = self.dimensions.get("Code Quality", QualityDimension("", 0, "")).score
        completeness_score = self.dimensions.get("Completeness", QualityDimension("", 0, "")).score
        usability_score = self.dimensions.get("Usability", QualityDimension("", 0, "")).score
        security_score = self.dimensions.get("Security", QualityDimension("", 0, "")).score
        
        # Check if Security dimension is included
        has_security = "Security" in self.dimensions
        
        # POWERFUL tier requirements
        if has_security:
            # With Security: all 5 dimensions must be strong
            if (self.overall_score >= 80 and 
                all(score >= 75 for score in [doc_score, code_score, completeness_score, usability_score]) and
                security_score >= 70):
                self.tier_recommendation = "POWERFUL"
                
            # STANDARD tier requirements (with Security)
            elif (self.overall_score >= 70 and 
                  sum(1 for score in [doc_score, code_score, completeness_score, usability_score, security_score] if score >= 65) >= 4 and
                  security_score >= 50):
                self.tier_recommendation = "STANDARD"
        else:
            # Without Security: 4 dimensions must be strong
            if (self.overall_score >= 80 and 
                all(score >= 75 for score in [doc_score, code_score, completeness_score, usability_score])):
                self.tier_recommendation = "POWERFUL"
                
            # STANDARD tier requirements (without Security)
            elif (self.overall_score >= 70 and 
                  sum(1 for score in [doc_score, code_score, completeness_score, usability_score] if score >= 65) >= 3):
                self.tier_recommendation = "STANDARD"
                
        # BASIC tier (minimum viable quality)
        # Falls through to BASIC if no other tier matched
            
    def _generate_improvement_roadmap(self):
        """Generate prioritized improvement suggestions"""
        all_suggestions = []
        
        # Collect suggestions from all dimensions with scores
        for dim_name, dimension in self.dimensions.items():
            for suggestion in dimension.suggestions:
                priority = "HIGH" if dimension.score < 60 else "MEDIUM" if dimension.score < 75 else "LOW"
                all_suggestions.append({
                    "priority": priority,
                    "dimension": dim_name,
                    "suggestion": suggestion,
                    "current_score": dimension.score
                })
                
        # Sort by priority and score
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        all_suggestions.sort(key=lambda x: (priority_order[x["priority"]], x["current_score"]))
        
        self.improvement_roadmap = all_suggestions[:10]  # Top 10 suggestions
        
    def _calculate_summary_stats(self):
        """Calculate summary statistics"""
        scores = [dim.score for dim in self.dimensions.values()]
        
        self.summary_stats = {
            "highest_dimension": max(self.dimensions.items(), key=lambda x: x[1].score)[0] if scores else "None",
            "lowest_dimension": min(self.dimensions.items(), key=lambda x: x[1].score)[0] if scores else "None",
            "score_variance": sum((score - self.overall_score) ** 2 for score in scores) / len(scores) if scores else 0,
            "dimensions_above_70": sum(1 for score in scores if score >= 70),
            "dimensions_below_50": sum(1 for score in scores if score < 50)
        }
