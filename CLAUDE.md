# CLAUDE.md - AI Assistant Guide for amzpydis

## Project Overview

**amzpydis** is a Python web scraper that monitors [Amazon UK warehouse jobs](https://www.jobsatamazon.co.uk/app#/jobSearch) for openings in specific areas and sends notifications to a Discord channel via webhook.

## Repository Structure

```
amzpydis/
├── src/
│   ├── __init__.py           # Package marker
│   ├── config.py             # Configuration from environment variables
│   ├── scraper.py            # Playwright-based scraper + Job dataclass
│   ├── discord_notifier.py   # Discord webhook integration
│   └── main.py               # Entrypoint with scheduling loop
├── .env.example              # Template for environment variables
├── .gitignore
├── .dockerignore
├── Dockerfile                # Container image for VPS deployment
├── docker-compose.yml        # Single-command deployment
├── requirements.txt          # Python dependencies
├── CLAUDE.md                 # This file
└── README.md                 # User-facing documentation
```

## Current State

- **Language:** Python 3.11+
- **Key library:** Playwright (Chromium, sync API)
- **Package manager:** pip / requirements.txt
- **Test framework:** Not yet configured
- **Linting/formatting:** Not yet configured
- **CI/CD:** Not configured — designed for Docker deployment on a VPS

## Development Workflow

### Install dependencies
```sh
pip install -r requirements.txt
playwright install chromium
```

### Run locally
```sh
cp .env.example .env   # then edit .env with your values
python -m src.main
```

### Run with Docker
```sh
cp .env.example .env   # then edit .env
docker compose up -d --build
```

### View logs (Docker)
```sh
docker compose logs -f scraper
```

## Key Modules

| Module | Purpose |
|---|---|
| `src/config.py` | Reads `.env` via `python-dotenv`. All tunables live here. |
| `src/scraper.py` | Launches headless Chromium, navigates to the SPA, extracts job cards. Supports proxy. Contains `Job` dataclass and `scrape_jobs()`. |
| `src/discord_notifier.py` | Formats job listings as Discord embeds and POSTs them to a webhook URL. |
| `src/main.py` | Entrypoint. Runs `scrape_jobs` → `send_job_alert` in a loop on `CHECK_INTERVAL`. Tracks seen jobs to avoid duplicate alerts. Handles SIGINT/SIGTERM. |

## Configuration (environment variables)

| Variable | Default | Description |
|---|---|---|
| `DISCORD_WEBHOOK_URL` | *(empty)* | Discord webhook for notifications |
| `PROXY_URL` | *(empty)* | Optional HTTP proxy (`http://user:pass@host:port`) |
| `SEARCH_AREAS` | `London` | Comma-separated areas to monitor |
| `CHECK_INTERVAL` | `300` | Seconds between scrape cycles |
| `HEADLESS` | `true` | Run browser without GUI (set `false` for debugging) |

## Conventions for AI Assistants

### General Principles

- Read existing code before proposing changes. Never modify files you haven't read.
- Keep changes minimal and focused on the request. Avoid unnecessary refactoring.
- Do not add features, abstractions, or error handling beyond what is asked for.
- Prefer editing existing files over creating new ones.
- Do not introduce security vulnerabilities (injection, XSS, etc.).

### Code Style

- Python 3.11+ with type hints (use `list[X]` / `str | None`, not `List` / `Optional`).
- Dataclasses for structured data.
- Logging via `logging` module (not `print`).
- Constants in `UPPER_SNAKE_CASE`, functions/variables in `lower_snake_case`.
- Private helpers prefixed with `_`.

### Git Practices

- Write clear, concise commit messages that describe the "why" not just the "what."
- Only commit when explicitly asked.
- Never force-push to main/master.
- Stage specific files rather than using `git add -A`.
- Never commit secrets, credentials, or `.env` files.

### Documentation

- Update this CLAUDE.md file as the project evolves (new tooling, commands, conventions).
- Keep README.md current with setup instructions and project description.

## Dependencies

Declared in `requirements.txt`:
- `playwright` — headless browser automation
- `requests` — HTTP client for Discord webhooks
- `python-dotenv` — `.env` file loading

## Architecture

```
                ┌─────────┐
                │ config   │  reads .env
                └────┬────┘
                     │
   ┌─────────────────┼───────────────┐
   │                 │               │
   v                 v               v
┌──────┐      ┌──────────┐   ┌──────────────┐
│ main │─────>│ scraper  │   │ discord_     │
│ loop │      │ (PW)     │   │ notifier     │
└──┬───┘      └──────────┘   └──────────────┘
   │                                 ^
   │  new jobs found                 │
   └─────────────────────────────────┘
```

`main` runs a timed loop: scrape → diff against seen set → notify Discord → sleep.
