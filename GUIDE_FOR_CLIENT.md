# Hướng Dẫn Cài Đặt & Chạy Dashboard (v2)

Tài liệu này hướng dẫn cách chạy ứng dụng từ Docker Hub và nạp dữ liệu từ file `data.json`.

## 1. Tải Image (Tùy chọn)

Để đảm bảo bạn có phiên bản mới nhất, hãy chạy lệnh sau:

```bash
docker pull longnt70/agoda-scraper:v2
```

## 2. Chuẩn Bị File

Bạn cần có 2 file sau trong cùng một thư mục (ví dụ: `my-project/`):

1.  **`docker-compose.yml`**: (Nội dung bên dưới)
2.  **`data.json`**: File dữ liệu do người gửi cung cấp.

### Nội dung file `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: ankane/pgvector:latest
    container_name: hotel_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password123
      POSTGRES_DB: hotel_insights
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d hotel_insights"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: hotel_cache
    ports:
      - "6379:6379"

  dashboard:
    image: longnt70/agoda-scraper:v2
    container_name: hotel_dashboard
    ports:
      - "8501:8501"
    environment:
      DATABASE_URL: postgresql://admin:password123@postgres:5432/hotel_insights
      REDIS_HOST: redis
      REDIS_PORT: 6379
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres-data:
```

## 3. Chạy Ứng Dụng

Mở Terminal (hoặc CMD/PowerShell) tại thư mục chứa file, chạy lệnh:

```bash
docker-compose up -d
```

Đợi khoảng 1-2 phút để các service (Database, Dashboard) khởi động hoàn toàn.

## 4. Nạp Dữ Liệu (Quan Trọng)

Sau khi chạy xong, database vẫn đang trống. Bạn cần nạp file `data.json` vào hệ thống.

Chạy lần lượt 2 lệnh sau:

**Bước 1: Copy file data vào trong container**
```bash
docker cp data.json hotel_dashboard:/app/data/data.json
```

**Bước 2: Chạy lệnh nạp dữ liệu**
```bash
docker exec -it hotel_dashboard python database/init_db.py --file /app/data/data.json
```

*Nếu thấy thông báo `Data upserted successfully` nghĩa là đã thành công.*

## 5. Truy Cập

Mở trình duyệt và vào địa chỉ:
👉 **http://localhost:8501**
