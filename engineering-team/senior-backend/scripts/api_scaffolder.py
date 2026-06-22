# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from api_scaffolder_base import *  # noqa: F403,E402
from api_scaffolder_p0 import load_spec, load_yaml_as_json  # noqa: F401,E501
from api_scaffolder_p1 import openapi_type_to_ts  # noqa: F401,E501
from api_scaffolder_p2 import extract_path_params, generate_zod_schema, openapi_path_to_express, to_camel_case, to_pascal_case  # noqa: F401,E501
from api_scaffolder_p3 import main  # noqa: F401,E501
from api_scaffolder_c0 import APIScaffolderMixin0  # noqa: F401
from api_scaffolder_c1 import APIScaffolderMixin1  # noqa: F401
from api_scaffolder_c2 import APIScaffolderMixin2  # noqa: F401
from api_scaffolder_c3 import APIScaffolderMixin3  # noqa: F401


class APIScaffolder(APIScaffolderMixin0, APIScaffolderMixin1, APIScaffolderMixin2, APIScaffolderMixin3):
    pass


if __name__ == '__main__':
    main()
