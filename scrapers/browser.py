# scrapers/browser.py
import asyncio
import random
import logging
import httpx

from config import RATE_LIMIT_MIN, RATE_LIMIT_MAX

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def _rate_limit():
    await asyncio.sleep(random.uniform(RATE_LIMIT_MIN, RATE_LIMIT_MAX))


def _is_valid_html(html: str, url: str) -> bool:
    if not html or len(html) < 500:
        logger.warning(f"  ⚠️  Response too short: {url}")
        return False
    lowered = html.lower()
    hard_blocks = [
        "access denied",
        "unusual traffic",
        "are you human",
        "security check",
        "please wait while we verify",
        "enable javascript and cookies",
    ]
    for signal in hard_blocks:
        if signal in lowered:
            logger.warning(f"  ⚠️  Bot-block '{signal}': {url}")
            return False
    if "captcha" in lowered and ("challenge-form" in lowered or "grecaptcha.execute" in lowered):
        logger.warning(f"  ⚠️  CAPTCHA challenge page: {url}")
        return False
    if "<body" not in lowered:
        logger.warning(f"  ⚠️  No <body>: {url}")
        return False
    return True


async def fetch_page(url: str, client: httpx.AsyncClient, retries: int = 2) -> str | None:
    await _rate_limit()
    for attempt in range(1, retries + 1):
        try:
            r = await client.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
            if r.status_code != 200:
                logger.warning(f"  ⚠️  HTTP {r.status_code}: {url}")
            elif _is_valid_html(r.text, url):
                logger.info(f"  ✅ httpx OK (attempt {attempt}): {url}")
                return r.text
        except Exception as e:
            logger.warning(f"  ⚠️  httpx error {url}: {e}")
        if attempt < retries:
            await asyncio.sleep(attempt * 3)
    logger.error(f"  ❌ Failed after {retries} attempts: {url}")
    return None


def make_httpx_client(site_id: str | None = None) -> httpx.AsyncClient:
    """Build an httpx.AsyncClient.

    When `site_id == "wildlifebuyer"`, the request is routed through the
    WildlifeBuyer proxy (see config/sites/wildlifebuyer.py). Other sites
    get a direct client — only WildlifeBuyer is behind Cloudflare and
    needs the proxy.

    Uses the `proxy=` parameter (single URL string) which is supported
    by both httpx 0.27 (where `proxies=` is deprecated) and 0.28+
    (where `proxies=` is removed). The same upstream proxy handles both
    http:// and https:// because the proxy supports CONNECT.
    """
    proxy_url = None
    if site_id == "wildlifebuyer":
        # Imported lazily so other sites never pay the import cost and
        # so a missing wildlifebuyer config does not break them.
        from config.sites.wildlifebuyer import WILDLIFEBUYER_PROXY_URL
        proxy_url = WILDLIFEBUYER_PROXY_URL
        logger.info(f"  🛰️  Using WILDLIFEBUYER proxy for client (site={site_id})")

    return httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_connections=5, max_keepalive_connections=3),
        follow_redirects=True,
        proxy=proxy_url,
    )
