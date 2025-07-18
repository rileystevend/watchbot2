import logging
import random
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("ebay_scraper")

# Rotate user-agents to keep eBay happy
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

def parse_ebay_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    listings = []

    # Each result is in an <li class="s-item"> block
    for item in soup.select("li.s-item"):
        try:
            title_el = item.select_one(".s-item__title")
            price_el = item.select_one(".s-item__price")
            link_el  = item.select_one(".s-item__link")

            # skip ads or malformed entries
            if not (title_el and price_el and link_el):
                continue

            title = title_el.get_text(strip=True)
            price = price_el.get_text(strip=True)
            link  = link_el["href"]

            listings.append({
                "title": title,
                "price": price,
                "link":  link
            })
        except Exception as err:
            logger.debug(f"parse error: {err}")

    logger.info(f"Parsed {len(listings)} eBay listings")
    return listings

def scrape_ebay_certified_rolex():
    # Build the eBay search URL for “certified Rolex watch”
    query = "certified+rolex+watch"
    url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_sop=10"  # sort by newly listed

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
        "Connection": "keep-alive",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info(f"eBay fetch succeeded: {resp.status_code} {len(resp.text)} bytes")
        return parse_ebay_listings(resp.text)
    except Exception as e:
        logger.error(f"Failed to fetch eBay listings: {e}")
        return []


if __name__ == "__main__":
    for watch in scrape_ebay_certified_rolex():
        print(f"{watch['title']} — {watch['price']}\n  {watch['link']}\n
