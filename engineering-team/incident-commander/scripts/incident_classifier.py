# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from incident_classifier_base import *  # noqa: F403,E402
from incident_classifier_p0 import format_json_output, format_text_output, parse_input_text  # noqa: F401,E501
from incident_classifier_p1 import interactive_mode  # noqa: F401,E501
from incident_classifier_p2 import main  # noqa: F401,E501
from incident_classifier_c0 import IncidentClassifierMixin0  # noqa: F401
from incident_classifier_c1 import IncidentClassifierMixin1  # noqa: F401
from incident_classifier_c2 import IncidentClassifierMixin2  # noqa: F401
from incident_classifier_c3 import IncidentClassifierMixin3  # noqa: F401
from incident_classifier_c4 import IncidentClassifierMixin4  # noqa: F401
from incident_classifier_c5 import IncidentClassifierMixin5  # noqa: F401
from incident_classifier_c6 import IncidentClassifierMixin6  # noqa: F401


class IncidentClassifier(IncidentClassifierMixin0, IncidentClassifierMixin1, IncidentClassifierMixin2, IncidentClassifierMixin3, IncidentClassifierMixin4, IncidentClassifierMixin5, IncidentClassifierMixin6):
    pass


if __name__ == "__main__":
    main()