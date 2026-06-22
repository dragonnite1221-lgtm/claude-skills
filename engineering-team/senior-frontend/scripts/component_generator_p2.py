# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from component_generator_base import *  # noqa: F403,E402
# fmt: off
from component_generator_p1 import TEMPLATES, to_pascal_case  # noqa: E402,E501
# fmt: on


def to_kebab_case(name: str) -> str:
    """Convert PascalCase to kebab-case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper() and i > 0:
            result.append('-')
        result.append(char.lower())
    return ''.join(result)
def generate_component(
    name: str,
    output_dir: Path,
    component_type: str = "client",
    with_test: bool = False,
    with_story: bool = False,
    with_index: bool = True,
    flat: bool = False,
) -> dict:
    """Generate component files."""
    pascal_name = to_pascal_case(name)
    kebab_name = to_kebab_case(pascal_name)

    # Determine output path
    if flat:
        component_dir = output_dir
    else:
        component_dir = output_dir / pascal_name

    files_created = []

    # Create directory
    component_dir.mkdir(parents=True, exist_ok=True)

    # Generate main component file
    if component_type == "hook":
        main_file = component_dir / f"use{pascal_name}.ts"
        template = TEMPLATES["hook"]
    else:
        main_file = component_dir / f"{pascal_name}.tsx"
        template = TEMPLATES[component_type]

    content = template.format(name=pascal_name)
    main_file.write_text(content)
    files_created.append(str(main_file))

    # Generate test file
    if with_test and component_type != "hook":
        test_file = component_dir / f"{pascal_name}.test.tsx"
        test_content = TEMPLATES["test"].format(name=pascal_name)
        test_file.write_text(test_content)
        files_created.append(str(test_file))

    # Generate story file
    if with_story and component_type != "hook":
        story_file = component_dir / f"{pascal_name}.stories.tsx"
        story_content = TEMPLATES["story"].format(name=pascal_name)
        story_file.write_text(story_content)
        files_created.append(str(story_file))

    # Generate index file
    if with_index and not flat:
        index_file = component_dir / "index.ts"
        index_content = TEMPLATES["index"].format(name=pascal_name)
        index_file.write_text(index_content)
        files_created.append(str(index_file))

    return {
        "name": pascal_name,
        "type": component_type,
        "directory": str(component_dir),
        "files": files_created,
    }
def print_result(result: dict, verbose: bool = False) -> None:
    """Print generation result."""
    print(f"\n{'='*50}")
    print(f"Component Generated: {result['name']}")
    print(f"{'='*50}")
    print(f"Type: {result['type']}")
    print(f"Directory: {result['directory']}")
    print(f"\nFiles created:")
    for file in result['files']:
        print(f"  - {file}")
    print(f"{'='*50}\n")

    # Print usage hint
    if result['type'] != 'hook':
        print("Usage:")
        print(f"  import {{ {result['name']} }} from '@/components/{result['name']}';")
        print(f"\n  <{result['name']}>Content</{result['name']}>")
    else:
        print("Usage:")
        print(f"  import {{ use{result['name']} }} from '@/hooks/use{result['name']}';")
        print(f"\n  const {{ isLoading, error }} = use{result['name']}();")
