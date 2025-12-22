# 🚀 Deployment Guide

This guide will walk you through deploying the Hotel Insights Dashboard to Docker Hub and running it in production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Building the Image](#building-the-image)
3. [Pushing to Docker Hub](#pushing-to-docker-hub)
4. [Deployment Options](#deployment-options)
5. [Production Checklist](#production-checklist)

## Prerequisites

- Docker installed and running
- Docker Hub account ([Sign up here](https://hub.docker.com/signup))
- Git installed

## Building the Image

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your Docker Hub username
nano .env  # or use your preferred editor

# Set DOCKER_USERNAME=your-dockerhub-username
# Set VERSION=v1.0.0 (or your version number)
```

### 2. Build the Docker Image

```bash
# Build with tag
docker build -t yourusername/hotel-insights-dashboard:latest .

# Build with version tag
docker build -t yourusername/hotel-insights-dashboard:v1.0.0 .

# Using docker-compose (recommended)
docker-compose build
```

### 3. Test Locally

```bash
# Test the image locally
docker run -p 8501:8501 \
  -e DATABASE_URL=postgresql://admin:password123@localhost:5432/hotel_insights \
  -e REDIS_HOST=localhost \
  yourusername/hotel-insights-dashboard:latest

# Or use docker-compose
docker-compose up
```

## Pushing to Docker Hub

### 1. Login to Docker Hub

```bash
docker login
# Enter your Docker Hub username and password
```

### 2. Tag Your Image

```bash
# Tag with latest
docker tag hotel-insights-dashboard:latest yourusername/hotel-insights-dashboard:latest

# Tag with version
docker tag hotel-insights-dashboard:latest yourusername/hotel-insights-dashboard:v1.0.0
```

### 3. Push to Docker Hub

```bash
# Push latest version
docker push yourusername/hotel-insights-dashboard:latest

# Push specific version
docker push yourusername/hotel-insights-dashboard:v1.0.0
```

### 4. Verify Push

Visit `https://hub.docker.com/r/yourusername/hotel-insights-dashboard` to see your image.

## Deployment Options

### Option 1: Docker Compose (Recommended for Full Stack)

```bash
# On your server
git clone https://github.com/yourusername/Agentic_web_scraping.git
cd Agentic_web_scraping

# Configure environment
cp .env.example .env
nano .env  # Edit as needed

# Start all services
docker-compose up -d

# Initialize database
docker exec hotel_dashboard python3 database/init_db.py

# Check logs
docker-compose logs -f streamlit_app
```

### Option 2: Docker Run (Dashboard Only)

```bash
# Pull the image
docker pull yourusername/hotel-insights-dashboard:latest

# Run with external database
docker run -d \
  --name hotel-dashboard \
  -p 8501:8501 \
  -e DATABASE_URL=postgresql://user:pass@your-db-host:5432/dbname \
  -e REDIS_HOST=your-redis-host \
  yourusername/hotel-insights-dashboard:latest
```

### Option 3: Cloud Platforms

#### AWS ECS

```bash
# Create task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster your-cluster \
  --service-name hotel-dashboard \
  --task-definition hotel-dashboard:1 \
  --desired-count 1
```

#### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy hotel-dashboard \
  --image yourusername/hotel-insights-dashboard:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=your-db-url,REDIS_HOST=your-redis
```

#### Azure Container Instances

```bash
az container create \
  --resource-group your-rg \
  --name hotel-dashboard \
  --image yourusername/hotel-insights-dashboard:latest \
  --dns-name-label hotel-dashboard \
  --ports 8501 \
  --environment-variables \
    DATABASE_URL=your-db-url \
    REDIS_HOST=your-redis
```

## Production Checklist

### Security ✅

- [ ] Change default database credentials
- [ ] Use strong passwords for all services
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Use secrets management (not environment variables in production)
- [ ] Regular security updates

```bash
# Generate strong passwords
openssl rand -base64 32  # For database
openssl rand -base64 32  # For Airflow
```

### Database 💾

- [ ] Set up automated backups
- [ ] Configure replication (if needed)
- [ ] Monitor disk space
- [ ] Set up connection pooling
- [ ] Configure proper indexes

```bash
# Backup database
docker exec hotel_db pg_dump -U admin hotel_insights > backup_$(date +%Y%m%d).sql

# Restore database
docker exec -i hotel_db psql -U admin hotel_insights < backup_20251220.sql
```

### Monitoring 📊

- [ ] Set up logging (ELK stack or similar)
- [ ] Configure alerts for errors
- [ ] Monitor resource usage
- [ ] Set up uptime monitoring
- [ ] Track application metrics

```bash
# View logs
docker-compose logs -f --tail=100

# Monitor resources
docker stats
```

### Performance 🚀

- [ ] Configure Redis cache TTL
- [ ] Set up CDN for static assets (if needed)
- [ ] Enable gzip compression
- [ ] Configure connection limits
- [ ] Set up load balancing (for multiple instances)

### Maintenance 🔧

- [ ] Document deployment process
- [ ] Set up CI/CD pipeline
- [ ] Plan for zero-downtime deployments
- [ ] Create rollback procedure
- [ ] Schedule regular updates

```bash
# Update to new version
docker-compose pull
docker-compose up -d

# Rollback if needed
docker-compose down
docker tag yourusername/hotel-insights-dashboard:v1.0.0 yourusername/hotel-insights-dashboard:latest
docker-compose up -d
```

## Environment Variables Reference

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

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs hotel_dashboard

# Check health status
docker inspect --format='{{.State.Health.Status}}' hotel_dashboard

# Restart container
docker restart hotel_dashboard
```

### Database connection issues

```bash
# Test database connectivity from container
docker exec hotel_dashboard psql $DATABASE_URL -c "SELECT 1"

# Check if database is running
docker ps | grep postgres
```

### Memory or CPU issues

```bash
# Set resource limits in docker-compose.yml
services:
  streamlit_app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Support

For deployment issues:
- 📧 Email: support@yourcompany.com
- 🐛 GitHub Issues: [Report a bug](https://github.com/yourusername/Agentic_web_scraping/issues)
- 💬 Discord: [Join our community](https://discord.gg/yourserver)

---

**Good luck with your deployment!** 🚀
