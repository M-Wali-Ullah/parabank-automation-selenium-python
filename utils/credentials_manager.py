"""
Simple credentials persistence helper.

Stores a small JSON file at config/temp_credentials.json with structure:
{
  "username": "...",
  "password": "...",
  "full_data": { ... }  # optional
}

This is intentionally minimal and local-only for test automation reuse.
"""
from pathlib import Path
import json
from typing import Optional, Dict, Any

from config.config import Config


def _credentials_path() -> Path:
    # place the file under the project's config folder
    return Config.BASE_DIR / "config" / "temp_credentials.json"


def save_credentials(creds: Dict[str, Any]) -> None:
    path = _credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(creds, fh, indent=2)


def read_credentials() -> Optional[Dict[str, Any]]:
    path = _credentials_path()
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def delete_credentials() -> None:
    path = _credentials_path()
    try:
        if path.exists():
            path.unlink()
    except Exception:
        # best-effort delete
        pass
