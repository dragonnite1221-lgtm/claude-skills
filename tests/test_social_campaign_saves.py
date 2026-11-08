import copy
import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "marketing-skill/social-media-analyzer/scripts/calculate_metrics.py"
SPEC = importlib.util.spec_from_file_location("social_campaign_saves", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
Calculator = MODULE.SocialMediaMetricsCalculator


class CampaignSaveTests(unittest.TestCase):
    def test_saves_only_campaign_matches_post(self):
        post = {"saves": 10, "reach": 100}
        calculator = Calculator({"posts": [post]})
        result = calculator.calculate_campaign_metrics()
        self.assertEqual(result["total_engagements"], 10)
        self.assertEqual(result["avg_engagement_rate"], 10.0)
        self.assertEqual(result["avg_engagement_rate"], calculator.calculate_engagement_rate(post))

    def test_sample_totals_include_all_four_actions(self):
        posts = [
            {"likes": 342, "comments": 28, "shares": 15, "saves": 45, "reach": 5200},
            {"likes": 587, "comments": 42, "shares": 31, "saves": 68, "reach": 8900},
            {"likes": 298, "comments": 19, "shares": 12, "saves": 34, "reach": 4100},
        ]
        calculator = Calculator({"posts": posts, "total_spend": 500})
        result = calculator.analyze_all()
        self.assertEqual(result["campaign_metrics"]["total_engagements"], 1521)
        self.assertAlmostEqual(result["campaign_metrics"]["avg_engagement_rate"], 1521 / 18200 * 100)
        self.assertEqual(result["roi_metrics"]["cost_per_engagement"], 0.33)
        self.assertEqual(result["roi_metrics"]["estimated_value"], 3802.5)
        self.assertEqual(result["roi_metrics"]["roi_percentage"], 660.5)

    def test_saves_propagate_to_roi_without_affecting_clicks(self):
        calculator = Calculator({"total_spend": 25, "posts": [{"saves": 10, "reach": 100, "clicks": 5, "impressions": 200}]})
        self.assertEqual(calculator.calculate_roi_metrics(), {"total_spend": 25, "cost_per_engagement": 2.5, "cost_per_click": 5.0, "estimated_value": 25.0, "roi_percentage": 0.0})
        self.assertEqual(calculator.calculate_campaign_metrics()["ctr"], 2.5)

    def test_missing_saves_equals_explicit_zero(self):
        data = {"posts": [{"likes": 4, "comments": 2, "shares": 1, "reach": 100}], "total_spend": 14}
        with_zero = copy.deepcopy(data)
        with_zero["posts"][0]["saves"] = 0
        self.assertEqual(Calculator(data).calculate_campaign_metrics(), Calculator(with_zero).calculate_campaign_metrics())
        self.assertEqual(Calculator(data).calculate_roi_metrics(), Calculator(with_zero).calculate_roi_metrics())

    def test_empty_and_zero_reach_remain_safe(self):
        self.assertEqual(Calculator({}).calculate_campaign_metrics()["total_engagements"], 0)
        result = Calculator({"posts": [{"saves": 3}]}).calculate_campaign_metrics()
        self.assertEqual(result["total_engagements"], 3)
        self.assertEqual(result["avg_engagement_rate"], 0.0)

    def test_multiple_posts_use_aggregate_reach(self):
        result = Calculator({"posts": [{"saves": 10, "reach": 100}, {"saves": 5, "reach": 200}]}).calculate_campaign_metrics()
        self.assertEqual(result["total_engagements"], 15)
        self.assertEqual(result["avg_engagement_rate"], 5.0)

    def test_input_is_not_mutated_and_post_ranking_kept(self):
        data = {"posts": [{"post_id": "a", "saves": 1, "reach": 100}, {"post_id": "b", "saves": 5, "reach": 100}]}
        original = copy.deepcopy(data)
        result = Calculator(data).analyze_all()
        self.assertEqual(data, original)
        self.assertEqual([p["post_id"] for p in result["top_posts"]], ["b", "a"])
        self.assertEqual([p["engagement_rate"] for p in result["top_posts"]], [5.0, 1.0])

    def test_aggregation_is_independent_of_post_order(self):
        posts = [{"likes": 7, "saves": 3, "reach": 50}, {"comments": 2, "shares": 4, "reach": 80}]
        first = Calculator({"posts": posts, "total_spend": 20})
        second = Calculator({"posts": posts[::-1], "total_spend": 20})
        self.assertEqual(first.calculate_campaign_metrics(), second.calculate_campaign_metrics())
        self.assertEqual(first.calculate_roi_metrics(), second.calculate_roi_metrics())


if __name__ == "__main__":
    unittest.main()
