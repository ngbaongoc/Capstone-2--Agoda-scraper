#!/usr/bin/env python3
"""
Script to update the database from agoda_reviews_cleaned.json
Usage: python3 database/update_from_cleaned.py
"""

import os
import sys
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "hotel_insights")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password123")
DB_PORT = os.getenv("DB_PORT", "5432")

# File path
CLEANED_JSON = os.path.join(os.path.dirname(__file__), "../data/agoda_reviews_cleaned.json")


def get_db_connection():
    """Get database connection"""
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )


def parse_date(date_str):
    """Parse date string to date object"""
    if not date_str:
        return None
    try:
        # Try format: "Reviewed October 02, 2025"
        clean_str = date_str.replace("Reviewed ", "").strip()
        return datetime.strptime(clean_str, "%B %d, %Y").date()
    except ValueError:
        try:
            # Try ISO format: "2025-10-02"
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logging.warning(f"Could not parse date: {date_str}")
            return None


def update_database():
    """Load data from cleaned JSON and update database"""
    
    # Check if file exists
    if not os.path.exists(CLEANED_JSON):
        logging.error(f"File not found: {CLEANED_JSON}")
        return False
    
    logging.info(f"Reading data from: {CLEANED_JSON}")
    
    # Load JSON data
    try:
        with open(CLEANED_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"Error reading JSON file: {e}")
        return False
    
    if not isinstance(data, list):
        logging.error("JSON data should be a list of hotel objects")
        return False
    
    logging.info(f"Found {len(data)} hotel(s) in the JSON file")
    
    # Connect to database
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logging.info("Connected to database successfully")
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return False
    
    # Prepare reviews for insertion
    reviews_to_insert = []
    total_reviews = 0
    
    for hotel in data:
        hotel_name = hotel.get('hotel_name', 'Unknown')
        reviews = hotel.get('reviews', [])
        total_reviews += len(reviews)
        
        logging.info(f"Processing hotel: {hotel_name} ({len(reviews)} reviews)")
        
        for review in reviews:
            # Extract review data
            review_data = (
                hotel_name,
                review.get('reviewer_name', 'Unknown'),
                float(review.get('reviewer_score', 0.0)),
                review.get('review_text', ''),
                parse_date(review.get('review_date')),
                review.get('room_type', ''),
                review.get('stay_duration', ''),
                review.get('reviewer_country') or review.get('country', ''),
                review.get('traveler_type', '')
            )
            reviews_to_insert.append(review_data)
    
    if not reviews_to_insert:
        logging.warning("No reviews found to insert")
        conn.close()
        return False
    
    logging.info(f"Total reviews to insert: {len(reviews_to_insert)}")
    
    # Insert data with ON CONFLICT handling
    try:
        insert_query = """
            INSERT INTO reviews (
                hotel_name, reviewer_name, reviewer_score, review_text, 
                review_date, room_type, stay_duration, country, traveler_type
            )
            VALUES %s
            ON CONFLICT (hotel_name, reviewer_name, review_date) 
            DO UPDATE SET
                reviewer_score = EXCLUDED.reviewer_score,
                review_text = EXCLUDED.review_text,
                room_type = EXCLUDED.room_type,
                stay_duration = EXCLUDED.stay_duration,
                country = EXCLUDED.country,
                traveler_type = EXCLUDED.traveler_type
        """
        
        execute_values(cur, insert_query, reviews_to_insert)
        conn.commit()
        
        # Get count
        cur.execute("SELECT COUNT(*) FROM reviews")
        total_in_db = cur.fetchone()[0]
        
        logging.info(f"✅ Database updated successfully!")
        logging.info(f"Total reviews in database: {total_in_db}")
        
        # Show breakdown by hotel
        cur.execute("""
            SELECT hotel_name, COUNT(*) as review_count 
            FROM reviews 
            GROUP BY hotel_name 
            ORDER BY review_count DESC
        """)
        
        logging.info("\nBreakdown by hotel:")
        for hotel_name, count in cur.fetchall():
            logging.info(f"  - {hotel_name}: {count} reviews")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        logging.error(f"Error inserting data: {e}")
        conn.rollback()
        conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("UPDATE DATABASE FROM CLEANED JSON")
    print("=" * 60)
    
    success = update_database()
    
    if success:
        print("\n✅ Database update completed successfully!")
    else:
        print("\n❌ Database update failed. Check logs for details.")
        sys.exit(1)
