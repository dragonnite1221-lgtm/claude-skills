# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p3 import DataProfiler  # noqa: F401,E501
from data_quality_validator_p5 import QualityScoreCalculator  # noqa: F401,E501
from data_quality_validator_p6 import DataContractValidator  # noqa: F401,E501
from data_quality_validator_p7 import ReportGenerator  # noqa: F401,E501
from data_quality_validator_p8 import DataLoader  # noqa: F401,E501


def cmd_contract(args):
    """Validate against data contract"""
    logger.info(f"Loading data from {args.input}")
    data = DataLoader.load(args.input)

    logger.info(f"Loading contract from {args.contract}")
    contract_validator = DataContractValidator()
    contract = contract_validator.load_contract(args.contract)

    results = contract_validator.validate_contract(data, contract)

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

    # Exit with error if contract validation failed
    errors = sum(1 for r in results if not r.passed and r.severity == "error")
    if errors > 0:
        sys.exit(1)


def cmd_schema(args):
    """Generate schema from data"""
    logger.info(f"Loading data from {args.input}")
    data = DataLoader.load(args.input)

    if not data:
        logger.error("Empty dataset")
        sys.exit(1)

    # Profile to detect types
    profiler = DataProfiler()
    profile = profiler.profile(data, name=Path(args.input).stem)

    # Generate schema
    schema = {
        "name": profile.name,
        "version": "1.0",
        "columns": []
    }

    for col in profile.columns:
        col_schema = {
            "name": col.name,
            "type": col.data_type,
            "nullable": col.null_percentage > 0,
            "description": ""
        }

        if col.unique_percentage > 99:
            col_schema["unique"] = True

        if col.min_value is not None:
            col_schema["min_value"] = col.min_value
            col_schema["max_value"] = col.max_value

        if col.min_length is not None:
            col_schema["min_length"] = col.min_length
            col_schema["max_length"] = col.max_length

        if col.detected_pattern:
            col_schema["pattern"] = col.detected_pattern

        # Add allowed values for low-cardinality columns
        if col.unique_count <= 20 and col.unique_percentage < 10:
            col_schema["allowed_values"] = [v[0] for v in col.top_values]

        schema["columns"].append(col_schema)

    output = json.dumps(schema, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Schema saved to {args.output}")
    else:
        print(output)
