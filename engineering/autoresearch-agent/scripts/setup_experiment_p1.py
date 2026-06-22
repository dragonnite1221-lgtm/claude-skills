# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from setup_experiment_base import *  # noqa: F403,E402


DOMAINS = ["engineering", "marketing", "content", "prompts", "custom"]
EVALUATOR_DIR = Path(__file__).parent.parent / "evaluators"
DEFAULT_CONFIG = """# autoresearch global config
default_time_budget_minutes: 5
default_scope: project
dashboard_format: markdown
"""
GITIGNORE_CONTENT = """# autoresearch — experiment logs are local state
**/results.tsv
**/run.log
**/run.*.log
config.yaml
"""
def run_cmd(cmd, cwd=None, timeout=None):
    """Run shell command, return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        cwd=cwd, timeout=timeout
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()
def get_autoresearch_root(scope, project_root=None):
    """Get the .autoresearch root directory based on scope."""
    if scope == "user":
        return Path.home() / ".autoresearch"
    return Path(project_root or ".") / ".autoresearch"
def init_root(root):
    """Initialize .autoresearch root if it doesn't exist."""
    created = False
    if not root.exists():
        root.mkdir(parents=True)
        created = True
        print(f"  Created {root}/")

    config_file = root / "config.yaml"
    if not config_file.exists():
        config_file.write_text(DEFAULT_CONFIG)
        print(f"  Created {config_file}")

    gitignore = root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(GITIGNORE_CONTENT)
        print(f"  Created {gitignore}")

    return created
def create_program_md(experiment_dir, domain, name, target, metric, direction, constraints=""):
    """Generate a program.md template for the experiment."""
    direction_word = "Minimize" if direction == "lower" else "Maximize"
    content = f"""# autoresearch — {name}

## Goal
{direction_word} `{metric}` on `{target}`. {"Lower" if direction == "lower" else "Higher"} is better.

## What the Agent Can Change
- Only `{target}` — this is the single file being optimized.
- Everything inside that file is fair game unless constrained below.

## What the Agent Cannot Change
- The evaluation script (`evaluate.py` or the eval command). It is read-only.
- Dependencies — do not add new packages or imports that aren't already available.
- Any other files in the project unless explicitly noted here.
{f"- Additional constraints: {constraints}" if constraints else ""}

## Strategy
1. First run: establish baseline. Do not change anything.
2. Profile/analyze the current state — understand why the metric is what it is.
3. Try the most obvious improvement first (low-hanging fruit).
4. If that works, push further in the same direction.
5. If stuck, try something orthogonal or radical.
6. Read the git log of previous experiments. Don't repeat failed approaches.

## Simplicity Rule
A small improvement that adds ugly complexity is NOT worth it.
Equal performance with simpler code IS worth it.
Removing code that gets same results is the best outcome.

## Stop When
You don't stop. The human will interrupt you when they're satisfied.
If no improvement in 20+ consecutive runs, change strategy drastically.
"""
    (experiment_dir / "program.md").write_text(content)
def create_config(experiment_dir, target, eval_cmd, metric, direction, time_budget):
    """Write experiment config."""
    content = f"""target: {target}
evaluate_cmd: {eval_cmd}
metric: {metric}
metric_direction: {direction}
metric_grep: ^{metric}:
time_budget_minutes: {time_budget}
created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    (experiment_dir / "config.cfg").write_text(content)
def init_results_tsv(experiment_dir):
    """Create results.tsv with header."""
    tsv = experiment_dir / "results.tsv"
    if tsv.exists():
        print(f"  results.tsv already exists ({tsv.stat().st_size} bytes)")
        return
    tsv.write_text("commit\tmetric\tstatus\tdescription\n")
    print("  Created results.tsv")
def copy_evaluator(experiment_dir, evaluator_name):
    """Copy a built-in evaluator to the experiment directory."""
    source = EVALUATOR_DIR / f"{evaluator_name}.py"
    if not source.exists():
        print(f"  Warning: evaluator '{evaluator_name}' not found in {EVALUATOR_DIR}")
        print(f"  Available: {', '.join(f.stem for f in EVALUATOR_DIR.glob('*.py'))}")
        return False
    dest = experiment_dir / "evaluate.py"
    shutil.copy2(source, dest)
    print(f"  Copied evaluator: {evaluator_name}.py -> evaluate.py")
    return True
def create_branch(path, domain, name):
    """Create and checkout the experiment branch."""
    branch = f"autoresearch/{domain}/{name}"
    result = subprocess.run(
        ["git", "checkout", "-b", branch],
        cwd=path, capture_output=True, text=True
    )
    if result.returncode != 0:
        if "already exists" in result.stderr:
            print(f"  Branch '{branch}' already exists. Checking out...")
            subprocess.run(
                ["git", "checkout", branch],
                cwd=path, capture_output=True, text=True
            )
            return branch
        print(f"  Warning: could not create branch: {result.stderr}")
        return None
    print(f"  Created branch: {branch}")
    return branch
