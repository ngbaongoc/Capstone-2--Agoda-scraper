import os
import sys
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Add the project root directory to Python path so we can import 'scraper'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "hotel_insights")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password123")
DB_PORT = os.getenv("DB_PORT", "5433")

# Check if Cleaned JSON file exists, else fallback to raw
CLEANED_FILE = os.path.join(os.path.dirname(__file__), "../data/agoda_reviews_cleaned.json")
RAW_FILE = os.path.join(os.path.dirname(__file__), "../data/agoda_reviews.json")

JSON_FILE = CLEANED_FILE if os.path.exists(CLEANED_FILE) else RAW_FILE


def get_db_connection():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    return conn

def parse_date(date_str):
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

def create_table(conn):
    try:
        cur = conn.cursor()
        logging.info("Creating table 'reviews'...")
        cur.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
            DROP TABLE IF EXISTS reviews;
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                hotel_name TEXT,
                reviewer_name TEXT,
                reviewer_score FLOAT,
                review_text TEXT,
                review_date DATE,
                room_type TEXT,
                stay_duration TEXT,
                country TEXT,
                traveler_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_review UNIQUE (hotel_name, reviewer_name, review_date)
            );
        """)
        conn.commit()
        cur.close()
        logging.info("Table 'reviews' created successfully.")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        conn.rollback()

def load_data(conn):
    if not os.path.exists(JSON_FILE):
        logging.error(f"File {JSON_FILE} not found.")
        return

    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
        
        # Flatten the data
        from scraper.utils import parse_date # Import from utils to match scraper logic
        
        reviews_to_insert = []
        for hotel in data:
            hotel_name = hotel.get('hotel_name', 'Unknown')
            for r in hotel.get('reviews', []):
                reviews_to_insert.append((
                    hotel_name,
                    r.get('reviewer_name'),
                    r.get('reviewer_score', 0.0),
                    r.get('review_text'),
                    parse_date(r.get('review_date')),
                    r.get('room_type'),
                    r.get('stay_duration'),
                    r.get('reviewer_country') or r.get('country'),
                    r.get('traveler_type')
                ))
        
        if not reviews_to_insert:
            logging.warning("No reviews found to insert.")
            return

        cur = conn.cursor()
        # INCREMENTAL LOAD: Do not truncate.
        
        logging.info(f"Processing {len(reviews_to_insert)} reviews...")
        
        insert_query = """
            INSERT INTO reviews (hotel_name, reviewer_name, reviewer_score, review_text, review_date, room_type, stay_duration, country, traveler_type)
            VALUES %s
            ON CONFLICT (hotel_name, reviewer_name, review_date) DO NOTHING
        """
        
        execute_values(cur, insert_query, reviews_to_insert)
        
        # Check how many were inserted - execute_values doesn't return count easily with ON CONFLICT
        # simplified logging
        
        conn.commit()
        cur.close()
        logging.info("Data upserted successfully (New reviews added, duplicates ignored).")
        
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        conn.rollback()

    except Exception as e:
        logging.error(f"Error loading data: {e}")
        conn.rollback()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default=JSON_FILE, help="Path to JSON file to ingest")
    args = parser.parse_args()
    
    # Override global JSON_FILE if arg provided
    if args.file:
        JSON_FILE = args.file

    try:
        conn = get_db_connection()
        create_table(conn)
        load_data(conn)
        conn.close()
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
