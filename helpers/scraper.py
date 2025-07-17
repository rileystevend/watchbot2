import os
import random
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
]

def scrape_chrono24(url):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml',
        'Referer': 'https://www.google.com',
        'Connection': 'keep-alive',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text
        print(f"[scraper] HTTP fetch succeeded: status={resp.status_code}, length={len(html)}")
    except requests.RequestException as e:
        print(f"[scraper] HTTP fetch failed ({e}), falling back to Selenium")
        return scrape_with_selenium(url)

    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    for item in soup.select('.article-item-container'):
        price_elem = item.select_one('.article-price')
        title_elem = item.select_one('.article-title')
        link_elem = item.select_one('a')
        if price_elem and title_elem and link_elem:
            listings.append({
                'title': title_elem.text.strip(),
                'price': price_elem.text.strip(),
                'link': link_elem['href']
            })
    print(f"[scraper] Parsed {len(listings)} listings")
    return listings

def scrape_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(2)
    # click the cookie-consent button if present
    try:
        btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        btn.click()
        time.sleep(1)
    except:
        pass

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')
    listings = []
    for item in soup.select('.article-item-container'):
        price_elem = item.select_one('.article-price')
        title_elem = item.select_one('.article-title')
        link_elem = item.select_one('a')
        if price_elem and title_elem and link_elem:
            listings.append({
                'title': title_elem.text.strip(),
                'price': price_elem.text.strip(),
                'link': link_elem['href']
            })
    print(f"[scraper/Selenium] Parsed {len(listings)} listings")
    return listings
