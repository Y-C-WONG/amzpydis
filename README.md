# amzpydis

A Playwright-based Python scraper that monitors [Amazon UK warehouse jobs](https://www.jobsatamazon.co.uk/app#/jobSearch) and sends Discord notifications when openings appear in your target areas.

## Features

- Scrapes the Amazon UK jobs SPA using headless Chromium via Playwright
- Filters jobs by configurable location/area keywords
- Sends rich Discord embed notifications with job details
- Tracks already-seen jobs to avoid duplicate alerts
- Supports HTTP/SOCKS proxy for IP rotation
- Runs on a configurable interval (default: every 5 minutes)
- Docker-ready for VPS deployment

## Quick Start

### Prerequisites

- Python 3.11+
- A Discord webhook URL ([how to create one](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))

### Install

```sh
git clone https://github.com/Y-C-WONG/amzpydis.git
cd amzpydis

pip install -r requirements.txt
playwright install chromium
```

### Configure

```sh
cp .env.example .env
```

Edit `.env` with your values:

```
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
SEARCH_AREAS=London,Manchester
CHECK_INTERVAL=300
PROXY_URL=http://user:pass@proxy-host:port
HEADLESS=true
```

| Variable | Default | Description |
|---|---|---|
| `DISCORD_WEBHOOK_URL` | *(required)* | Discord webhook for notifications |
| `SEARCH_AREAS` | `London` | Comma-separated areas/cities to monitor |
| `CHECK_INTERVAL` | `300` | Seconds between scrape cycles |
| `PROXY_URL` | *(empty)* | Optional HTTP proxy (`http://user:pass@host:port`) |
| `HEADLESS` | `true` | Set `false` to see the browser for debugging |

### Run

```sh
python -m src.main
```

## Deploy to VPS (Docker)

```sh
# On your VPS:
git clone https://github.com/Y-C-WONG/amzpydis.git
cd amzpydis
cp .env.example .env
# Edit .env with your production values

docker compose up -d --build
```

View logs:
```sh
docker compose logs -f scraper
```

Stop:
```sh
docker compose down
```

## Project Structure

```
src/
├── config.py             # Env var loading
├── scraper.py            # Playwright scraper + Job dataclass
├── discord_notifier.py   # Discord webhook sender
└── main.py               # Entrypoint + scheduling loop
```

## How It Works

1. **Scrape** — Launches headless Chromium, navigates to the Amazon UK jobs SPA, waits for job cards to render, and extracts listings.
2. **Filter** — Matches jobs against your configured `SEARCH_AREAS` by checking location text.
3. **Diff** — Compares against previously seen jobs to find only new openings.
4. **Notify** — Sends new jobs to Discord as rich embeds (title, location, pay, schedule).
5. **Sleep** — Waits `CHECK_INTERVAL` seconds, then repeats.

## License

MIT
