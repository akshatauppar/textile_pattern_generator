# Deployment Guide

## Deployment Options

### Option 1: Local Development (Current Setup)

**Best for:** Testing, development, small personal use

```bash
python app.py
# Runs on http://localhost:5000
```

---

## Option 2: Gunicorn (Recommended for Single Server)

**Best for:** Production on single Linux server

### Install Gunicorn

```bash
pip install gunicorn
```

### Create systemd Service

Create `/etc/systemd/system/textile-api.service`:

```ini
[Unit]
Description=Textile Pattern Generator API
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/textile_generator_backend
Environment="PATH=/opt/textile_generator_backend/venv/bin"
ExecStart=/opt/textile_generator_backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable textile-api
sudo systemctl start textile-api

# Check status
sudo systemctl status textile-api
journalctl -u textile-api -f
```

---

## Option 3: Docker Compose (Recommended for Full Stack)

**Best for:** Easy deployment with PostgreSQL included

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: textile_db
    environment:
      POSTGRES_USER: textile_user
      POSTGRES_PASSWORD: textile_pass
      POSTGRES_DB: textile_generator
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U textile_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: textile_api
    environment:
      FLASK_ENV: production
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      DB_HOST: db
      DB_PORT: 5432
      DB_NAME: textile_generator
      DB_USER: textile_user
      DB_PASS: textile_pass
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ${MODEL_PATH}:/app/models
    depends_on:
      db:
        condition: service_healthy
    command: >
      sh -c "python init_db.py --init &&
             gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app"

  nginx:
    image: nginx:alpine
    container_name: textile_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./uploads:/app/uploads:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api

volumes:
  postgres_data:
```

### Create nginx.conf

```nginx
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:5000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    # Cache
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;

    server {
        listen 80;
        server_name _;

        client_max_body_size 50M;

        location / {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
        }

        # Cache images
        location ~ ^/api/images/ {
            proxy_pass http://api;
            proxy_cache api_cache;
            proxy_cache_valid 200 7d;
            proxy_cache_key "$scheme$request_method$host$request_uri";
            add_header X-Cache-Status $upstream_cache_status;
        }

        # Health check
        location /health {
            access_log off;
            proxy_pass http://api;
        }
    }

    # HTTPS configuration (if using SSL)
    # server {
    #     listen 443 ssl;
    #     server_name your-domain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     
    #     # ... same location blocks as above ...
    # }
}
```

### Deploy with Docker Compose

```bash
# Create .env file with secrets
echo "SECRET_KEY=<strong-random-key>" > .env
echo "JWT_SECRET_KEY=<strong-random-key>" >> .env
echo "MODEL_PATH=/path/to/models" >> .env

# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop
docker-compose down

# Backup database
docker-compose exec db pg_dump -U textile_user textile_generator > backup.sql
```

---

## Option 4: AWS Deployment

**Best for:** Scalable cloud deployment

### Using Elastic Beanstalk

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize EB Application:**
```bash
eb init -p python-3.9 textile-generator
```

3. **Create `.ebextensions/python.config`:**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: wsgi:app
    NumProcesses: 4
    NumThreads: 2
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    
packages:
  yum:
    postgresql-devel: []
```

4. **Deploy:**
```bash
eb create textile-api-env
eb deploy
```

---

## Option 5: Render (Simplest Cloud Option)

**Best for:** Quick cloud deployment

### Prepare for Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: textile-api
    env: python
    buildCommand: pip install -r requirements.txt && python init_db.py --init
    startCommand: gunicorn wsgi:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DB_HOST
        fromDatabase:
          name: textile-db
          property: host
      - key: DB_USER
        fromDatabase:
          name: textile-db
          property: user
      - key: DB_PASS
        fromDatabase:
          name: textile-db
          property: password
          
  - type: pserv
    name: textile-db
    dbName: textile_generator
    user: textile_user
```

2. Push to GitHub
3. Connect to Render.com
4. Deploy

---

## Security Checklist

- [ ] Change all secret keys
- [ ] Use HTTPS/SSL in production
- [ ] Enable CORS restrictions
- [ ] Set secure database credentials
- [ ] Implement rate limiting
- [ ] Add authentication for sensitive endpoints
- [ ] Regular backups
- [ ] Monitor logs for errors
- [ ] Update dependencies regularly
- [ ] Use environment variables for secrets

---

## Monitoring and Logging

### Application Logs

```bash
# Gunicorn
tail -f /var/log/textile-api.log

# Docker
docker-compose logs -f api

# Systemd
journalctl -u textile-api -f
```

### Performance Monitoring

```bash
# Monitor GPU usage
watch -n 1 nvidia-smi

# Monitor memory
top -p $(pgrep -f gunicorn)

# Database connections
psql -U textile_user -c "SELECT * FROM pg_stat_activity;"
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Multiple Gunicorn Workers:**
```bash
gunicorn --workers 8 --worker-class sync wsgi:app
```

2. **Load Balancer (Nginx):**
```nginx
upstream api {
    server api1:5000;
    server api2:5000;
    server api3:5000;
}
```

3. **Database Connection Pool:**
```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
}
```

### Asynchronous Generation Queue

For high traffic, use Celery + Redis:

```bash
pip install celery redis
```

```python
# app/utils/celery_tasks.py
from celery import Celery
celery = Celery('textile')

@celery.task
def generate_pattern_task(generation_id, prompt, style, ...):
    # Same as _process_generation
    pass
```

---

## Backup Strategy

### Automated Database Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/textile"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump -U textile_user textile_generator | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

Schedule with cron:
```bash
0 2 * * * /path/to/backup.sh
```

---

## Maintenance

### Database Maintenance

```bash
# Vacuum (optimize)
vacuumdb -U textile_user textile_generator

# Analyze (update statistics)
analyzedb -U textile_user textile_generator

# Reindex
reindexdb -U textile_user textile_generator
```

### Clean Old Generations

```python
# Delete generations older than 30 days
from app import create_app
from app.models import db, Generation
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    cutoff = datetime.utcnow() - timedelta(days=30)
    old_gens = Generation.query.filter(Generation.created_at < cutoff).all()
    for gen in old_gens:
        if gen.image_path:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], gen.image_path))
        db.session.delete(gen)
    db.session.commit()
```

---

## Disaster Recovery

### Restore from Backup

```bash
# Restore database
psql -U textile_user textile_generator < backup.sql

# Restore uploads (if using cloud storage)
aws s3 sync s3://textile-backups/uploads ./uploads
```

### High Availability Setup

1. **Primary + Standby Database:** PostgreSQL replication
2. **Multiple API servers:** Behind load balancer
3. **Cloud storage:** S3 for image backups
4. **CDN:** CloudFront for image delivery

---

## Support & References

- [Flask Deployment](https://flask.palletsprojects.com/deployment/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [PostgreSQL Backup/Restore](https://www.postgresql.org/docs/current/backup.html)
- [Docker Documentation](https://docs.docker.com/)
- [AWS Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/)
