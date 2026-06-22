# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_analyzer_base import *  # noqa: F403,E402


class CohortAnalyzer:
    def __init__(self, customers):
        self.customers = customers

    def build_cohorts(self):
        """Group customers by acquisition cohort (month)."""
        cohorts = defaultdict(list)
        for c in self.customers:
            cohorts[c.cohort_month()].append(c)
        return dict(sorted(cohorts.items()))

    def retention_at_month(self, cohort_customers, months_after):
        """
        What fraction of cohort ARR remains `months_after` months after acquisition?
        """
        if not cohort_customers:
            return None

        opening_arr = sum(c.arr for c in cohort_customers)
        if opening_arr == 0:
            return None

        earliest_start = min(c.start_date for c in cohort_customers)
        check_date = earliest_start + timedelta(days=int(months_after * 30.44))

        if check_date > date.today():
            return None  # Future — no data

        retained_arr = sum(
            c.arr for c in cohort_customers
            if c.is_active(check_date)
        )
        return retained_arr / opening_arr

    def retention_curve(self, cohort_customers, max_months=24):
        """Return retention at months 0, 3, 6, 9, 12, 18, 24."""
        checkpoints = [0, 3, 6, 9, 12, 18, 24]
        checkpoints = [m for m in checkpoints if m <= max_months]
        curve = {}
        for m in checkpoints:
            rate = self.retention_at_month(cohort_customers, m)
            if rate is not None:
                curve[m] = rate
        return curve

    def cohort_report(self):
        """Returns dict: cohort → {size, opening_arr, retention_curve}."""
        cohorts = self.build_cohorts()
        report = {}
        for cohort_month, customers in cohorts.items():
            curve = self.retention_curve(customers)
            report[cohort_month] = {
                "customer_count": len(customers),
                "opening_arr":    sum(c.arr for c in customers),
                "churned_count":  sum(1 for c in customers if c.is_churned()),
                "current_retention": curve.get(12, curve.get(max(curve.keys()) if curve else 0)),
                "retention_curve": curve,
            }
        return report

    def identify_at_risk(self, tenure_months_max=6, health_threshold=60):
        """
        Identify at-risk customers based on:
        - Low health score (if available)
        - Short tenure (haven't proved long-term value)
        - High contraction signals
        """
        at_risk = []
        for c in self.customers:
            if c.is_churned():
                continue
            reasons = []
            score = 0

            # Health score signal
            if c.health_score is not None and c.health_score < health_threshold:
                reasons.append(f"Health score {c.health_score:.0f} < {health_threshold}")
                score += 40

            # Early tenure risk
            tenure = c.tenure_months()
            if tenure < tenure_months_max:
                reasons.append(f"Tenure {tenure:.1f} months (< {tenure_months_max})")
                score += 20

            # Contraction signal
            if c.contraction_arr > 0:
                contraction_pct = c.contraction_arr / c.arr
                reasons.append(f"Contraction {contraction_pct:.0%} of ARR")
                score += 30

            # No expansion in mature account
            if tenure > 12 and c.expansion_arr == 0:
                reasons.append("No expansion after 12+ months (stagnant)")
                score += 10

            if score > 0:
                at_risk.append({
                    "customer_id": c.customer_id,
                    "name":        c.name,
                    "segment":     c.segment,
                    "arr":         c.arr,
                    "tenure_months": round(tenure, 1),
                    "health_score": c.health_score,
                    "risk_score":  score,
                    "risk_reasons": reasons,
                })

        return sorted(at_risk, key=lambda x: -x["risk_score"])
