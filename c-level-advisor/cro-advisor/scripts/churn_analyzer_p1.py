# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_analyzer_base import *  # noqa: F403,E402


class Customer:
    def __init__(self, customer_id, name, segment, arr, start_date,
                 churn_date=None, expansion_arr=0.0, contraction_arr=0.0,
                 health_score=None):
        self.customer_id = customer_id
        self.name = name
        self.segment = segment
        self.arr = float(arr)
        self.start_date = self._parse_date(start_date)
        self.churn_date = self._parse_date(churn_date) if churn_date else None
        self.expansion_arr = float(expansion_arr or 0)
        self.contraction_arr = float(contraction_arr or 0)
        self.health_score = float(health_score) if health_score else None

    @staticmethod
    def _parse_date(value):
        if not value or str(value).strip() in ("", "None", "null"):
            return None
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {value!r}")

    def is_churned(self):
        return self.churn_date is not None

    def is_active(self, as_of=None):
        as_of = as_of or date.today()
        if self.churn_date and self.churn_date <= as_of:
            return False
        return self.start_date <= as_of

    def tenure_days(self, as_of=None):
        as_of = as_of or date.today()
        end = self.churn_date if self.churn_date else as_of
        return (end - self.start_date).days

    def tenure_months(self, as_of=None):
        return self.tenure_days(as_of) / 30.44

    def cohort_month(self):
        """Acquisition cohort: YYYY-MM of start_date."""
        return self.start_date.strftime("%Y-%m")

    def cohort_quarter(self):
        q = (self.start_date.month - 1) // 3 + 1
        return f"Q{q} {self.start_date.year}"

    def net_arr(self):
        """Current ARR + expansion - contraction."""
        return self.arr + self.expansion_arr - self.contraction_arr

    def days_since_acquisition(self, as_of=None):
        as_of = as_of or date.today()
        return (as_of - self.start_date).days
