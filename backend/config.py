"""Configuration settings for the AI Math Tutor application."""

import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "data" / "math_tutor.db"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
Path(BASE_DIR / "data").mkdir(exist_ok=True)

# MiMo API Configuration
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")

# Default model: use flash for fast response, pro for deep reasoning
MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-v2-flash")
MIMO_REASONING_MODEL = os.getenv("MIMO_REASONING_MODEL", "mimo-v2-pro")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
