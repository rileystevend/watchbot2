from helpers.scraper import scrape_chrono24
from helpers.evaluator import evaluate_listing
from helpers.notifier import send_notification

def main():
    url = "https://www.chrono24.com/rolex/daytona--mod2.htm"
    listings = scrape_chrono24(url)
    print(f"[bot] Retrieved {len(listings)} listings")
    for listing in listings:
        result = evaluate_listing(listing)
        if "undervalued" in result.lower():
            message = (
                f"Title: {listing['title']}\n"
                f"Price: {listing['price']}\n"
                f"Analysis: {result}\n"
                f"Link: {listing['link']}"
            )
            send_notification(message)

if __name__ == '__main__':
    main()
