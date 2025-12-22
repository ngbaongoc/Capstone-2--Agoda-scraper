import argparse
import logging
import os
from scraper import AgodaScraper
from utils import setup_logging, save_data

def get_latest_review_dates():
    """Fetch the latest review date for each hotel from the database."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "hotel_insights"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASS", "password123"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        cur.execute("SELECT hotel_name, MAX(review_date) FROM reviews GROUP BY hotel_name")
        results = cur.fetchall()
        
        stop_dates = {}
        for row in results:
            if row[1]:
                stop_dates[row[0]] = row[1]
        
        conn.close()
        return stop_dates
    except Exception as e:
        logging.warning(f"Could not fetch latest dates from DB: {e}")
        return {}

def main():
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(description="Agoda Hotel Reviews Scraper")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--max-hotels", type=int, default=3, help="Max hotels to scrape")
    parser.add_argument("--reviews", type=int, default=20, help="Reviews per hotel")
    parser.add_argument("--url", type=str, 
                       default="https://www.agoda.com/city/da-nang-vn.html?ds=tCjgS9%2FXlnLw8%2F0G",
                       help="Search URL")
    parser.add_argument("--mode", choices=["multiple", "single"], default="multiple", help="Scrape mode")
    parser.add_argument("--single-url", type=str, help="URL for single hotel mode")
    parser.add_argument("--output", type=str, default="data/agoda_reviews.json", help="Output .json file path")
    
    args = parser.parse_args()
    
    # Handle output path
    if args.output == "data/agoda_reviews.json": # Default value
        from datetime import datetime
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        output_path = f"data/{timestamp}.json"
    else:
        output_path = args.output

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Fetch existing data for incremental scraping
    stop_dates = get_latest_review_dates()
    if stop_dates:
        logger.info(f"Incremental Scraping Active. Loaded {len(stop_dates)} existing hotels.")
    
    scraper = AgodaScraper(headless=args.headless, logger=logger)
    try:
        scraper.start()
        
        if args.mode == "single":
            if not args.single_url:
                logger.error("Single mode requires --single-url")
                return
            data = scraper.scrape_hotel(args.single_url, max_reviews=args.reviews)
            save_data([data], output_path, logger)
        else:
            reviews = scraper.scrape_multiple(args.url, max_hotels=args.max_hotels, reviews_per_hotel=args.reviews, stop_dates=stop_dates, output_path=output_path)
            save_data(reviews, output_path, logger)
            
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
