# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from deployment_manager_base import *  # noqa: F403,E402


class DeploymentManagerMixin0:
    """Generate GCP deployment scripts and IaC configurations."""
    def __init__(self, app_name: str, requirements: Dict[str, Any]):
        """
        Initialize with application requirements.

        Args:
            app_name: Application name (used for resource naming)
            requirements: Dictionary with pattern, region, project requirements
        """
        self.app_name = app_name.lower().replace(' ', '-')
        self.requirements = requirements
        self.region = requirements.get('region', 'us-central1')
        self.project_id = requirements.get('project_id', 'my-project')
        self.pattern = requirements.get('pattern', 'serverless_web')
    def generate_gcloud_script(self) -> str:
        """
        Generate gcloud CLI deployment script.

        Returns:
            Shell script as string
        """
        if self.pattern == 'serverless_web':
            return self._gcloud_serverless_web()
        elif self.pattern == 'gke_microservices':
            return self._gcloud_gke_microservices()
        elif self.pattern == 'data_pipeline':
            return self._gcloud_data_pipeline()
        else:
            return self._gcloud_serverless_web()
