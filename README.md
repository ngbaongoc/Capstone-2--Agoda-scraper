# 🏨 Agoda Hotel Reviews Dashboard

A comprehensive hotel review analytics dashboard that scrapes Agoda reviews, performs AI sentiment analysis, and provides actionable insights for hotel management.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)

## 🌟 Features

- **📊 Real-time Analytics Dashboard** - Interactive Streamlit dashboard with multi-hotel support
- **🤖 AI Sentiment Analysis** - Automatic sentiment scoring and conflict detection
- **🔄 Automated Scraping** - Airflow-powered scheduled data collection from Agoda
- **💾 Smart Caching** - Redis-based caching for optimal performance
- **📈 Advanced Visualizations** - Trend analysis, word clouds, demographics, and category breakdowns
- **⚡ Action Center** - Priority-based review management with email templates
- **🔍 Smart Search** - Full-text search across all reviews

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│   Streamlit     │◄────►│  PostgreSQL  │◄────►│   Airflow   │
│   Dashboard     │      │   Database   │      │  Scheduler  │
└────────┬────────┘      └──────────────┘      └──────┬──────┘
         │                                              │
         │              ┌──────────────┐               │
         └─────────────►│    Redis     │◄──────────────┘
                        │    Cache     │
                        └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Option 1: Using Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/Agentic_web_scraping.git
cd Agentic_web_scraping

# 2. Start all services
docker-compose up -d

# 3. Initialize the database
docker exec hotel_dashboard python3 database/init_db.py

# 4. Access the services
# Dashboard: http://localhost:8501
# Airflow: http://localhost:8080 (admin/admin)
```

### Option 2: Using Docker Hub Image

```bash
# Pull the image
docker pull yourusername/hotel-insights-dashboard:latest

# Run with environment variables
docker run -p 8501:8501 \
  -e DATABASE_URL=postgresql://admin:password123@your-db:5432/hotel_insights \
  -e REDIS_HOST=your-redis \
  yourusername/hotel-insights-dashboard:latest
```

### Option 3: Local Development

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirement.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Set up database
python3 database/init_db.py

# 5. Run the dashboard
streamlit run app/dashboard.py
```

## 📊 Dashboard Access

Once running, access the dashboard at `http://localhost:8501`

### Default Features:
- ✅ Multi-hotel selection dropdown
- ✅ Date range filtering
- ✅ Navigation: Overview, Complaints, Fake Reviews
- ✅ Real-time metrics and sentiment analysis
- ✅ Interactive charts and word clouds
- ✅ Priority-based action center
- ✅ Full-text review search

## 🗄️ Database Setup

### Initialize Database

```bash
# Using Docker
docker exec hotel_dashboard python3 database/init_db.py

# Local
python3 database/init_db.py
```

### Update from Cleaned Data

```bash
# Clean and deduplicate JSON data
python3 database/clean_data.py

# Update database
python3 database/update_from_cleaned.py
```

## 🤖 Automated Scraping with Airflow

### Access Airflow

1. Navigate to `http://localhost:8080`
2. Login with credentials: **admin / admin**
3. Enable the `agoda_scraper_dag` DAG
4. Trigger manually or wait for scheduled runs

### Scraping Configuration

Edit `/airflow/dags/agoda_scraper.py` to configure:
- Target hotels
- Scraping schedule
- Number of reviews to fetch

## 📦 Data Pipeline

```
1. Scrape Reviews (Airflow)
   ↓
2. Store Raw JSON (data/)
   ↓
3. Clean & Deduplicate (clean_data.py)
   ↓
4. Insert to Database (init_db.py)
   ↓
5. Cache & Analyze (Redis + Dashboard)
   ↓
6. Display Insights (Streamlit)
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file for custom configuration:

```bash
# Database
DATABASE_URL=postgresql://admin:password123@postgres:5432/hotel_insights
DB_HOST=localhost
DB_NAME=hotel_insights
DB_USER=admin
DB_PASS=password123
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Streamlit
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Customizing the Dashboard

Edit `app/dashboard.py` to:
- Modify metrics and visualizations
- Add custom filters
- Change color schemes
- Adjust sentiment analysis thresholds

## 📊 Key Metrics Explained

| Metric | Description |
|--------|-------------|
| **Điểm Agoda** | Average rating from Agoda platform |
| **Sentiment** | AI-calculated emotional score from review text |
| **Rủi Ro Ẩn** | Reviews with high scores but negative sentiment |
| **Tiêu Cực** | Percentage of negative reviews |

## 🔧 Troubleshooting

### Dashboard shows "Chưa có dữ liệu"

```bash
# Check database connection
docker exec -it hotel_db psql -U admin -d hotel_insights -c "SELECT COUNT(*) FROM reviews;"

# Reinitialize if needed
python3 database/update_from_cleaned.py
```

### Redis cache issues

```bash
# Clear Redis cache
docker exec hotel_cache redis-cli FLUSHALL

# Restart dashboard
docker-compose restart streamlit_app
```

### Airflow not scraping

```bash
# Check Airflow logs
docker logs airflow_scheduler

# Verify DAG is enabled in UI
# Navigate to http://localhost:8080
```

## 🐳 Docker Hub Deployment

### Build and Push

```bash
# Build the image
docker build -t yourusername/hotel-insights-dashboard:latest .

# Tag with version
docker tag yourusername/hotel-insights-dashboard:latest yourusername/hotel-insights-dashboard:v1.0.0

# Push to Docker Hub
docker login
docker push yourusername/hotel-insights-dashboard:latest
docker push yourusername/hotel-insights-dashboard:v1.0.0
```

### Pull and Run

```bash
docker pull yourusername/hotel-insights-dashboard:latest
docker-compose up -d
```

## 📁 Project Structure

```
Agentic_web_scraping/
├── app/
│   └── dashboard.py          # Main Streamlit dashboard
├── scraper/
│   ├── main.py              # Agoda scraper
│   └── utils.py             # Helper functions
├── database/
│   ├── init_db.py           # Database initialization
│   ├── clean_data.py        # Data cleaning
│   └── update_from_cleaned.py  # Database updater
├── airflow/
│   ├── dags/                # DAG definitions
│   └── logs/                # Airflow logs
├── data/                    # JSON data storage
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Multi-container setup
├── requirement.txt          # Python dependencies
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Agoda** for the review data
- **Streamlit** for the amazing dashboard framework
- **Airflow** for workflow orchestration
- **PostgreSQL** for robust data storage
- **Redis** for caching performance

## 📞 Support

For issues and questions:
- 📧 Email: your.email@example.com
- 🐛 GitHub Issues: [Create an issue](https://github.com/yourusername/Agentic_web_scraping/issues)

---

Made with ❤️ for better hotel management
