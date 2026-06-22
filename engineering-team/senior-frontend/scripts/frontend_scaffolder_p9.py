# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from frontend_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from frontend_scaffolder_p1 import TEMPLATES  # noqa: E402,E501
from frontend_scaffolder_p2 import FEATURES  # noqa: E402,E501
from frontend_scaffolder_p6 import FILE_CONTENTS, generate_structure  # noqa: E402,E501
from frontend_scaffolder_p8 import get_config_templates  # noqa: E402,E501
# fmt: on


def generate_config_files(
    project_path: Path,
    template: str,
    project_name: str,
    features: List[str],
    dry_run: bool = False
) -> List[str]:
    """Generate configuration files."""
    created_files = []
    config_templates = get_config_templates(project_name, template, features)

    template_config = TEMPLATES[template]
    for config_file in template_config["config_files"]:
        file_path = project_path / config_file
        if config_file in config_templates:
            if not dry_run:
                file_path.write_text(config_templates[config_file])
            created_files.append(str(file_path))

    return created_files
def scaffold_project(
    name: str,
    output_dir: Path,
    template: str = "nextjs",
    features: Optional[List[str]] = None,
    dry_run: bool = False,
) -> Dict:
    """Scaffold a complete frontend project."""
    features = features or []
    project_path = output_dir / name

    if project_path.exists() and not dry_run:
        return {"error": f"Directory already exists: {project_path}"}

    template_config = TEMPLATES.get(template)
    if not template_config:
        return {"error": f"Unknown template: {template}"}

    created_files = []

    # Create project directory
    if not dry_run:
        project_path.mkdir(parents=True, exist_ok=True)

    # Generate base structure
    created_files.extend(
        generate_structure(project_path, template_config["structure"], dry_run)
    )

    # Generate config files
    created_files.extend(
        generate_config_files(project_path, template, name, features, dry_run)
    )

    # Add feature files
    for feature in features:
        if feature in FEATURES:
            for file_path, content_key in FEATURES[feature]["files"].items():
                full_path = project_path / file_path
                if not dry_run:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    content = FILE_CONTENTS.get(content_key, f"// TODO: Implement {content_key}")
                    full_path.write_text(content)
                created_files.append(str(full_path))

    return {
        "name": name,
        "template": template,
        "template_name": template_config["name"],
        "features": features,
        "path": str(project_path),
        "files_created": len(created_files),
        "files": created_files,
        "next_steps": [
            f"cd {name}",
            "npm install",
            "npm run dev",
        ],
    }
def print_result(result: Dict) -> None:
    """Print scaffolding result."""
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        return

    print(f"\n{'='*60}")
    print(f"Project Scaffolded: {result['name']}")
    print(f"{'='*60}")
    print(f"Template: {result['template_name']}")
    print(f"Location: {result['path']}")
    print(f"Files Created: {result['files_created']}")

    if result["features"]:
        print(f"Features: {', '.join(result['features'])}")

    print(f"\nNext Steps:")
    for step in result["next_steps"]:
        print(f"  $ {step}")

    print(f"{'='*60}\n")
