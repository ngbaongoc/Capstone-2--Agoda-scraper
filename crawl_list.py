import logging
import json
import time
from scraper.scraper import AgodaScraper
from scraper.utils import setup_logging, save_data

# URL List provided by user
URLS = [
    "agoda.com/maximilan-danang-beach-hotel/hotel/da-nang-vn.html?countryId=38&finalPriceView=1&isShowMobileAppPrice=false&cid=1922896&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2026-01-1&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&tag=7adbeb35-4108-414c-9559-32893b4cdfe5&flightSearchCriteria=[object%20Object]&tspTypes=9&los=7&searchrequestid=3ac72566-660b-49ee-8c77-b24f817198e8",
    "agoda.com/jbay-beachfront-boutique-hotel/hotel/da-nang-vn.html?countryId=38&finalPriceView=1&isShowMobileAppPrice=false&cid=1922896&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2026-01-1&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&tag=7adbeb35-4108-414c-9559-32893b4cdfe5&flightSearchCriteria=[object%20Object]&los=7&searchrequestid=3ac72566-660b-49ee-8c77-b24f817198e8",
    "agoda.com/leaf-beachfront-hotel-da-nang/hotel/da-nang-vn.html?countryId=38&finalPriceView=1&isShowMobileAppPrice=false&cid=1922896&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2026-01-1&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&tag=7adbeb35-4108-414c-9559-32893b4cdfe5&flightSearchCriteria=[object%20Object]&los=7&searchrequestid=3ac72566-660b-49ee-8c77-b24f817198e8",
    "https://www.agoda.com/crowne-plaza-danang-city-centre-by-ihg/hotel/da-nang-vn.html?countryId=38&finalPriceView=1&isShowMobileAppPrice=false&cid=1922896&numberOfBedrooms=&familyMode=false&adults=2&children=0&rooms=1&maxRooms=0&checkIn=2026-01-1&isCalendarCallout=false&childAges=&numberOfGuest=0&missingChildAges=false&travellerType=1&showReviewSubmissionEntry=false&currencyCode=VND&isFreeOccSearch=false&tag=7adbeb35-4108-414c-9559-32893b4cdfe5&flightSearchCriteria=[object%20Object]&tspTypes=-1&los=7&searchrequestid=3ac72566-660b-49ee-8c77-b24f817198e8"
]

def clean_url(url):
    url = url.strip()
    if not url.startswith("http"):
        url = "https://www." + url
    return url

def main():
    logger = setup_logging()
    scraper = AgodaScraper(headless=True, logger=logger)
    
    results = []
    output_path = "data/custom_list_crawl.json"
    
    try:
        scraper.start()
        
        for i, raw_url in enumerate(URLS):
            url = clean_url(raw_url)
            logger.info(f"Processing {i+1}/{len(URLS)}: {url}")
            
            try:
                # Scrape 50 reviews per hotel
                data = scraper.scrape_hotel(url, max_reviews=50)
                results.append(data)
                
                # Progressive save
                save_data(results, output_path, logger)
                
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
            
            # Rate limit pause
            if i < len(URLS) - 1:
                time.sleep(2)
                
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        scraper.close()
        logger.info("Batch crawl complete.")

if __name__ == "__main__":
    main()
