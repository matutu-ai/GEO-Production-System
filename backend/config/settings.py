"""Central configuration for GEO Production System."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = PROJECT_ROOT
load_dotenv(PROJECT_ROOT / ".env")

APP_NAME = os.getenv("APP_NAME", "GEO Production System")
APP_ENV = os.getenv("APP_ENV", "local")
VERSION = os.getenv("APP_VERSION", "2.2.0")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "mock")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MODEL_NAME = os.getenv("MODEL_NAME", OPENAI_MODEL)
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "json")
STORAGE_PATH = Path(os.getenv("STORAGE_PATH", str(PROJECT_ROOT / "storage")))
UPLOAD_DIR = STORAGE_PATH / "uploads"
PROJECTS_DIR = STORAGE_PATH / "projects"
PROJECTS_FILE = Path(os.getenv("PROJECTS_FILE", str(PROJECTS_DIR / "projects.json")))
USERS_FILE = Path(os.getenv("USERS_FILE", str(STORAGE_PATH / "users" / "users.json")))
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", str(STORAGE_PATH / "reports")))
TASK_OUTPUT_DIR = Path(os.getenv("TASK_OUTPUT_DIR", str(REPORTS_DIR)))

JWT_SECRET = os.getenv("JWT_SECRET", "geo-production-system-local-secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
