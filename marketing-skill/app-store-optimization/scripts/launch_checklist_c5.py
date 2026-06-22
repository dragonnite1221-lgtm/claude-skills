# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from launch_checklist_base import *  # noqa: F403,E402


class LaunchChecklistGeneratorMixin5:
    def _validate_google_compliance(
        self,
        app_data: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> None:
        """Validate Google Play Store compliance."""
        # Check for required fields
        if not app_data.get('privacy_policy_url'):
            validation_results['errors'].append("Privacy Policy URL is required")

        if not app_data.get('feature_graphic'):
            validation_results['errors'].append("Feature graphic (1024x500px) is required")

        # Check metadata character limits
        title = app_data.get('title', '')
        if len(title) > 50:
            validation_results['errors'].append(f"Title exceeds 50 characters ({len(title)})")

        short_desc = app_data.get('short_description', '')
        if len(short_desc) > 80:
            validation_results['errors'].append(f"Short description exceeds 80 characters ({len(short_desc)})")

        # Warnings
        if not short_desc:
            validation_results['warnings'].append("Short description is empty")
    def _calculate_next_versions(
        self,
        current_version: str,
        update_frequency: str,
        feature_count: int
    ) -> List[str]:
        """Calculate next version numbers."""
        # Parse current version (assume semantic versioning)
        parts = current_version.split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2] if len(parts) > 2 else 0)

        versions = []
        for i in range(feature_count):
            if update_frequency == 'weekly':
                patch += 1
            elif update_frequency == 'biweekly':
                patch += 1
            elif update_frequency == 'monthly':
                minor += 1
                patch = 0
            else:  # quarterly
                minor += 1
                patch = 0

            versions.append(f"{major}.{minor}.{patch}")

        return versions
    def _distribute_features(
        self,
        features: List[str],
        versions: List[str]
    ) -> List[Dict[str, Any]]:
        """Distribute features across versions."""
        features_per_version = max(1, len(features) // len(versions))

        schedule = []
        for i, version in enumerate(versions):
            start_idx = i * features_per_version
            end_idx = start_idx + features_per_version if i < len(versions) - 1 else len(features)

            schedule.append({
                'version': version,
                'features': features[start_idx:end_idx],
                'release_priority': 'high' if i == 0 else ('medium' if i < len(versions) // 2 else 'low')
            })

        return schedule
    def _generate_whats_new_template(self, version_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate What's New template for version."""
        features_list = '\n'.join([f"• {feature}" for feature in version_data['features']])

        template = f"""Version {version_data['version']}

{features_list}

We're constantly improving your experience. Thanks for using [App Name]!

Have feedback? Contact us at support@[company].com"""

        return {
            'version': version_data['version'],
            'template': template
        }
    def _generate_update_recommendations(self, update_frequency: str) -> List[str]:
        """Generate recommendations for update strategy."""
        recommendations = []

        if update_frequency == 'weekly':
            recommendations.append("Weekly updates show active development but ensure quality doesn't suffer")
        elif update_frequency == 'monthly':
            recommendations.append("Monthly updates are optimal for most apps - balance features and stability")

        recommendations.extend([
            "Include bug fixes in every update",
            "Update 'What's New' section with each release",
            "Respond to reviews mentioning fixed issues"
        ])

        return recommendations
