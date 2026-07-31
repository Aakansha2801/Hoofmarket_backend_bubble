# ============================================================
# HoofMarketIQ — config/sites/wildlifebuyer.py
# All WildlifeBuyer.com-specific settings
# ============================================================
import os

SITE_ID   = "wildlifebuyer"
BASE_URL  = "https://wildlifebuyer.com"
ENABLED   = True
IMAGE_CDN = "wildlifebuyerimages.blob.core.windows.net"

# ── Proxy for WildlifeBuyer ────────────────────────────────────
# Cloudflare blocks direct requests from this server's IP.
# A rotating/forward proxy is used so WildlifeBuyer requests
# originate from a different IP. Other sites (bucktrader,
# onlinehuntingauctions) do NOT use this proxy.
#
# Override at deploy-time via the WILDLIFEBUYER_PROXY_URL env var
# (e.g. in your process manager, systemd unit, or .env file).
WILDLIFEBUYER_PROXY_URL = os.getenv(
    "WILDLIFEBUYER_PROXY_URL",
    "http://shpsfbko:hdalrep0qjma@31.56.127.193:7684",
)

# httpx 0.27 accepts a dict keyed by URL scheme.
# Same upstream proxy is used for both http:// and https:// because
# the proxy supports CONNECT (verified via curl).
WILDLIFEBUYER_PROXY = {
    "http://":  WILDLIFEBUYER_PROXY_URL,
    "https://": WILDLIFEBUYER_PROXY_URL,
}

BROWSE_CATEGORIES = [
    {"name": "Exotics & Deer",  "url": "/Browse/C160535/Exotics-Deer",  "scrape": True},
    {"name": "Livestock",       "url": "/Browse/C160829/Livestock",      "scrape": True},
    {"name": "Classifieds",     "url": "/Browse/C160536/Classifieds",    "scrape": True},
    {"name": "Taxidermy",       "url": "/Browse/C160832/Taxidermy-Related-Products", "scrape": False},
    {"name": "Equipment",       "url": "/Browse/C160825/Equipment",      "scrape": False},
    {"name": "Advertising",     "url": "/Browse/C160814/Advertising",    "scrape": False},
    {"name": "Hunting Accessories", "url": "/Browse/C160826/Hunting-Accessories", "scrape": False},
]

ACTIVE_CATEGORIES = [c for c in BROWSE_CATEGORIES if c["scrape"]]

# Slugs used in bid-button links — excluded from listing card parsing
CATEGORY_SLUGS = {"Exotics-Deer", "Livestock", "Classifieds"}

SELECTORS = {
    "listing_card": ".listing-card",
    "title":        ".listing-title",
    "price":        ".listing-price",
    "location":     ".listing-location",
    "link":         "a.listing-link",
    "next_page":    "a.next-page",
}

PAGINATION = {
    "style":      "query_param",
    "param_name": "page",
    "start":      1,
}