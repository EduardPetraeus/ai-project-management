# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | Yes                |
| < 1.0   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, use GitHub's private vulnerability reporting feature:
1. Go to the repository's Security tab.
2. Click "Report a vulnerability."
3. Provide a description, steps to reproduce, and potential impact.

## What to Expect

- **Acknowledgment:** Within 48 hours of your report.
- **Assessment:** We will assess the severity and impact within 7 days.
- **Fix:** Critical vulnerabilities will be patched within 14 days.
- **Disclosure:** We will coordinate disclosure timing with you.

## Scope

This policy covers:
- The `ai-pm` Python package (source code in `src/`).
- JSON schemas in `schemas/`.
- CLI commands and their behavior.
- YAML template handling and parsing.

Out of scope:
- Third-party dependencies (report these to the respective maintainers).
- Example files (these contain no sensitive data by design).

## Best Practices

When using this tool in your projects:
- Do not store secrets, credentials, or API keys in task YAML files.
- Use `.gitignore` to exclude any local configuration with sensitive data.
- Review task YAML files before committing to public repositories.
