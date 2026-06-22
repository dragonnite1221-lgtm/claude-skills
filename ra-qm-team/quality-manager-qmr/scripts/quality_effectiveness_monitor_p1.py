# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from quality_effectiveness_monitor_base import *  # noqa: F403,E402
from quality_effectiveness_monitor_p0 import QualityMetric, format_qms_report  # noqa: F401,E501


def main():
    parser = argparse.ArgumentParser(description="QMS Effectiveness Monitor")
    parser.add_argument("--metrics", type=str, help="CSV file with quality metrics")
    parser.add_argument("--qms-data", type=str, help="JSON file with QMS data")
    parser.add_argument("--dashboard", action="store_true", help="Generate dashboard summary")
    parser.add_argument("--predict", action="store_true", help="Include predictive analytics")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()
    monitor = QMSEffectivenessMonitor()

    if args.metrics:
        metrics = monitor.load_csv(args.metrics)
        report = monitor.analyze(metrics)
    elif args.qms_data:
        with open(args.qms_data) as f:
            data = json.load(f)
        # Convert to QualityMetric objects
        metrics = [QualityMetric(**m) for m in data.get("metrics", [])]
        report = monitor.analyze(metrics)
    else:
        # Demo data
        demo_metrics = [
            QualityMetric("M001", "Customer Complaint Rate", "Customer", "2026-03-01", 0.8, "per 1000", 1.0, 1.5, 0.5),
            QualityMetric("M002", "Defect Rate PPM", "Quality", "2026-03-01", 125, "PPM", 100, 500, 0, trend_direction="down", sigma_level=4.2),
            QualityMetric("M003", "On-Time Delivery", "Operations", "2026-03-01", 96.5, "%", 98, 0, 95, trend_direction="down"),
            QualityMetric("M004", "CAPA Closure Rate", "Quality", "2026-03-01", 92.0, "%", 100, 0, 90, is_alert=True),
            QualityMetric("M005", "Supplier Defect Rate", "Supplier", "2026-03-01", 450, "PPM", 200, 1000, 0, is_critical=True),
        ]
        # Simulate time series
        all_metrics = []
        for i in range(30):
            for dm in demo_metrics:
                new_metric = QualityMetric(
                    metric_id=dm.metric_id,
                    metric_name=dm.metric_name,
                    category=dm.category,
                    date=f"2026-03-{i+1:02d}",
                    value=dm.value + (i * 0.1) if dm.metric_name == "Customer Complaint Rate" else dm.value,
                    unit=dm.unit,
                    target=dm.target,
                    upper_limit=dm.upper_limit,
                    lower_limit=dm.lower_limit
                )
                all_metrics.append(new_metric)
        report = monitor.analyze(all_metrics)

    if args.output == "json":
        result = asdict(report)
        print(json.dumps(result, indent=2))
    else:
        print(format_qms_report(report))
