# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from data_quality_validator_base import *  # noqa: F403,E402
from data_quality_validator_p0 import ColumnProfile, ColumnSchema, DataProfile, DataSchema, QualityScore, ValidationResult  # noqa: F401,E501
from data_quality_validator_p1 import BaseValidator, TypeDetector  # noqa: F401,E501
from data_quality_validator_p2 import AnomalyDetector  # noqa: F401,E501
from data_quality_validator_p3 import DataProfiler  # noqa: F401,E501
from data_quality_validator_p4 import GreatExpectationsGenerator  # noqa: F401,E501
from data_quality_validator_p5 import QualityScoreCalculator  # noqa: F401,E501
from data_quality_validator_p6 import DataContractValidator  # noqa: F401,E501
from data_quality_validator_p7 import ReportGenerator  # noqa: F401,E501
from data_quality_validator_p8 import DataLoader, SchemaLoader  # noqa: F401,E501
from data_quality_validator_p9 import cmd_generate_suite, cmd_profile, cmd_validate  # noqa: F401,E501
from data_quality_validator_p10 import cmd_contract, cmd_schema  # noqa: F401,E501
from data_quality_validator_p11 import main  # noqa: F401,E501
from data_quality_validator_c0 import SchemaValidatorMixin0  # noqa: F401
from data_quality_validator_c1 import SchemaValidatorMixin1  # noqa: F401
from data_quality_validator_c2 import SchemaValidatorMixin2  # noqa: F401


class SchemaValidator(SchemaValidatorMixin0, SchemaValidatorMixin1, SchemaValidatorMixin2, BaseValidator):
    pass


if __name__ == '__main__':
    main()
