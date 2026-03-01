"""YAML loading with error handling and file discovery."""

from __future__ import annotations

import datetime
from pathlib import Path

import yaml


def _convert_dates(obj):
    """Recursively convert datetime.date objects to ISO format strings."""
    if isinstance(obj, dict):
        return {k: _convert_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_dates(item) for item in obj]
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return obj


class ParseError(Exception):
    """Raised when a YAML file cannot be parsed."""

    def __init__(self, path: Path, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"{path}: {reason}")


def load_yaml_file(path: Path) -> dict:
    """Load and parse a single YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        ParseError: If the file cannot be read or parsed.
    """
    if not path.exists():
        raise ParseError(path, "File does not exist")

    if not path.is_file():
        raise ParseError(path, "Path is not a file")

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ParseError(path, f"Cannot read file: {e}") from e

    if not text.strip():
        raise ParseError(path, "File is empty")

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ParseError(path, f"Invalid YAML: {e}") from e

    if not isinstance(data, dict):
        raise ParseError(path, f"Expected a YAML mapping, got {type(data).__name__}")

    return _convert_dates(data)


def discover_yaml_files(directory: Path, recursive: bool = True) -> list[Path]:
    """Find all YAML files in a directory.

    Args:
        directory: Root directory to search.
        recursive: Whether to search subdirectories.

    Returns:
        Sorted list of YAML file paths.
    """
    if not directory.exists():
        return []

    if not directory.is_dir():
        # Single file passed
        if directory.suffix in (".yaml", ".yml"):
            return [directory]
        return []

    pattern = "**/*.yaml" if recursive else "*.yaml"
    yaml_files = list(directory.glob(pattern))

    # Also match .yml extension
    yml_pattern = "**/*.yml" if recursive else "*.yml"
    yaml_files.extend(directory.glob(yml_pattern))

    return sorted(set(yaml_files))


def load_all_tasks(backlog_dir: Path) -> list[dict]:
    """Load all task YAML files from a backlog directory.

    Args:
        backlog_dir: Path to the backlog/ directory.

    Returns:
        List of parsed task dictionaries, sorted by ID.
    """
    tasks = []
    for yaml_path in discover_yaml_files(backlog_dir, recursive=False):
        if yaml_path.stem.startswith("TASK-"):
            try:
                data = load_yaml_file(yaml_path)
                data["_source_path"] = str(yaml_path)
                tasks.append(data)
            except ParseError:
                continue

    return sorted(tasks, key=lambda t: t.get("id", ""))


def find_backlog_dir(start_path: Path) -> Path | None:
    """Search for a backlog/ directory starting from the given path.

    Looks in the given path, then walks up to 3 parent levels.
    """
    candidates = [
        start_path / "backlog",
        start_path,
    ]

    # Walk up parents
    current = start_path
    for _ in range(3):
        current = current.parent
        candidates.append(current / "backlog")

    for candidate in candidates:
        if candidate.is_dir() and any(candidate.glob("TASK-*.yaml")):
            return candidate

    return None
