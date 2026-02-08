import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

# Proxy
PROXY_URL = os.getenv("PROXY_URL", "")

# Search
SEARCH_AREAS = [
    area.strip()
    for area in os.getenv("SEARCH_AREAS", "London").split(",")
    if area.strip()
]

# Scheduling
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))

# Browser
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

# Target URL
BASE_URL = "https://www.jobsatamazon.co.uk/app#/jobSearch"
