import logging
import requests

from src.config import DISCORD_WEBHOOK_URL
from src.scraper import Job

logger = logging.getLogger(__name__)

MAX_EMBED_DESCRIPTION = 4096
MAX_EMBEDS_PER_MESSAGE = 10


def send_job_alert(jobs: list[Job], areas: list[str]) -> bool:
    """Send a Discord message listing newly found jobs.

    Returns True if the message was sent successfully.
    """
    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL not set — skipping notification")
        return False

    if not jobs:
        return False

    area_label = ", ".join(areas) if areas else "all areas"

    embeds = []
    for job in jobs[:MAX_EMBEDS_PER_MESSAGE]:
        fields = []
        if job.location:
            fields.append({"name": "Location", "value": job.location, "inline": True})
        if job.pay:
            fields.append({"name": "Pay", "value": job.pay, "inline": True})
        if job.schedule:
            fields.append({"name": "Schedule", "value": job.schedule, "inline": True})

        embed = {
            "title": job.title[:256],
            "color": 0xFF9900,  # Amazon orange
            "fields": fields,
        }

        if job.url:
            url = job.url
            if not url.startswith("http"):
                url = f"https://www.jobsatamazon.co.uk{url}"
            embed["url"] = url

        embeds.append(embed)

    overflow = len(jobs) - MAX_EMBEDS_PER_MESSAGE
    content = f"**{len(jobs)} job(s) found near {area_label}**"
    if overflow > 0:
        content += f" (showing first {MAX_EMBEDS_PER_MESSAGE}, {overflow} more not shown)"

    payload = {
        "content": content,
        "embeds": embeds,
    }

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=15)
        resp.raise_for_status()
        logger.info("Discord notification sent (%d jobs)", len(jobs))
        return True
    except requests.RequestException as exc:
        logger.error("Failed to send Discord notification: %s", exc)
        return False
