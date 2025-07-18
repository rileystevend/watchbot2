import logging
import random
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger('scraper')

# Rotate user agents to mimic real browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

# Cookie to bypass cookie-consent banner
COOKIES = {"cookieconsent_status": "dismiss"}

headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml',
        'Referer': 'https://www.google.com',
        'Connection': 'keep-alive',
}

from urllib.parse import urlparse, urlunparse

def _normalize_desktop_url(url: str) -> str:
    """
    Turn either
      https://www.chrono24.com/rolex/daytona--mod2.htm
      https://www.chrono24.com/m-rolex/daytona--mod2.htm
      https://m.chrono24.com/rolex/daytona--mod2.htm
    all into
      https://www.chrono24.com/rolex/daytona--mod2.htm
    """
    p = urlparse(url)
    # 1) Fix the host to www.chrono24.com
    host = p.netloc
    if host.startswith("m."):
        host = host.replace("m.", "www.", 1)
    # 2) Strip any leading "/m-" from the path
    path = p.path
    if path.startswith("/m-"):
        path = path[len("/m-"):]
    # 3) Rebuild without any query or fragment
    return urlunparse((p.scheme, host, path, "", "", ""))

def scrape_chrono24(url):
    # 1) force the search + mobile subdomain
    desktop_url = _normalize_desktop_url(url)
    fetch_url = (desktop_url + "?dosearch=true").replace(
        "www.chrono24.com", "m.chrono24.com"
    )
    logger.info(f"Normalized desktop URL → {desktop_url}")
    logger.info(f"Fetching mobile URL → {fetch_url}")
    
    try:
        resp = requests.get(fetch_url, headers=headers, cookies=COOKIES, timeout=10)
        resp.raise_for_status()
        logger.info(f"HTTP fetch succeeded for {fetch_url}")
        return _parse_listings(resp.text)
    except Exception as e:
        logger.warning(f"HTTP failed ({e}), falling back to Selenium")
        desktop_search = desktop_url + "?dosearch=true"
        return _scrape_with_selenium(desktop_search)

def _scrape_with_selenium(url):
    service = Service("/usr/bin/chromedriver")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(service=service, options=options)
    # inject consent on the *www* domain so mobile inherits it
    driver.get("https://www.chrono24.com/")
    driver.add_cookie({
        "name":   "cookieconsent_status",
        "value":  "dismiss",
        "domain": "www.chrono24.com",
        "path":   "/"
    })

    # now hit the mobile+search URL
    driver.get(url)
    # 2) WAIT for the mobile tiles
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.listing-item--tile"))
    )
    # scroll to ensure any lazy-loading
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    html = driver.page_source
    driver.quit()
    logger.info("Selenium fetch succeeded and injected cookie")
    # 3) Dump a quick snippet so you can verify you really have tiles
    snippet_idx = html.lower().find('div class="listing-item--tile')
    if snippet_idx != -1:
        logger.debug("[scraper] TILE SNIPPET:\n" + html[snippet_idx:snippet_idx+500])
    else:
        logger.debug("[scraper] No listing-item--tile found in HTML")

    return _parse_listings(html)

def _parse_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for tile in soup.select("div.listing-item--tile"):
        try:
            title = tile.select_one(".listing-item--title").text.strip()
            price = tile.select_one(".listing-item--price").text.strip()
            href  = tile.select_one("a")["href"]
            listings.append({
                "title": title,
                "price": price,
                "link":  "https://www.chrono24.com" + href
            })
        except Exception as err:
            logger.debug(f"Failed parsing a tile: {err}")
    logger.info(f"Parsed {len(listings)} listings")
    return listings
