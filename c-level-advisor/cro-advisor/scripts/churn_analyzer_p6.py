# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from churn_analyzer_base import *  # noqa: F403,E402
# fmt: off
from churn_analyzer_p1 import Customer  # noqa: E402,E501
# fmt: on


SAMPLE_CSV = """customer_id,name,segment,arr,start_date,churn_date,expansion_arr,contraction_arr,health_score
C001,Acme Manufacturing,Enterprise,120000,2023-01-15,,45000,0,82
C002,TechStart Inc,Mid-Market,28000,2023-02-01,,8000,0,74
C003,Global Retail Co,Enterprise,250000,2023-01-05,,0,25000,45
C004,MedTech Solutions,Mid-Market,45000,2023-03-10,,15000,0,88
C005,FinServ Holdings,Enterprise,185000,2023-01-20,2023-09-15,0,0,
C006,StartupHub Network,SMB,12000,2023-04-01,,0,3000,55
C007,EduPlatform Inc,Mid-Market,32000,2023-02-15,,10000,0,91
C008,BioLab Analytics,Enterprise,95000,2023-01-10,,20000,0,78
C009,RegionalBank Corp,Enterprise,310000,2023-03-01,,75000,0,85
C010,CloudOps Systems,Mid-Market,38000,2023-05-01,2024-01-10,0,0,
C011,InsurTech Platform,Mid-Market,55000,2023-06-15,,0,0,62
C012,LegalAI Corp,SMB,18000,2023-07-01,,5000,0,79
C013,RetailChain Ltd,Enterprise,140000,2023-04-20,,0,20000,41
C014,DataPipeline Co,Mid-Market,42000,2023-08-01,,12000,0,83
C015,NanoTech Startup,SMB,9500,2023-09-15,2024-02-28,0,0,
C016,MedDevice Corp,Enterprise,220000,2023-02-28,,60000,0,92
C017,ConsultingFirm XYZ,SMB,15000,2023-10-01,,0,5000,38
C018,GovTech Solutions,Enterprise,175000,2023-11-15,,0,0,71
C019,AgriData Systems,Mid-Market,31000,2024-01-10,,8000,0,77
C020,HealthcarePlus,Mid-Market,62000,2024-02-01,,0,0,65
"""
def load_customers_from_csv(csv_text):
    reader = csv.DictReader(StringIO(csv_text))
    customers = []
    errors = []
    for i, row in enumerate(reader, start=2):
        try:
            c = Customer(
                customer_id=row.get("customer_id", f"row_{i}"),
                name=row.get("name", f"Customer {i}"),
                segment=row.get("segment", ""),
                arr=row.get("arr", 0),
                start_date=row.get("start_date", ""),
                churn_date=row.get("churn_date", None) or None,
                expansion_arr=row.get("expansion_arr", 0) or 0,
                contraction_arr=row.get("contraction_arr", 0) or 0,
                health_score=row.get("health_score", None) or None,
            )
            customers.append(c)
        except (ValueError, KeyError) as e:
            errors.append(f"  Row {i}: {e}")
    if errors:
        print("⚠️  Skipped rows with errors:")
        for err in errors:
            print(err)
    return customers
def parse_period(period_str):
    """Parse 'YYYY-QN' or 'YYYY-MM' into (start_date, end_date)."""
    if not period_str:
        today = date.today()
        q = (today.month - 1) // 3
        start = date(today.year, q * 3 + 1, 1)
        # End of current quarter
        end_month = start.month + 2
        end_year = start.year + (end_month - 1) // 12
        end_month = ((end_month - 1) % 12) + 1
        import calendar
        end_day = calendar.monthrange(end_year, end_month)[1]
        return start, date(end_year, end_month, end_day)

    import calendar
    if "-Q" in period_str:
        year, qpart = period_str.split("-Q")
        year = int(year)
        q = int(qpart)
        start_month = (q - 1) * 3 + 1
        end_month = start_month + 2
        start = date(year, start_month, 1)
        end = date(year, end_month, calendar.monthrange(year, end_month)[1])
        return start, end

    # YYYY-MM
    year, month = period_str.split("-")
    year, month = int(year), int(month)
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    return start, end
