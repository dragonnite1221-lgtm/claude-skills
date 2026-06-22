# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from cost_optimizer_base import *  # noqa: F403,E402


class CostOptimizerMixin0:
    """Analyze GCP costs and provide optimization recommendations."""
    def __init__(self, current_resources: Dict[str, Any], monthly_spend: float):
        """
        Initialize with current GCP resources and spending.

        Args:
            current_resources: Dictionary of current GCP resources
            monthly_spend: Current monthly GCP spend in USD
        """
        self.resources = current_resources
        self.monthly_spend = monthly_spend
        self.recommendations = []
    def analyze_and_optimize(self) -> Dict[str, Any]:
        """
        Analyze current setup and generate cost optimization recommendations.

        Returns:
            Dictionary with recommendations and potential savings
        """
        self.recommendations = []
        potential_savings = 0.0

        compute_savings = self._analyze_compute()
        potential_savings += compute_savings

        storage_savings = self._analyze_storage()
        potential_savings += storage_savings

        database_savings = self._analyze_database()
        potential_savings += database_savings

        network_savings = self._analyze_networking()
        potential_savings += network_savings

        general_savings = self._analyze_general_optimizations()
        potential_savings += general_savings

        return {
            'current_monthly_spend': self.monthly_spend,
            'potential_monthly_savings': round(potential_savings, 2),
            'optimized_monthly_spend': round(self.monthly_spend - potential_savings, 2),
            'savings_percentage': round((potential_savings / self.monthly_spend) * 100, 2) if self.monthly_spend > 0 else 0,
            'recommendations': self.recommendations,
            'priority_actions': self._prioritize_recommendations()
        }
