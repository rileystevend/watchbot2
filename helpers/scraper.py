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
    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.chrono24.com/")
    driver.add_cookie({
        "name":  "cookieconsent_status",
        "value": "dismiss",
        "domain": "www.chrono24.com",
        "path":   "/"
     })
    try:
        driver.get(url)

        # Wait for the JS-rendered listings to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'nav.s3-links'))
        )
    
        # now scroll *way* down into the results area
        driver.execute_script("window.scrollTo(0, 3000);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    
        # finally wait for at least one result card to appear
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.article-item-container'))
        )
        # Scroll to bottom to load any lazy content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Dismiss the cookie banner if it's still present
        try:
            btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            btn.click()
        except Exception:
            pass

        html = driver.page_source
#        start = html.lower().find('<body')
#        end   = html.lower().find('</body>') + len('</body>')
#        logger.info(f"[scraper] BODY HTML:\n{html[start:end]}")
        
        driver.quit()
        logger.info("Selenium fetch succeeded with dynamic wait and injected cookie")
# find where the first card lives in the HTML and log a snippet
        idx = html.lower().find('<div class="article-item-container')
        if idx != -1:
            snippet = html[idx: idx + 1000]   # 1,000 chars around the first card
            logger.info(f"[scraper] SAMPLE CARD HTML:\n{snippet}")
        else:
            logger.info("[scraper] No <div.article-item-container> found in HTML")
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
