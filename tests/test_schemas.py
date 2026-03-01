"""Validate all example YAML files against their schemas."""

from ai_pm.parser import discover_yaml_files, load_yaml_file
from ai_pm.validator import find_schema_for_file, validate_yaml_against_schema


class TestExampleValidation:
    """Validate all example YAMLs against their schemas."""

    def test_solo_developer_examples(self, examples_dir, schemas_dir):
        solo = examples_dir / "solo-developer"
        yaml_files = discover_yaml_files(solo)
        assert len(yaml_files) > 0, "Expected example YAML files in solo-developer/"

        for yaml_path in yaml_files:
            data = load_yaml_file(yaml_path)
            schema_path = find_schema_for_file(data, yaml_path, schemas_dir)
            if schema_path is not None:
                errors = validate_yaml_against_schema(data, schema_path)
                assert errors == [], f"{yaml_path} failed validation against {schema_path.stem}: {errors}"

    def test_multi_team_examples(self, examples_dir, schemas_dir):
        multi = examples_dir / "multi-team"
        yaml_files = discover_yaml_files(multi)
        assert len(yaml_files) > 0, "Expected example YAML files in multi-team/"

        for yaml_path in yaml_files:
            data = load_yaml_file(yaml_path)
            schema_path = find_schema_for_file(data, yaml_path, schemas_dir)
            if schema_path is not None:
                errors = validate_yaml_against_schema(data, schema_path)
                assert errors == [], f"{yaml_path} failed validation against {schema_path.stem}: {errors}"


class TestTemplateValidation:
    """Validate template YAML files against their schemas."""

    def test_task_template(self, templates_dir, schemas_dir):
        path = templates_dir / "backlog" / "TASK-TEMPLATE.yaml"
        data = load_yaml_file(path)
        schema_path = schemas_dir / "task-schema.json"
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == [], f"TASK-TEMPLATE.yaml: {errors}"

    def test_sprint_template(self, templates_dir, schemas_dir):
        path = templates_dir / "sprints" / "SPRINT-TEMPLATE.yaml"
        data = load_yaml_file(path)
        schema_path = schemas_dir / "sprint-schema.json"
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == [], f"SPRINT-TEMPLATE.yaml: {errors}"

    def test_roadmap_template(self, templates_dir, schemas_dir):
        path = templates_dir / "ROADMAP.yaml"
        data = load_yaml_file(path)
        schema_path = schemas_dir / "roadmap-schema.json"
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == [], f"ROADMAP.yaml: {errors}"

    def test_roles_template(self, templates_dir, schemas_dir):
        path = templates_dir / "ROLES.yaml"
        data = load_yaml_file(path)
        schema_path = schemas_dir / "roles-schema.json"
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == [], f"ROLES.yaml: {errors}"

    def test_trust_profile_template(self, templates_dir, schemas_dir):
        path = templates_dir / "TRUST_PROFILE.yaml"
        data = load_yaml_file(path)
        schema_path = schemas_dir / "trust-profile-schema.json"
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == [], f"TRUST_PROFILE.yaml: {errors}"

    def test_metrics_template(self, templates_dir, schemas_dir):
        path = templates_dir / "METRICS.yaml"
        data = load_yaml_file(path)
        schema_path = schemas_dir / "metrics-schema.json"
        errors = validate_yaml_against_schema(data, schema_path)
        assert errors == [], f"METRICS.yaml: {errors}"
