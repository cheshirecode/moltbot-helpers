"""Seek configuration loader."""

import json
import os

DEFAULT_CONFIG_PATH = "~/.config/seek/config.json"

DEFAULT_CONFIG = {
    "paths": [],
    "sqliteSources": [],
    "model": "all-MiniLM-L6-v2",
    "dbPath": "~/.local/share/seek/seek.db",
    "chunkSize": 256,
    "chunkOverlap": 32,
}


def load_config():
    path = os.path.expanduser(os.environ.get("SEEK_CONFIG", DEFAULT_CONFIG_PATH))
    if os.path.exists(path):
        with open(path) as f:
            cfg = json.load(f)
        # Merge with defaults
        merged = {**DEFAULT_CONFIG, **cfg}
        return merged
    return dict(DEFAULT_CONFIG)


def expand(path):
    """Expand ~ and env vars in a path."""
    return os.path.expanduser(os.path.expandvars(path))
