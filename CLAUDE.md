# CLAUDE.md — ai-project-management

This file governs all AI agent sessions in this repository.

## project_context

- **Repo:** ai-project-management
- **Purpose:** YAML-based task engine for agentic software development
- **License:** MIT
- **Status:** Active development (v0.1.0)
- **Design principle:** One YAML file per task — enables parallel agent work with zero merge conflicts

## conventions

- All content in English — no exceptions
- File names: `kebab-case.md` for docs, `UPPER-CASE.yaml` for templates
- Task IDs: `TASK-001` format (zero-padded, sequential)
- Sprint IDs: `S001` format
- YAML files must validate against schemas in `schemas/`
- Cross-references use relative links

## architecture

This repo provides **templates** that projects instantiate. It does not contain project-specific tasks.

```
templates/     → YAML templates copied into project repos
schemas/       → JSON Schema for validation
commands/      → Claude Code slash commands for task management
examples/      → Reference implementations (solo-developer, multi-team)
docs/          → Philosophy and integration guides
```

## session_protocol

1. Read this CLAUDE.md
2. Confirm scope: which templates, commands, or docs to work on
3. After changes: verify YAML validates against schemas
4. Verify all cross-references resolve

## quality_standards

- Every YAML template must be valid YAML and validate against its schema
- Every template must work as-is without modification (sensible defaults)
- Commands must be self-contained and portable across projects
- Examples must be complete and runnable

## framework_references

- Governance: ~/Github repos/ai-governance-framework
- Engineering Standards: ~/Github repos/ai-engineering-standards
- Umbrella: ~/Github repos/agentic-engineering
