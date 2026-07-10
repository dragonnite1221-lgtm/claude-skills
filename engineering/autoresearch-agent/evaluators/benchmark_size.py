#!/usr/bin/env python3
"""Measure file, bundle, or Docker image size.
DO NOT MODIFY after experiment starts — this is the fixed evaluator."""

import os
import subprocess
import sys

# --- CONFIGURE ONE OF THESE ---
# Option 1: File size
TARGET_FILE = "dist/main.js"

# Option 2: Directory size (uncomment to use)
# TARGET_DIR = "dist/"

# Option 3: Docker image (uncomment to use)
# DOCKER_IMAGE = "myapp:latest"
# DOCKER_BUILD_CMD = "docker build -t myapp:latest ."

# Option 4: Build first, then measure (uncomment to use)
# BUILD_CMD = "npm run build"
# --- END CONFIG ---

build_cmd = globals().get("BUILD_CMD")
docker_build_cmd = globals().get("DOCKER_BUILD_CMD")
docker_image = globals().get("DOCKER_IMAGE")
target_dir = globals().get("TARGET_DIR")

# Build if needed
if build_cmd:
    result = subprocess.run(build_cmd, shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"Build failed: {result.stderr.decode()[:200]}", file=sys.stderr)
        sys.exit(1)

# Measure
if docker_image:
    if docker_build_cmd:
        subprocess.run(docker_build_cmd, shell=True, capture_output=True)
    result = subprocess.run(
        f"docker image inspect {docker_image} --format '{{{{.Size}}}}'",
        shell=True, capture_output=True, text=True
    )
    try:
        size_bytes = int(result.stdout.strip())
    except ValueError:
        print(f"Could not parse size from: {result.stdout[:100]}", file=sys.stderr)
        sys.exit(1)
elif target_dir:
    size_bytes = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, fns in os.walk(target_dir) for f in fns
    )
elif os.path.exists(TARGET_FILE):
    size_bytes = os.path.getsize(TARGET_FILE)
else:
    print(f"Target not found: {TARGET_FILE}", file=sys.stderr)
    sys.exit(1)

size_kb = size_bytes / 1024
size_mb = size_bytes / (1024 * 1024)

print(f"size_bytes: {size_bytes}")
print(f"size_kb: {size_kb:.1f}")
print(f"size_mb: {size_mb:.2f}")
