"""Tests for schema validation."""

from pathlib import Path

from ai_pm.validator import (
    find_schema_for_file,
    load_schema,
    validate_file,
    validate_yaml_against_schema,
)


class TestFindSchemaForFile:
    """Test automatic schema detection."""

    def test_detect_task(self, schemas_dir):
        data = {"id": "TASK-001", "title": "Test", "status": "ready"}
        path = Path("backlog/TASK-001.yaml")
        schema = find_schema_for_file(data, path, schemas_dir)
        assert schema is not None
        assert schema.stem == "task-schema"

    def test_detect_sprint(self, schemas_dir):
        data = {"id": "S001", "title": "Sprint 1", "goal": "Ship v1", "tasks": ["TASK-001"]}
        path = Path("sprints/S001.yaml")
        schema = find_schema_for_file(data, path, schemas_dir)
        assert schema is not None
        assert schema.stem == "sprint-schema"

    def test_detect_roadmap(self, schemas_dir):
        data = {"project": "Test", "milestones": [], "updated": "2026-01-01"}
        path = Path("ROADMAP.yaml")
        schema = find_schema_for_file(data, path, schemas_dir)
        assert schema is not None
        assert schema.stem == "roadmap-schema"

    def test_detect_roles(self, schemas_dir):
        data = {"roles": {"code": {"description": "Writes code", "handles": ["backend"]}}}
        path = Path("ROLES.yaml")
        schema = find_schema_for_file(data, path, schemas_dir)
        assert schema is not None
        assert schema.stem == "roles-schema"

    def test_detect_trust_profile(self, schemas_dir):
        data = {"profiles": {"elevated": {"description": "Low risk", "applies_to": ["docs"], "permissions": {}}}}
        path = Path("TRUST_PROFILE.yaml")
        schema = find_schema_for_file(data, path, schemas_dir)
        assert schema is not None
        assert schema.stem == "trust-profile-schema"

    def test_detect_metrics(self, schemas_dir):
        data = {"project": "Test", "updated": "2026-01-01", "agent_performance": {}, "cost": {}, "quality": {}}
        path = Path("METRICS.yaml")
        schema = find_schema_for_file(data, path, schemas_dir)
        assert schema is not None
        assert schema.stem == "metrics-schema"

    def test_no_match(self, schemas_dir):
        data = {"random_key": "value"}
        path = Path("unknown.yaml")
        schema = find_schema_for_file(data, path, schemas_dir)
        assert schema is None


class TestValidateYamlAgainstSchema:
    """Test schema validation with specific data."""

    def test_valid_task(self, schemas_dir):
        schema_path = schemas_dir / "task-schema.json"
        data = {
            "id": "TASK-001",
            "title": "A valid task title here",
            "status": "ready",
            "priority": "high",
            "agent": "code",
            "review": "agent-review",
            "created": "2026-01-01",
        }
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == []

    def test_invalid_task_missing_required(self, schemas_dir):
        schema_path = schemas_dir / "task-schema.json"
        data = {"id": "TASK-001"}
        errors = validate_yaml_against_schema(data, schema_path)
        assert len(errors) > 0

    def test_invalid_task_bad_status(self, schemas_dir):
        schema_path = schemas_dir / "task-schema.json"
        data = {
            "id": "TASK-001",
            "title": "Valid title here",
            "status": "invalid_status",
            "priority": "high",
            "agent": "code",
            "review": "agent-review",
            "created": "2026-01-01",
        }
        errors = validate_yaml_against_schema(data, schema_path)
        assert any("status" in e for e in errors)

    def test_invalid_task_id_pattern(self, schemas_dir):
        schema_path = schemas_dir / "task-schema.json"
        data = {
            "id": "BAD-FORMAT",
            "title": "Valid title here",
            "status": "ready",
            "priority": "high",
            "agent": "code",
            "review": "agent-review",
            "created": "2026-01-01",
        }
        errors = validate_yaml_against_schema(data, schema_path)
        assert any("id" in e for e in errors)

    def test_valid_sprint(self, schemas_dir):
        schema_path = schemas_dir / "sprint-schema.json"
        data = {
            "id": "S001",
            "title": "First sprint goal",
            "status": "planning",
            "start_date": "2026-01-01",
            "end_date": "2026-01-14",
            "goal": "Deliver the first increment of the product",
            "tasks": ["TASK-001", "TASK-002"],
        }
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == []

    def test_invalid_sprint_bad_status(self, schemas_dir):
        schema_path = schemas_dir / "sprint-schema.json"
        data = {
            "id": "S001",
            "title": "First sprint goal",
            "status": "invalid",
            "start_date": "2026-01-01",
            "end_date": "2026-01-14",
            "goal": "Deliver the first increment of the product",
            "tasks": [],
        }
        errors = validate_yaml_against_schema(data, schema_path)
        assert len(errors) > 0

    def test_valid_roadmap(self, schemas_dir):
        schema_path = schemas_dir / "roadmap-schema.json"
        data = {
            "project": "Test Project",
            "updated": "2026-01-01",
            "milestones": [
                {
                    "id": "M001",
                    "title": "First milestone title",
                    "target_date": "2026-02-01",
                    "status": "planned",
                    "description": "What this milestone delivers",
                    "success_criteria": ["Criterion 1"],
                }
            ],
        }
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == []

    def test_valid_roles(self, schemas_dir):
        schema_path = schemas_dir / "roles-schema.json"
        data = {
            "roles": {
                "code": {
                    "description": "Writes code",
                    "handles": ["backend"],
                    "trust_level": "standard",
                    "review_default": "agent-review",
                }
            },
            "solo_mode": {"enabled": True, "description": "Solo mode"},
        }
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == []


class TestValidateFile:
    """Test file-level validation."""

    def test_validate_valid_file(self, tmp_path, schemas_dir):
        f = tmp_path / "TASK-001.yaml"
        f.write_text(
            "id: TASK-001\ntitle: A valid task title here\nstatus: ready\n"
            "priority: high\nagent: code\nreview: agent-review\ncreated: '2026-01-01'\n"
        )
        is_valid, errors = validate_file(f, schemas_dir, quiet=True)
        assert is_valid
        assert errors == []

    def test_validate_invalid_file(self, tmp_path, schemas_dir):
        f = tmp_path / "TASK-001.yaml"
        f.write_text("id: BAD\ntitle: Short\n")
        is_valid, errors = validate_file(f, schemas_dir, quiet=True)
        assert not is_valid
        assert len(errors) > 0

    def test_validate_unparseable_file(self, tmp_path, schemas_dir):
        f = tmp_path / "broken.yaml"
        f.write_text("")
        is_valid, errors = validate_file(f, schemas_dir, quiet=True)
        assert not is_valid

    def test_validate_no_matching_schema(self, tmp_path, schemas_dir):
        f = tmp_path / "random.yaml"
        f.write_text("unknown_key: value\n")
        is_valid, errors = validate_file(f, schemas_dir, quiet=True)
        # No schema means skip — treated as valid
        assert is_valid


class TestLoadSchema:
    """Test schema loading."""

    def test_load_existing_schema(self, schemas_dir):
        schema = load_schema(schemas_dir / "task-schema.json")
        assert schema["title"] == "Task"
        assert "properties" in schema

    def test_load_all_schemas(self, schemas_dir):
        for schema_file in schemas_dir.glob("*.json"):
            schema = load_schema(schema_file)
            assert "$schema" in schema
