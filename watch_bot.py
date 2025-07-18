import logging
from helpers.ebay_scraper import scrape_ebay_certified_rolex
from helpers.evaluator import evaluate_listing
from helpers.notifier import send_notification

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger('watch-bot')

def main():
    try:
        url = "https://www.ebay.com/sch/i.html?_nkw=certified+rolex+watchh&_sop=10"
        logger.info(f"Starting scrape for {url}")
        listings = scrape_ebay_certified_rolex(url)
        logger.info(f"Retrieved {len(listings)} listings")

        if not listings:
            logger.warning("No listings found. Exiting.")
            return

        for listing in listings:
            score = evaluate_listing(listing["title"])
            listing["score"] = score
            logger.info(f"Score is {score}")
            time.sleep(0.5)  # throttle so you don’t get more 429s
            try:
                result = evaluate_listing(listing)
                logger.info(f"Evaluation for '{listing['title']}': {result}")
                if "undervalued" in result.lower():
                    message = (
                        f"Title: {listing['title']}\n"
                        f"Price: {listing['price']}\n"
                        f"Analysis: {result}\n"
                        f"Link: {listing['link']}"
                    )
                    send_notification(message)
            except Exception as eval_err:
                logger.error(f"Failed to evaluate listing {listing}: {eval_err}")
    except Exception as main_err:
        logger.exception(f"Unhandled exception in main: {main_err}")

if __name__ == '__main__':
    main()
