"""Compatibility launcher for `streamlit run streamlit_app.py`.

The application now lives in the ``frontend`` package; the canonical entry
point is ``frontend/app.py``. This shim keeps older commands working.
"""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent / "frontend" / "app.py"),
    run_name="__main__",
)
