# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from launch_checklist_base import *  # noqa: F403,E402


def generate_launch_checklist(
    platform: str,
    app_info: Dict[str, Any],
    launch_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to generate launch checklist.

    Args:
        platform: Platform ('apple', 'google', or 'both')
        app_info: App information
        launch_date: Target launch date

    Returns:
        Complete launch checklist
    """
    generator = LaunchChecklistGenerator(platform)
    return generator.generate_prelaunch_checklist(app_info, launch_date)
