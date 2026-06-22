# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from dockerfile_analyzer_base import *  # noqa: F403,E402


BASE_IMAGE_SIZES = {
    "scratch": 0,
    "alpine": 7,
    "distroless/static": 2,
    "distroless/base": 20,
    "distroless/cc": 25,
    "debian-slim": 80,
    "debian": 120,
    "ubuntu": 78,
    "python-slim": 130,
    "python-alpine": 50,
    "python": 900,
    "node-alpine": 130,
    "node-slim": 200,
    "node": 1000,
    "golang-alpine": 250,
    "golang": 800,
    "rust-slim": 750,
    "rust": 1400,
    "nginx-alpine": 40,
    "nginx": 140,
}
DEMO_DOCKERFILE = """FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV SECRET_KEY=mysecretkey123
EXPOSE 8000 5432 6379
CMD python manage.py runserver 0.0.0.0:8000
"""
def parse_dockerfile(content):
    """Parse Dockerfile into structured instructions."""
    instructions = []
    current = ""

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith("\\"):
            current += stripped[:-1] + " "
            continue
        current += stripped
        # Parse instruction
        match = re.match(r"^(\w+)\s+(.*)", current.strip())
        if match:
            instructions.append({
                "instruction": match.group(1).upper(),
                "args": match.group(2),
                "raw": current.strip(),
            })
        current = ""

    return instructions
def analyze_layers(instructions):
    """Count and classify layers."""
    layer_instructions = {"FROM", "RUN", "COPY", "ADD"}
    layers = [i for i in instructions if i["instruction"] in layer_instructions]
    stages = [i for i in instructions if i["instruction"] == "FROM"]
    return {
        "total_layers": len(layers),
        "stages": len(stages),
        "is_multistage": len(stages) > 1,
        "run_count": sum(1 for i in instructions if i["instruction"] == "RUN"),
        "copy_count": sum(1 for i in instructions if i["instruction"] == "COPY"),
        "add_count": sum(1 for i in instructions if i["instruction"] == "ADD"),
    }
def analyze_base_image(instructions):
    """Analyze base image choice."""
    from_instructions = [i for i in instructions if i["instruction"] == "FROM"]
    if not from_instructions:
        return {"image": "unknown", "tag": "unknown", "estimated_size_mb": 0}

    last_from = from_instructions[-1]["args"].split()[0]
    parts = last_from.split(":")
    image = parts[0]
    tag = parts[1] if len(parts) > 1 else "latest"

    # Estimate size
    size = 0
    image_base = image.split("/")[-1]
    for key, val in BASE_IMAGE_SIZES.items():
        if key in f"{image_base}-{tag}" or key == image_base:
            size = val
            break

    return {
        "image": image,
        "tag": tag,
        "estimated_size_mb": size,
        "is_alpine": "alpine" in tag,
        "is_slim": "slim" in tag,
        "is_distroless": "distroless" in image,
    }
