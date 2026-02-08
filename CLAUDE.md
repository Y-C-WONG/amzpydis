# CLAUDE.md - AI Assistant Guide for amzpydis

## Project Overview

**amzpydis** is a newly initialized repository currently in the pre-development phase. No source code, build tooling, or test infrastructure has been set up yet.

## Repository Structure

```
amzpydis/
├── CLAUDE.md          # This file - AI assistant guide
└── README.md          # Project readme (placeholder)
```

## Current State

- **Language:** Not yet determined
- **Build system:** Not configured
- **Package manager:** Not configured
- **Test framework:** Not configured
- **Linting/formatting:** Not configured
- **CI/CD:** Not configured

## Development Workflow

No build, test, or lint commands are available yet. This section should be updated as tooling is added.

<!-- Example structure to fill in as the project develops:
### Build
```sh
# <build command here>
```

### Test
```sh
# <test command here>
```

### Lint / Format
```sh
# <lint command here>
```

### Run
```sh
# <run command here>
```
-->

## Conventions for AI Assistants

### General Principles

- Read existing code before proposing changes. Never modify files you haven't read.
- Keep changes minimal and focused on the request. Avoid unnecessary refactoring.
- Do not add features, abstractions, or error handling beyond what is asked for.
- Prefer editing existing files over creating new ones.
- Do not introduce security vulnerabilities (injection, XSS, etc.).

### Git Practices

- Write clear, concise commit messages that describe the "why" not just the "what."
- Only commit when explicitly asked.
- Never force-push to main/master.
- Stage specific files rather than using `git add -A`.
- Never commit secrets, credentials, or `.env` files.

### Code Style

No project-specific style guidelines have been established yet. When code is added, follow the conventions already present in the codebase (indentation, naming, imports, etc.). Update this section as patterns emerge.

### Documentation

- Update this CLAUDE.md file as the project evolves (new tooling, commands, conventions).
- Keep README.md current with setup instructions and project description.

## Dependencies

No dependencies have been declared yet. Update this section when a package manager and dependency file are introduced.

## Architecture

No architecture decisions have been made yet. Document key design decisions, module boundaries, and data flow here as the project takes shape.
