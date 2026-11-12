"""Start the building-gen web app on http://127.0.0.1:8228 (local only).

Run: python run_web.py   (needs requirements-web.txt)
"""
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

if __name__ == "__main__":
    uvicorn.run("buildgen.web.app:app", host="127.0.0.1", port=8228)
