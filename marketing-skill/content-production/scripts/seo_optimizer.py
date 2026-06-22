# ruff: noqa: F403, F405, E501
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from seo_optimizer_base import *  # noqa: F403,E402
from seo_optimizer_p0 import optimize_content  # noqa: F401,E501
from seo_optimizer_c0 import SEOOptimizerMixin0  # noqa: F401
from seo_optimizer_c1 import SEOOptimizerMixin1  # noqa: F401
from seo_optimizer_c2 import SEOOptimizerMixin2  # noqa: F401
from seo_optimizer_c3 import SEOOptimizerMixin3  # noqa: F401


class SEOOptimizer(SEOOptimizerMixin0, SEOOptimizerMixin1, SEOOptimizerMixin2, SEOOptimizerMixin3):
    pass


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="SEO Content Optimizer - Analyzes and optimizes content for SEO"
    )
    parser.add_argument(
        "file", nargs="?", default=None,
        help="Text file to analyze"
    )
    parser.add_argument(
        "--keyword", "-k", default=None,
        help="Primary keyword to optimize for"
    )
    parser.add_argument(
        "--secondary", "-s", default=None,
        help="Comma-separated secondary keywords"
    )
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as f:
            content = f.read()
        print(optimize_content(content, args.keyword, args.secondary))
    else:
        print("Usage: python seo_optimizer.py <file> [--keyword primary] [--secondary kw1,kw2]")
