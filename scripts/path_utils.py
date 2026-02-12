from pathlib import Path
import sys


def _runtime_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def asset_path(relative_path: str) -> str:
    return str(_runtime_root() / relative_path)
