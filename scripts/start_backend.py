import os
import subprocess
import sys

from backend.app.database.database import Base, engine
from backend.app.database.models import DocumentAnalysis


Base.metadata.create_all(bind=engine)

subprocess.run(
    [sys.executable, "scripts/seed_demo.py"],
    check=True,
)

port = os.getenv("PORT", "8000")

subprocess.run(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        port,
    ],
    check=True,
)