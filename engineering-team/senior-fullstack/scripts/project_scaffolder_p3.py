# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_scaffolder_base import *  # noqa: F403,E402


def _mod_cg0_1():
    return {
        "utils.ts": '''export function cn(...classes: (string | undefined | false)[]): string {
  return classes.filter(Boolean).join(" ");
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric", month: "long", day: "numeric",
  }).format(date);
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
''',
        "db.ts": '''// Database connection (Prisma example)
// import { PrismaClient } from "@prisma/client";
// export const db = new PrismaClient();

export const db = {
  // Placeholder - configure your database
};
''',
        "index.ts": '''export interface User {
  id: string;
  email: string;
  name: string | null;
  createdAt: Date;
}

export interface ApiResponse<T> {
  data: T;
  error: string | null;
  success: boolean;
}
''',
        "main.py": f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings

app = FastAPI(title="{project_name}", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}
''',
        "config.py": '''from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/db"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    SECRET_KEY: str = "change-me-in-production"  # ⚠️ SCAFFOLDING PLACEHOLDER — replace before deployment

    class Config:
        env_file = ".env"

settings = Settings()
''',
        "database.py": '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
        "routes.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return {"users": []}

@router.post("/users")
async def create_user(db: Session = Depends(get_db)):
    return {"message": "User created"}
''',
        "deps.py": '''from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

def get_current_user():
    # Implement authentication
    pass
''',
        "user.py": '''from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
''',
    }
