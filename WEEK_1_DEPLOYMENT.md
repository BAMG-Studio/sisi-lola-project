# WEEK 1: API DEPLOYMENT & DOMAIN SETUP

## Day 1: Server Setup

### Option A: AWS EC2 (Recommended)
```bash
# Launch Ubuntu 22.04 t3.medium instance
# Security Group: Allow 22, 80, 443, 8000

# SSH into server
ssh -i your-key.pem ubuntu@YOUR_SERVER_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y
```

### Option B: DigitalOcean Droplet
```bash
# Create $12/month droplet (2GB RAM, Ubuntu 22.04)
# Same setup as AWS above
```

## Day 2: Deploy Backend

```bash
# Clone repository
cd /var/www
sudo git clone YOUR_REPO_URL sisilola-api
cd sisilola-api/sisi_lola_api

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_control_center.txt
pip install gunicorn psycopg2-binary

# Set up PostgreSQL
sudo -u postgres psql
```

```sql
CREATE DATABASE sisilola_control;
CREATE USER sisilola WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sisilola_control TO sisilola;
\q
```

```bash
# Create production .env
sudo nano .env
```

Add:
```bash
JWT_SECRET_KEY=generate-with-openssl-rand-base64-32
DATABASE_URL=postgresql://sisilola:your_secure_password@localhost/sisilola_control
DOMAIN_API=https://api.sisilola.io
CORS_ORIGINS=https://app.sisilola.io,https://www.sisilola.io

# Copy all other keys from your local .env
```

```bash
# Initialize database
python -c "from app.database import init_db; init_db()"

# Create admin user
cd ../..
python create_admin.py

# Test server
gunicorn app.main:app --bind 0.0.0.0:8000 --workers 4
```

## Day 3: Domain & SSL Setup

```bash
# Configure DNS (at your domain registrar)
# Add A records:
# api.sisilola.io -> YOUR_SERVER_IP
# app.sisilola.io -> YOUR_SERVER_IP
# sisilola.io -> YOUR_SERVER_IP
# www.sisilola.io -> YOUR_SERVER_IP

# Wait for DNS propagation (check with: dig api.sisilola.io)

# Get SSL certificates
sudo certbot certonly --nginx -d api.sisilola.io -d app.sisilola.io -d sisilola.io -d www.sisilola.io

# Configure Nginx
sudo nano /etc/nginx/sites-available/sisilola
```

```nginx
# API Backend
server {
    listen 80;
    server_name api.sisilola.io;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.sisilola.io;

    ssl_certificate /etc/letsencrypt/live/api.sisilola.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sisilola.io/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/sisilola /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Create systemd service
sudo nano /etc/systemd/system/sisilola-api.service
```

```ini
[Unit]
Description=Sisi Lola Control Center API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/sisilola-api/sisi_lola_api
Environment="PATH=/var/www/sisilola-api/sisi_lola_api/venv/bin"
ExecStart=/var/www/sisilola-api/sisi_lola_api/venv/bin/gunicorn app.main:app --bind 127.0.0.1:8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable sisilola-api
sudo systemctl start sisilola-api
sudo systemctl status sisilola-api
```

## Day 4-5: Testing & Monitoring

```bash
# Test API
curl https://api.sisilola.io/
curl -X POST https://api.sisilola.io/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sisilola.io","password":"SisiLola2025!"}'

# Set up monitoring
pip install sentry-sdk

# Add to app/main.py
import sentry_sdk
sentry_sdk.init(dsn="YOUR_SENTRY_DSN")

# Set up automated backups
sudo crontab -e
```

Add:
```bash
0 2 * * * pg_dump sisilola_control > /var/backups/sisilola_$(date +\%Y\%m\%d).sql
0 3 * * * find /var/backups -name "sisilola_*.sql" -mtime +7 -delete
```

## Week 1 Deliverables
- ✅ API running at https://api.sisilola.io
- ✅ PostgreSQL database configured
- ✅ SSL certificates installed
- ✅ Systemd service for auto-restart
- ✅ Daily backups configured
- ✅ Admin user created
