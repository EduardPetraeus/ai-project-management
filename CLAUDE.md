# CLAUDE.md -- ai-project-management

This file governs all AI agent sessions in this repository.

## project_context

- **Repo:** ai-project-management
- **Purpose:** YAML-based task engine for agentic software development
- **License:** MIT
- **Status:** v1.0.0 (stable)
- **PyPI:** `pip install ai-pm`
- **Design principle:** One YAML file per task -- enables parallel agent work with zero merge conflicts

## conventions

- All content in English -- no exceptions
- File names: `kebab-case.md` for docs, `UPPER-CASE.yaml` for templates
- Task IDs: `TASK-001` format (zero-padded, sequential)
- Sprint IDs: `S001` format
- YAML files must validate against schemas in `src/ai_pm/schemas/`
- Cross-references use relative links

## architecture

```
src/ai_pm/          -> Python package (CLI + engine + validator)
  schemas/           -> JSON Schema for validation (bundled)
  templates/         -> YAML templates (bundled, copied by `ai-pm init`)
  commands/          -> Claude Code slash commands (bundled)
examples/            -> Reference implementations (solo-developer, multi-team)
docs/                -> Integration guide
tests/               -> Test suite (122 tests)
```

## session_protocol

1. Read this CLAUDE.md
2. Confirm scope: which templates, commands, or docs to work on
3. After changes: verify YAML validates against schemas
4. Verify all cross-references resolve
5. Run `pytest` to confirm all tests pass

## quality_standards

- Every YAML template must be valid YAML and validate against its schema
- Every template must work as-is without modification (sensible defaults)
- Commands must be self-contained and portable across projects
- Examples must be complete and runnable
- `ai-pm validate examples/` must pass
