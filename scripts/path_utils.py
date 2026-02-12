from pathlib import Path
import sys


def _runtime_root() -> Path:
    """Return the effective runtime root for both source and PyInstaller builds."""
    # In a PyInstaller onefile build, resources are extracted under sys._MEIPASS.
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    # In source mode, treat project root as the base (scripts/..).
    return Path(__file__).resolve().parent.parent


def asset_path(relative_path: str) -> str:
    """Resolve an asset path against the active runtime root."""
    return str(_runtime_root() / relative_path)
