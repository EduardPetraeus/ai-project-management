# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-03-07

### Added
- `ai-pm init` command to bootstrap projects with templates and commands
- Schemas, templates, and commands bundled inside the package (works with `pip install`)
- `pick-next` and `critical-path` CLI commands
- Full PyPI metadata (classifiers, keywords, URLs)
- GitHub issue and PR templates
- Trusted Publishing workflow for PyPI releases
- 122 tests with comprehensive coverage

### Changed
- Schemas moved from repo root to `src/ai_pm/schemas/` (bundled in wheel)
- Templates moved from repo root to `src/ai_pm/templates/` (bundled in wheel)
- Commands moved from repo root to `src/ai_pm/commands/` (bundled in wheel)
- README rewritten for open-source audience
- Example tasks replaced with generic scenarios
- INTEGRATION.md updated to reference `ai-pm init`

### Fixed
- Schema path resolution now works in non-editable installs

## [0.1.0] - 2026-03-01

### Added
- Python CLI with validate, task list, task create, task complete, lint, sprint status
- Task engine with state machine, dependency resolution, and critical path calculation
- JSON schemas for all YAML template types (task, sprint, roadmap, roles, trust-profile, metrics)
- YAML validator with rich error reporting
- CI/CD pipeline with linting, testing, and schema validation
- Open source files: CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md

## [0.1.0] - 2026-03-01

### Added
- Initial scaffolding with YAML templates, schemas, and commands
- Solo-developer and multi-team examples
