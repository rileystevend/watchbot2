from bs4 import BeautifulSoup
from selenium import webdriver

def scrape_chrono24(url):
    driver = webdriver.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listings = []
    for item in soup.select('.article-item-container'):
        price = item.select_one('.article-price').text.strip()
        title = item.select_one('.article-title').text.strip()
        link = item.select_one('a')['href']
        listings.append({"title": title, "price": price, "link": link})
    driver.quit()
    return listings
