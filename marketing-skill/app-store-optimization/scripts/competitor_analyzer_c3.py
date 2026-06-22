# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from competitor_analyzer_base import *  # noqa: F403,E402


class CompetitorAnalyzerMixin3:
    def _identify_keyword_gaps(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify keywords used by some competitors but not others."""
        all_keywords_by_app = {}

        for analysis in analyses:
            app_name = analysis['app_name']
            keywords = analysis['keyword_strategy']['primary_keywords']
            all_keywords_by_app[app_name] = set(keywords)

        # Find keywords used by some but not all
        all_keywords_set = set()
        for keywords in all_keywords_by_app.values():
            all_keywords_set.update(keywords)

        gaps = []
        for keyword in all_keywords_set:
            using_apps = [
                app for app, keywords in all_keywords_by_app.items()
                if keyword in keywords
            ]
            if 1 < len(using_apps) < len(analyses):
                gaps.append({
                    'keyword': keyword,
                    'used_by': using_apps,
                    'usage_percentage': round(len(using_apps) / len(analyses) * 100, 1)
                })

        return sorted(gaps, key=lambda x: x['usage_percentage'], reverse=True)[:15]
    def _analyze_rating_distribution(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze rating distribution across competitors."""
        ratings = [a['rating_metrics']['rating'] for a in analyses]
        ratings_counts = [a['rating_metrics']['ratings_count'] for a in analyses]

        return {
            'average_rating': round(sum(ratings) / len(ratings), 2),
            'highest_rating': max(ratings),
            'lowest_rating': min(ratings),
            'average_ratings_count': int(sum(ratings_counts) / len(ratings_counts)),
            'total_ratings_in_category': sum(ratings_counts)
        }
    def _identify_best_practices(self, ranked_competitors: List[Dict[str, Any]]) -> List[str]:
        """Identify best practices from top competitors."""
        if not ranked_competitors:
            return []

        top_competitor = ranked_competitors[0]
        practices = []

        # Title strategy
        title_analysis = top_competitor['title_analysis']
        if title_analysis['has_keywords']:
            practices.append(
                f"Title Strategy: Include primary keyword in title (e.g., '{title_analysis['title']}')"
            )

        # Description structure
        desc_analysis = top_competitor['description_analysis']
        if desc_analysis['structure']['has_bullet_points']:
            practices.append("Description: Use bullet points to highlight key features")

        if desc_analysis['structure']['has_sections']:
            practices.append("Description: Organize content with clear section headers")

        # Rating strategy
        rating_quality = top_competitor['rating_metrics']['rating_quality']
        if rating_quality in ['excellent', 'good']:
            practices.append(
                f"Ratings: Maintain high rating quality ({top_competitor['rating_metrics']['rating']}★) "
                f"with significant volume ({top_competitor['rating_metrics']['ratings_count']} ratings)"
            )

        return practices[:5]
    def _identify_opportunities(
        self,
        analyses: List[Dict[str, Any]],
        common_keywords: List[str],
        keyword_gaps: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify ASO opportunities based on competitive analysis."""
        opportunities = []

        # Keyword opportunities from gaps
        if keyword_gaps:
            underutilized_keywords = [
                gap['keyword'] for gap in keyword_gaps
                if gap['usage_percentage'] < 50
            ]
            if underutilized_keywords:
                opportunities.append(
                    f"Target underutilized keywords: {', '.join(underutilized_keywords[:5])}"
                )

        # Rating opportunity
        avg_rating = sum(a['rating_metrics']['rating'] for a in analyses) / len(analyses)
        if avg_rating < 4.5:
            opportunities.append(
                f"Category average rating is {avg_rating:.1f} - opportunity to differentiate with higher ratings"
            )

        # Content depth opportunity
        avg_desc_length = sum(
            a['description_analysis']['length'] for a in analyses
        ) / len(analyses)
        if avg_desc_length < 1500:
            opportunities.append(
                "Competitors have relatively short descriptions - opportunity to provide more comprehensive information"
            )

        return opportunities[:5]
