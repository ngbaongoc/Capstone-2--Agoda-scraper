# 🚀 QUICK START GUIDE

## ✅ Run the Application

To start the Dashboard, Database, and Airflow:

```bash
docker-compose up -d
```
*Wait ~1 minute for services to initialize.*

**Access Points:**
*   **Dashboard:** [http://localhost:8501](http://localhost:8501)
*   **Airflow:** [http://localhost:8080](http://localhost:8080) (Logins: `admin` / `admin`)

---

## 🛑 Stop the Application

To stop all services:
```bash
docker-compose down
```

---

## 🗄️ Database Connection (DBeaver)

Use these **EXACT** settings to connect to the database:

*   **Host:** `localhost`
*   **Port:** **`5433`** (⚠️ Note: Not 5432)
*   **Database:** `hotel_insights`
*   **Username:** `admin`
*   **Password:** `password123`

---

## 🛠️ Data Management

### 1. Generate Fake Data
```bash
python generate_fake_data.py
# Creates data/fake_reviews.json
```

### 2. Manual Crawl (Background)
```bash
# Example: 5 hotels, 20 reviews each
python scraper/main.py --max-hotels 5 --reviews 20 --output data/manual_crawl.json
```

### 3. Inject Data
To load any JSON file into the database:
```bash
# Replace 'your_file.json' with the file name inside 'data/' folder
docker exec hotel_dashboard python database/init_db.py --file /app/data/option_b_crawl.json
```
