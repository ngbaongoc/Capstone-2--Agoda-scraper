# 🏨 Agoda Hotel Reviews Dashboard


A comprehensive hotel review analytics dashboard that scrapes Agoda reviews, performs AI sentiment analysis, and provides actionable insights for hotel management.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)





https://github.com/user-attachments/assets/8149b997-dfc6-4047-b0d8-952e942bf281

https://github.com/user-attachments/assets/55743856-1e71-47df-a2fa-c72c927d34be

https://github.com/user-attachments/assets/d52bde10-ee49-4f27-a93e-c707c541b05a








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
├── requirements.txt         # Python dependencies
└── README.md               # This file
```



## 🚀 Quick Start




### Prerequisites

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (Required for containerization)
- **[Git](https://git-scm.com/downloads)** (Version control)
- **[AgentQL API Key](https://docs.agentql.com/docs/introduction)** (Required for scraping)
- **Database Client** (Optional, e.g., [DBeaver](https://dbeaver.io/))

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
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium

# 4. Set up database
python3 database/init_db.py

# 5. Run the dashboard
streamlit run app/dashboard.py
```

### 🛑 Stop the Application

To stop all services:
```bash
docker-compose down

## 💻 System Requirements & Configuration

### 1. 🐳 Docker Installation
Required to run the application containers.
- **Windows/Mac**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Linux**: Install via terminal: `curl -fsSL https://get.docker.com | sh`
- **Verify**: Run `docker --version` and `docker-compose --version`.

### 2. 🐘 PostgreSQL Connection
Details to connect external tools (like DBeaver/TablePlus) to the database.

| Parameter | Value | Note |
|:---|:---|:---|
| **Host** | `localhost` | |
| **Port** | `5433` | ⚠️ Docker maps 5432 -> 5433 locally |
| **Database** | `hotel_insights` | |
| **Username** | `admin` | |
| **Password** | `password123` | |

### 3. 🤖 AgentQL Connection
Required for the AI scraper to function.
1. Get API Key from [AgentQL Dashboard](https://dev.agentql.com).
2. Create/Edit `.env` file in the project root.
3. Add variable: `AGENTQL_API_KEY=your_actual_key_here`

## 🛠️ Data Management


### 1. Manual Crawl (Background)
```bash
# Example: 5 hotels, 20 reviews each
python scraper/main.py --max-hotels 5 --reviews 20 --output data/manual_crawl.json
```

### 2. Ingest Data
To load any JSON file into the database:
```bash
# Replace 'your_file.json' with the file name inside 'data/' folder
docker exec hotel_dashboard python database/init_db.py --file /app/data/option_b_crawl.json
```






### Configuration
Edit `/airflow/dags/agoda_scraper.py` to configure target hotels and schedule.

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

### Environment Variables (.env)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_HOST` | Redis host address | localhost | Yes |
| `REDIS_PORT` | Redis port | 6379 | No |
| `POSTGRES_USER` | Database username | admin | No |
| `POSTGRES_PASSWORD` | Database password | password123 | No |
| `POSTGRES_DB` | Database name | hotel_insights | No |
| `STREAMLIT_PORT` | Dashboard port | 8501 | No |
| `AIRFLOW_PORT` | Airflow UI port | 8080 | No |
| `AGENTQL_API_KEY` | AgentQL API Key | - | **Yes (for Scraper)** |

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
```

### Airflow not scraping
```bash
# Check logs
docker logs airflow_scheduler
```


## 🙏 Acknowledgments

- **Agoda** for the review data
- **Streamlit** for the amazing dashboard framework
- **Airflow** for workflow orchestration
- **PostgreSQL** for robust data storage
- **Redis** for caching performance

## 📞 Support

For issues and questions:
- 📧 Email: ngobaongoc053@gmail.com
- 🐛 GitHub: https://github.com/ngbaongoc

---

Made with ❤️ for better hotel management
