# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from forecast_builder_base import *  # noqa: F403,E402
from forecast_builder_p0 import main, safe_divide, simple_linear_regression  # noqa: F401,E501
from forecast_builder_c0 import ForecastBuilderMixin0  # noqa: F401
from forecast_builder_c1 import ForecastBuilderMixin1  # noqa: F401
from forecast_builder_c2 import ForecastBuilderMixin2  # noqa: F401
from forecast_builder_c3 import ForecastBuilderMixin3  # noqa: F401
from forecast_builder_c4 import ForecastBuilderMixin4  # noqa: F401


class ForecastBuilder(ForecastBuilderMixin0, ForecastBuilderMixin1, ForecastBuilderMixin2, ForecastBuilderMixin3, ForecastBuilderMixin4):
    pass


if __name__ == "__main__":
    main()
