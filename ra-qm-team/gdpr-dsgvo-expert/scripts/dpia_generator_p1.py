# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dpia_generator_base import *  # noqa: F403,E402


DPIA_TRIGGERS = {
    "systematic_monitoring": {
        "description": "Systematic monitoring of publicly accessible area",
        "article": "Art. 35(3)(c)",
        "weight": 10
    },
    "large_scale_special_category": {
        "description": "Large-scale processing of special category data (Art. 9)",
        "article": "Art. 35(3)(b)",
        "weight": 10
    },
    "automated_decision_making": {
        "description": "Automated decision-making with legal/significant effects",
        "article": "Art. 35(3)(a)",
        "weight": 10
    },
    "evaluation_scoring": {
        "description": "Evaluation or scoring of individuals",
        "article": "WP29 Guidelines",
        "weight": 7
    },
    "sensitive_data": {
        "description": "Processing of sensitive data or highly personal data",
        "article": "WP29 Guidelines",
        "weight": 7
    },
    "large_scale": {
        "description": "Data processed on a large scale",
        "article": "WP29 Guidelines",
        "weight": 6
    },
    "data_matching": {
        "description": "Matching or combining datasets",
        "article": "WP29 Guidelines",
        "weight": 5
    },
    "vulnerable_subjects": {
        "description": "Data concerning vulnerable data subjects",
        "article": "WP29 Guidelines",
        "weight": 7
    },
    "innovative_technology": {
        "description": "Innovative use or applying new technological solutions",
        "article": "WP29 Guidelines",
        "weight": 5
    },
    "cross_border_transfer": {
        "description": "Transfer of data outside the EU/EEA",
        "article": "GDPR Chapter V",
        "weight": 5
    }
}
