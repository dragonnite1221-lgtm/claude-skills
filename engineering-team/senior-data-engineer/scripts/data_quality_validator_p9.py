# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p2 import AnomalyDetector  # noqa: F401,E501
from data_quality_validator_p3 import DataProfiler  # noqa: F401,E501
from data_quality_validator_p4 import GreatExpectationsGenerator  # noqa: F401,E501
from data_quality_validator_p5 import QualityScoreCalculator  # noqa: F401,E501
from data_quality_validator_p7 import ReportGenerator  # noqa: F401,E501
from data_quality_validator_p8 import DataLoader, SchemaLoader  # noqa: F401,E501


def cmd_validate(args):
    """Run validation against schema"""
    logger.info(f"Loading data from {args.input}")
    data = DataLoader.load(args.input)

    results = []

    if args.schema:
        logger.info(f"Loading schema from {args.schema}")
        schema = SchemaLoader.load(args.schema)

        validator = SchemaValidator()
        results = validator.validate(data, schema)

    if args.detect_anomalies:
        logger.info("Running anomaly detection")
        anomaly_detector = AnomalyDetector()
        anomaly_results = anomaly_detector.validate(data)
        results.extend(anomaly_results)

    # Profile data
    profiler = DataProfiler()
    profile = profiler.profile(data, name=Path(args.input).stem)

    # Calculate score
    score_calc = QualityScoreCalculator()
    score = score_calc.calculate(profile, results)

    # Generate report
    reporter = ReportGenerator()

    if args.json:
        report = reporter.generate_json_report(profile, results, score)
        output = json.dumps(report, indent=2)
    else:
        output = reporter.generate_text_report(profile, results, score)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Report saved to {args.output}")
    else:
        print(output)

    # Exit with error if validation failed
    errors = sum(1 for r in results if not r.passed and r.severity == "error")
    if errors > 0:
        sys.exit(1)


def cmd_profile(args):
    """Generate data profile"""
    logger.info(f"Loading data from {args.input}")
    data = DataLoader.load(args.input)

    profiler = DataProfiler()
    profile = profiler.profile(data, name=Path(args.input).stem)

    if args.json or args.output:
        output = json.dumps(asdict(profile), indent=2, default=str)
    else:
        # Text output
        lines = []
        lines.append(f"Dataset: {profile.name}")
        lines.append(f"Rows: {profile.row_count:,}")
        lines.append(f"Columns: {profile.column_count}")
        lines.append(f"Duplicate rows: {profile.duplicate_rows:,}")
        lines.append(f"\nColumn Profiles:")

        for col in profile.columns:
            lines.append(f"\n  {col.name} ({col.data_type})")
            lines.append(f"    Nulls: {col.null_percentage:.1f}%")
            lines.append(f"    Unique: {col.unique_percentage:.1f}%")
            if col.mean is not None:
                lines.append(f"    Stats: min={col.min_value}, max={col.max_value}, mean={col.mean:.2f}")

        output = "\n".join(lines)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Profile saved to {args.output}")
    else:
        print(output)


def cmd_generate_suite(args):
    """Generate Great Expectations suite"""
    logger.info(f"Loading data from {args.input}")
    data = DataLoader.load(args.input)

    # Profile first
    profiler = DataProfiler()
    profile = profiler.profile(data, name=Path(args.input).stem)

    # Generate suite
    generator = GreatExpectationsGenerator()
    suite = generator.generate_suite(profile)

    output = json.dumps(suite, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Expectation suite saved to {args.output}")
    else:
        print(output)
