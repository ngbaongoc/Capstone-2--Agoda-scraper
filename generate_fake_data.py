import json
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker
fake = Faker()

def generate_reviews(num_reviews=50):
    reviews = []
    
    # Curated list of realistic review templates
    review_templates = [
        {
            "score": 10.0,
            "text": "Exceptional",
            "title": "“Perfect stay!”",
            "content": "Absolutely loved our stay here. The staff went above and beyond to make us feel welcome. The room was spotless and the view was breathtaking. Breakfast had a huge variety of options. Will definitely come back!"
        },
        {
            "score": 9.6,
            "text": "Exceptional",
            "title": "“Great location and service”",
            "content": "The hotel is in a prime location, close to the beach and many restaurants. Our room was upgrading upon arrival which was a lovely surprise. The rooftop pool is amazing in the evenings."
        },
        {
            "score": 8.8,
            "text": "Excellent",
            "title": "“Value for money”",
            "content": "Good hotel for the price. The room was clean and comfortable. Staff were friendly but check-in was a bit slow. The breakfast was decent but could use more western options."
        },
        {
            "score": 10.0,
            "text": "Exceptional",
            "title": "“A hidden gem in Da Nang”",
            "content": "We were blown away by the quality of this hotel. From the moment we stepped in, the service was impeccable. The room design is modern and very functional. Highly recommended for couples."
        },
        {
            "score": 7.5,
            "text": "Very Good",
            "title": "“Nice but noisy”",
            "content": "The hotel itself is very nice and modern. However, the soundproofing isn't great. We could hear traffic noise and neighbors talking. If you are a light sleeper, bring earplugs."
        },
        {
            "score": 9.2,
            "text": "Superb",
            "title": "“Wonderful family vacation”",
            "content": "We traveled with two kids and the hotel was very accommodating. They provided an extra cot and the kids loved the pool. The location is very convenient for families."
        },
        {
            "score": 6.0,
            "text": "Pleasant",
            "title": "“Average experience”",
            "content": "It was okay for a short stay. The room smelled a bit musty and the AC was loud. Staff were polite but not overly helpful. Location is the best part."
        },
        {
            "score": 10.0,
            "text": "Exceptional",
            "title": "“Best hotel in Vietnam so far”",
            "content": "I have traveled all over Vietnam and this is hands down the best hotel I've stayed at. The attention to detail is amazing. The bed is super comfortable and the shower pressure is great."
        },
        {
            "score": 8.4,
            "text": "Excellent",
            "title": "“Good base for exploring”",
            "content": "Clean, safe, and central. That's all we needed. We were out exploring most of the day so didn't use the facilities much, but everything looked well-maintained."
        },
        {
            "score": 5.5,
            "text": "Passable",
            "title": "“Disappointing housekeeping”",
            "content": "We had to ask three times for fresh towels. The floor was sticky when we arrived. Not what I expected based on the photos. Location is good though."
        },
         {
            "score": 9.0,
            "text": "Superb",
            "title": "“Luxury feel at affordable price”",
            "content": "Feels like a 5-star hotel without the price tag. The lobby is grand and the rooms are spacious. The afternoon tea included was a nice touch."
        },
        {
            "score": 4.0,
            "text": "Average",
            "title": "“Not coming back”",
            "content": "Very disappointed. The photos are misleading. The pool is tiny and the water looked dirty. Values for money is very low here."
        }
    ]
    
    room_types = [
        "Superior City View Room", 
        "Deluxe Ocean View", 
        "Executive Suite", 
        "Family Room",
        "Presidential Suite"
    ]
    
    traveler_types = [
        "Family with young children",
        "Solo traveler",
        "Couple",
        "Group",
        "Business traveler"
    ]

    for _ in range(num_reviews):
        # Pick a random template
        template = random.choice(review_templates)
        
        # Add slight variation to score to avoid duplicates looking too fake
        score_variance = round(random.uniform(-0.1, 0.1), 1)
        final_score = max(2.0, min(10.0, template["score"] + score_variance))

        # Generate dates
        stay_date = fake.date_between(start_date='-1y', end_date='today')
        stay_month = stay_date.strftime("%B %Y")
        stay_duration_days = random.randint(1, 7)
        
        review_date = stay_date + timedelta(days=random.randint(1, 14))
        review_date_str = review_date.strftime("Reviewed %B %d, %Y")

        review = {
            "reviewer_score": final_score,
            "reviewer_score_text": template["text"],
            "reviewer_name": fake.name(),
            "reviewer_country": fake.country(),
            "traveler_type": random.choice(traveler_types),
            "room_type": f"{random.choice(room_types)} - Afternoon Tea Included",
            "stay_duration": f"Stayed {stay_duration_days} nights in {stay_month}",
            "review_title": template["title"],
            "review_text": template["content"],
            "review_date": review_date_str
        }
        reviews.append(review)

    return reviews

def main():
    hotel_names = ["Muong Thanh Luxury Da Nang Hotel", "Dao Ngoc Hotel"]
    data = []

    for hotel_name in hotel_names:
        hotel_data = {
            "hotel_name": hotel_name,
            "reviews": generate_reviews(50)
        }
        data.append(hotel_data)
    
    output_file = "fake_reviews.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated fake reviews for {len(hotel_names)} hotels in {output_file}")

if __name__ == "__main__":
    main()


