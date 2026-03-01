"""Schema-based validation using jsonschema with rich error output."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from rich.console import Console
from rich.panel import Panel

from ai_pm.parser import ParseError, load_yaml_file

console = Console()

# Default schemas directory (relative to package)
SCHEMAS_DIR = Path(__file__).resolve().parent.parent.parent / "schemas"

# Mapping from schema file stem to identifying characteristics
_SCHEMA_DETECTORS: list[tuple[str, callable]] = []


def _detect_task(data: dict, path: Path) -> bool:
    """Detect task YAML files."""
    return path.stem.startswith("TASK-") or (
        "id" in data and isinstance(data.get("id", ""), str) and data["id"].startswith("TASK-")
    )


def _detect_sprint(data: dict, path: Path) -> bool:
    """Detect sprint YAML files."""
    return (
        "id" in data
        and isinstance(data.get("id", ""), str)
        and data["id"].startswith("S")
        and "tasks" in data
        and "goal" in data
    )


def _detect_roadmap(data: dict, path: Path) -> bool:
    """Detect roadmap YAML files."""
    return "milestones" in data and "project" in data


def _detect_roles(data: dict, path: Path) -> bool:
    """Detect roles YAML files."""
    has_roles = "roles" in data and isinstance(data.get("roles"), dict)
    return has_roles and "milestones" not in data and "profiles" not in data


def _detect_trust_profile(data: dict, path: Path) -> bool:
    """Detect trust profile YAML files."""
    return "profiles" in data and isinstance(data.get("profiles"), dict)


def _detect_metrics(data: dict, path: Path) -> bool:
    """Detect metrics YAML files."""
    return "agent_performance" in data or ("cost" in data and "quality" in data)


# Register detectors in priority order (most specific first)
_SCHEMA_DETECTORS = [
    ("task-schema", _detect_task),
    ("sprint-schema", _detect_sprint),
    ("trust-profile-schema", _detect_trust_profile),
    ("metrics-schema", _detect_metrics),
    ("roadmap-schema", _detect_roadmap),
    ("roles-schema", _detect_roles),
]


def find_schema_for_file(data: dict, path: Path, schemas_dir: Path | None = None) -> Path | None:
    """Determine which JSON schema matches a YAML file.

    Args:
        data: Parsed YAML data.
        path: Path to the YAML file (used for naming hints).
        schemas_dir: Directory containing JSON schema files.

    Returns:
        Path to the matching schema, or None if no match found.
    """
    schemas_dir = schemas_dir or SCHEMAS_DIR

    for schema_stem, detector in _SCHEMA_DETECTORS:
        if detector(data, path):
            schema_path = schemas_dir / f"{schema_stem}.json"
            if schema_path.exists():
                return schema_path

    return None


def load_schema(schema_path: Path) -> dict:
    """Load a JSON schema file.

    Args:
        schema_path: Path to the JSON schema.

    Returns:
        Parsed schema dictionary.
    """
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_yaml_against_schema(
    data: dict,
    schema_path: Path,
) -> list[str]:
    """Validate YAML data against a JSON schema.

    Args:
        data: Parsed YAML data.
        schema_path: Path to the JSON schema.

    Returns:
        List of validation error messages (empty if valid).
    """
    schema = load_schema(schema_path)
    validator_cls = jsonschema.Draft202012Validator
    validator = validator_cls(schema)

    errors = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        field_path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"{field_path}: {error.message}")

    return errors


def validate_file(
    path: Path,
    schemas_dir: Path | None = None,
    quiet: bool = False,
) -> tuple[bool, list[str]]:
    """Validate a single YAML file against its matching schema.

    Args:
        path: Path to the YAML file.
        schemas_dir: Directory containing JSON schemas.
        quiet: If True, suppress rich console output.

    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    schemas_dir = schemas_dir or SCHEMAS_DIR

    try:
        data = load_yaml_file(path)
    except ParseError as e:
        errors = [str(e)]
        if not quiet:
            console.print(Panel(f"[red]PARSE ERROR[/red]: {e}", title=str(path)))
        return False, errors

    schema_path = find_schema_for_file(data, path, schemas_dir)

    if schema_path is None:
        if not quiet:
            console.print(f"  [yellow]SKIP[/yellow] {path} (no matching schema)")
        return True, []

    errors = validate_yaml_against_schema(data, schema_path)

    if not quiet:
        if errors:
            error_text = "\n".join(f"  - {e}" for e in errors)
            console.print(Panel(f"[red]FAIL[/red] ({schema_path.stem})\n{error_text}", title=str(path)))
        else:
            console.print(f"  [green]PASS[/green] {path} ({schema_path.stem})")

    return len(errors) == 0, errors
