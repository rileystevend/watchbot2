def scrape_chrono24(url):
    # 1) force the search + mobile subdomain
    fetch_url = (url + "?dosearch=true").replace(
        "www.chrono24.com", "m.chrono24.com"
    )
    try:
        resp = requests.get(fetch_url, headers=headers, cookies=COOKIES, timeout=10)
        resp.raise_for_status()
        logger.info(f"HTTP fetch succeeded for {fetch_url}")
        return _parse_listings(resp.text)
    except Exception as e:
        logger.warning(f"HTTP failed ({e}), falling back to Selenium")
        return _scrape_with_selenium(fetch_url)

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
