import logging
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Browser, Page, Playwright

from src.config import BASE_URL, HEADLESS, PROXY_URL

logger = logging.getLogger(__name__)

NAVIGATION_TIMEOUT = 60_000  # 60s for page loads
ELEMENT_TIMEOUT = 30_000     # 30s for element waits


@dataclass
class Job:
    title: str
    location: str
    job_id: str = ""
    url: str = ""
    pay: str = ""
    schedule: str = ""

    def __eq__(self, other):
        if not isinstance(other, Job):
            return False
        return self.title == other.title and self.location == other.location

    def __hash__(self):
        return hash((self.title, self.location))


@dataclass
class ScraperResult:
    jobs: list[Job] = field(default_factory=list)
    error: str | None = None


def _build_browser_args() -> dict:
    """Build Playwright browser launch arguments."""
    args = {"headless": HEADLESS}
    if PROXY_URL:
        args["proxy"] = {"server": PROXY_URL}
        logger.info("Using proxy: %s", PROXY_URL.split("@")[-1] if "@" in PROXY_URL else PROXY_URL)
    return args


def _extract_jobs_from_page(page: Page) -> list[Job]:
    """Extract job listings from the currently loaded page."""
    jobs = []

    # The site is an SPA — wait for job cards to render.
    # Try multiple common selectors that Amazon job sites use.
    card_selectors = [
        "[data-test='job-card']",
        ".job-card",
        ".job-tile",
        ".jobCard",
        ".job-listing",
        ".job-result",
        ".job-item",
        "a[href*='job']",
    ]

    cards_selector = None
    for sel in card_selectors:
        try:
            page.wait_for_selector(sel, timeout=5_000)
            cards_selector = sel
            logger.info("Found job cards with selector: %s", sel)
            break
        except Exception:
            continue

    if not cards_selector:
        # Fallback: look for any repeated list-like structure
        # by inspecting what the page actually rendered.
        logger.warning("No known card selector matched. Attempting generic extraction.")
        return _extract_jobs_generic(page)

    cards = page.query_selector_all(cards_selector)
    logger.info("Found %d job card elements", len(cards))

    for card in cards:
        try:
            title = _get_text(card, "h2, h3, .job-title, .title, [data-test='job-title']") or card.inner_text().strip()[:100]
            location = _get_text(card, ".location, .job-location, [data-test='job-location']") or ""
            pay = _get_text(card, ".pay, .salary, .compensation, [data-test='job-pay']") or ""
            schedule = _get_text(card, ".schedule, .shift, [data-test='job-schedule']") or ""

            href = card.get_attribute("href") or ""
            job_id = href.split("/")[-1] if href else ""

            if title:
                jobs.append(Job(
                    title=title.strip(),
                    location=location.strip(),
                    job_id=job_id,
                    url=href,
                    pay=pay.strip(),
                    schedule=schedule.strip(),
                ))
        except Exception as exc:
            logger.debug("Error extracting card: %s", exc)

    return jobs


def _extract_jobs_generic(page: Page) -> list[Job]:
    """Fallback extraction: grab all visible text blocks that look like job listings."""
    jobs = []

    # Capture the full page content and look for structured data
    # by finding repeated DOM patterns.
    all_links = page.query_selector_all("a")
    for link in all_links:
        href = link.get_attribute("href") or ""
        text = link.inner_text().strip()

        # Skip navigation / header links
        if not text or len(text) < 5 or len(text) > 300:
            continue

        # Heuristic: job links usually contain keywords
        combined = (href + " " + text).lower()
        if any(kw in combined for kw in ["job", "position", "role", "shift", "warehouse", "driver", "sortation", "fulfilment", "fulfillment"]):
            jobs.append(Job(
                title=text,
                location="",
                url=href,
            ))

    return jobs


def _get_text(element, selector: str) -> str:
    """Safely get inner text of a child element matching selector."""
    try:
        child = element.query_selector(selector)
        if child:
            return child.inner_text().strip()
    except Exception:
        pass
    return ""


def scrape_jobs(search_areas: list[str]) -> ScraperResult:
    """
    Launch browser, navigate to Amazon UK jobs, and extract listings
    filtered by the given search areas.
    """
    all_jobs: list[Job] = []

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**_build_browser_args())
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()

            logger.info("Navigating to %s", BASE_URL)
            page.goto(BASE_URL, timeout=NAVIGATION_TIMEOUT, wait_until="networkidle")

            # Give the SPA extra time to hydrate
            page.wait_for_timeout(3_000)

            # Attempt to interact with location/area search if available
            _try_search_by_area(page, search_areas)

            # Wait for results to load after any search interaction
            page.wait_for_timeout(3_000)

            raw_jobs = _extract_jobs_from_page(page)
            logger.info("Extracted %d raw jobs", len(raw_jobs))

            # Filter by area if location data is available
            if search_areas:
                for job in raw_jobs:
                    if _job_matches_area(job, search_areas):
                        all_jobs.append(job)
                logger.info("After area filter: %d jobs match %s", len(all_jobs), search_areas)

                # If we couldn't filter (no location data), return all
                if not all_jobs and raw_jobs:
                    logger.info("No location data to filter on — returning all %d jobs", len(raw_jobs))
                    all_jobs = raw_jobs
            else:
                all_jobs = raw_jobs

            browser.close()

    except Exception as exc:
        logger.exception("Scraper error")
        return ScraperResult(error=str(exc))

    return ScraperResult(jobs=all_jobs)


def _try_search_by_area(page: Page, areas: list[str]) -> None:
    """Try to use the page's search/filter UI to narrow results by area."""
    search_selectors = [
        "input[type='search']",
        "input[placeholder*='location' i]",
        "input[placeholder*='city' i]",
        "input[placeholder*='postcode' i]",
        "input[placeholder*='search' i]",
        "input[aria-label*='location' i]",
        "input[aria-label*='search' i]",
        "#locationSearchInput",
        "#searchInput",
        ".search-input input",
    ]

    search_input = None
    for sel in search_selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                search_input = el
                logger.info("Found search input: %s", sel)
                break
        except Exception:
            continue

    if search_input and areas:
        query = areas[0]  # Use first area for the search box
        try:
            search_input.click()
            search_input.fill(query)
            logger.info("Typed area '%s' into search input", query)

            # Try pressing Enter or clicking a search button
            page.keyboard.press("Enter")
            page.wait_for_timeout(2_000)
        except Exception as exc:
            logger.debug("Could not interact with search input: %s", exc)


def _job_matches_area(job: Job, areas: list[str]) -> bool:
    """Check if a job's location matches any of the target areas."""
    if not job.location:
        return False
    location_lower = job.location.lower()
    return any(area.lower() in location_lower for area in areas)
