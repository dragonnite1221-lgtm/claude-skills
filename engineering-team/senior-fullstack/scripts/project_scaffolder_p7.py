# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from project_scaffolder_p1 import TEMPLATES  # noqa: E402,E501
from project_scaffolder_p2 import _mod_cg0_0  # noqa: E402,E501
from project_scaffolder_p3 import _mod_cg0_1  # noqa: E402,E501
from project_scaffolder_p4 import _mod_cg0_2  # noqa: E402,E501
from project_scaffolder_p5 import _mod_cg0_3  # noqa: E402,E501
from project_scaffolder_p6 import _mod_cg0_4  # noqa: E402,E501
# fmt: on


def get_file_content(template: str, filepath: str, project_name: str) -> str:
    """Generate file content based on template and file type."""
    filename = Path(filepath).name

    contents = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2(), **_mod_cg0_3(), **_mod_cg0_4()}

    # Handle special cases
    if "routes" in filepath and filename == "index.ts":
        return '''import { Router } from "express";
import usersRouter from "./users";

const router = Router();
router.use("/users", usersRouter);
export default router;
'''

    if "schemas" in filepath and filename == "user.py":
        return '''from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
'''

    if "users" in filepath and filename == "urls.py":
        return '''from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet)
urlpatterns = [path("", include(router.urls))]
'''

    return contents.get(filename, f"// {filename}\n")
def get_next_steps(template: str, name: str) -> List[str]:
    """Get setup instructions for template."""
    steps = {
        "nextjs": [f"cd {name}", "npm install", "cp .env.example .env.local", "npm run dev"],
        "fastapi-react": [
            f"cd {name}",
            "docker-compose up -d db",
            "cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload",
            "cd frontend && npm install && npm run dev"
        ],
        "mern": [
            f"cd {name}",
            "docker-compose up -d mongo",
            "cd server && npm install && npm run dev",
            "cd client && npm install && npm run dev"
        ],
        "django-react": [
            f"cd {name}",
            "docker-compose up -d db",
            "cd backend && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver",
            "cd frontend && npm install && npm run dev"
        ]
    }
    return steps.get(template, [f"cd {name}"])
def create_project(template_name: str, project_name: str, output_dir: Path) -> Dict:
    """Create project from template."""
    if template_name not in TEMPLATES:
        return {
            "success": False,
            "error": f"Unknown template: {template_name}",
            "available": list(TEMPLATES.keys())
        }

    template = TEMPLATES[template_name]
    project_dir = output_dir / project_name

    if project_dir.exists():
        return {"success": False, "error": f"Directory exists: {project_dir}"}

    created_files = []
    created_dirs = []

    for dir_path, files in template["structure"].items():
        if dir_path:
            full_dir = project_dir / dir_path
        else:
            full_dir = project_dir

        full_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(full_dir))

        for filename in files:
            filepath = full_dir / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            content = get_file_content(template_name, str(dir_path / filename), project_name)
            filepath.write_text(content)
            created_files.append(str(filepath))

    return {
        "success": True,
        "project_name": project_name,
        "template": template_name,
        "description": template["description"],
        "location": str(project_dir),
        "files_created": len(created_files),
        "directories_created": len(created_dirs),
        "next_steps": get_next_steps(template_name, project_name)
    }
def list_templates() -> Dict:
    """List available templates."""
    return {
        "templates": [
            {"name": k, "display_name": v["name"], "description": v["description"]}
            for k, v in TEMPLATES.items()
        ]
    }
