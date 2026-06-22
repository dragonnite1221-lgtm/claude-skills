# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_bootstrapper_base import *  # noqa: F403,E402
# fmt: off
from project_bootstrapper_p1 import STACK_TEMPLATES  # noqa: E402,E501
from project_bootstrapper_p2 import generate_env_example, generate_readme  # noqa: E402,E501
from project_bootstrapper_p3 import generate_docker_compose, generate_dockerfile, generate_gitignore  # noqa: E402,E501
# fmt: on


def scaffold_project(config: Dict[str, Any], output_dir: str, dry_run: bool = False) -> Dict[str, Any]:
    """Generate project scaffolding."""
    stack = config.get("stack", "nextjs")
    template = STACK_TEMPLATES.get(stack, STACK_TEMPLATES["nextjs"])
    files_created = []

    # Create directories
    for d in template.get("dirs", []):
        path = os.path.join(output_dir, d)
        if not dry_run:
            os.makedirs(path, exist_ok=True)
        files_created.append({"path": d + "/", "type": "directory"})

    # Create template files
    all_files = {}

    # Package/requirements file
    for key in ("package.json", "requirements.txt"):
        if key in template:
            all_files[key] = template[key](config)

    if "tsconfig.json" in template:
        all_files["tsconfig.json"] = template["tsconfig.json"](config)

    # Stack-specific files
    all_files.update(template.get("files", {}))

    # Common files
    all_files["README.md"] = generate_readme(config)
    all_files[".env.example"] = generate_env_example(config)
    all_files[".gitignore"] = generate_gitignore(stack)
    all_files["docker-compose.yml"] = generate_docker_compose(config)
    all_files["Dockerfile"] = generate_dockerfile(config)

    # Write files
    for filepath, content in all_files.items():
        full_path = os.path.join(output_dir, filepath)
        if not dry_run:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(content)
        files_created.append({"path": filepath, "type": "file", "size": len(content)})

    return {
        "generated_at": datetime.now().isoformat(),
        "project_name": config.get("name", "my-project"),
        "stack": stack,
        "output_dir": output_dir,
        "files_created": files_created,
        "total_files": len([f for f in files_created if f["type"] == "file"]),
        "total_dirs": len([f for f in files_created if f["type"] == "directory"]),
        "dry_run": dry_run
    }
def main():
    parser = argparse.ArgumentParser(description="Bootstrap SaaS project from config")
    parser.add_argument("input", help="Path to project config JSON")
    parser.add_argument("--output-dir", type=str, default="./my-project", help="Output directory")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")

    args = parser.parse_args()

    with open(args.input) as f:
        config = json.load(f)

    result = scaffold_project(config, args.output_dir, args.dry_run)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Project '{result['project_name']}' scaffolded at {result['output_dir']}")
        print(f"Stack: {result['stack']}")
        print(f"Created: {result['total_files']} files, {result['total_dirs']} directories")
        if result["dry_run"]:
            print("\n[DRY RUN] No files were created. Files that would be created:")
        print("\nFiles:")
        for f in result["files_created"]:
            prefix = "📁" if f["type"] == "directory" else "📄"
            size = f" ({f.get('size', 0)} bytes)" if f.get("size") else ""
            print(f"  {prefix} {f['path']}{size}")
