import logging
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

logger = logging.getLogger('scraper')

# Rotate user agents to mimic real browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

# Cookie to bypass cookie-consent banner
COOKIES = {"cookieconsent_status": "dismiss"}


def scrape_chrono24(url):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml',
        'Referer': 'https://www.google.com',
        'Connection': 'keep-alive',
    }
    try:
        resp = requests.get(url, headers=headers, cookies=COOKIES, timeout=10)
        resp.raise_for_status()
        html = resp.text
        logger.info(f"HTTP fetch succeeded: status={resp.status_code}, length={len(html)}")
        return _parse_listings(html)
    except Exception as http_err:
        logger.warning(f"HTTP fetch failed ({http_err}), falling back to Selenium")
        return _scrape_with_selenium(url)


def _scrape_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    options.binary_location = '/usr/bin/chromium'
    try:
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        # Dismiss cookie banner
        try:
            btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            btn.click()
        except Exception:
            pass
        html = driver.page_source
        # after html = resp.text (or html = driver.page_source)
        logger.info(f"[scraper] HTML snippet:\n{html[:2000]}")  # log the first 2000 characters
        driver.quit()
        logger.info("Selenium fetch succeeded")
        return _parse_listings(html)
    except Exception as sel_err:
        logger.error(f"Selenium fetch failed: {sel_err}")
        return []


def _parse_listings(html):
    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    for item in soup.select('.article-item-container'):
        try:
            price = item.select_one('.article-price').text.strip()
            title = item.select_one('.article-title').text.strip()
            link = item.select_one('a')['href']
            listings.append({'title': title, 'price': price, 'link': link})
        except Exception as parse_err:
            logger.debug(f"Failed parsing an item: {parse_err}")
    logger.info(f"Parsed {len(listings)} listings")
    return listings
