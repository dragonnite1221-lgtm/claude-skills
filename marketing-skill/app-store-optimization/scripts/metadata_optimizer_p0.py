# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from metadata_optimizer_base import *  # noqa: F403,E402


def optimize_app_metadata(
    platform: str,
    app_info: Dict[str, Any],
    target_keywords: List[str]
) -> Dict[str, Any]:
    """
    Convenience function to optimize all metadata fields.

    Args:
        platform: 'apple' or 'google'
        app_info: App information dictionary
        target_keywords: Target keywords list

    Returns:
        Complete metadata optimization package
    """
    optimizer = MetadataOptimizer(platform)

    return {
        'platform': platform,
        'title': optimizer.optimize_title(
            app_info['name'],
            target_keywords
        ),
        'description': optimizer.optimize_description(
            app_info,
            target_keywords,
            'full'
        ),
        'keyword_field': optimizer.optimize_keyword_field(
            target_keywords
        ) if platform == 'apple' else None
    }
