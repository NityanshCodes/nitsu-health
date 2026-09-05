# Production Deployment Guide

## Pre-Deployment Checklist

### Environment Setup

- [ ] All required environment variables are set (see `.env.example`)
- [ ] Database credentials are secure and not committed to version control
- [ ] JWT secret key is a cryptographically random string (min 32 chars)
- [ ] OpenAI API key (if using OpenAI provider) is secure
- [ ] CORS origins are restricted to your domain(s)
- [ ] Debug mode is disabled in production (`DEBUG=false`)

### Security Review

- [ ] All secrets are stored in environment variables, not source code
- [ ] `.env` and `.env.*.local` files are in `.gitignore`
- [ ] JWT token expiry is set appropriately (default 60 minutes)
- [ ] Password validation is enforced (8+ chars, uppercase, lowercase, digit)
- [ ] Database backups are automated
- [ ] HTTPS is enforced for all endpoints
- [ ] Rate limiting is configured (recommended via nginx or load balancer)

### Backend Verification

```bash
# Run the full test suite
cd backend
PYTHONPATH=. python -m pytest tests -q
# Expected: 34 passed

# Check for security issues in dependencies
pip-audit

# Verify configuration loads correctly
python -c "from app.core.config import settings; print(f'Environment: {settings.environment}, Debug: {settings.debug}')"
```

### Frontend Verification

```bash
# Build production bundle
cd frontend
npm run build

# Verify bundle size and integrity
ls -lh dist/

# Check for any hardcoded secrets or API keys
grep -r "VITE_OPENAI_API_KEY\|VITE_JWT_SECRET" src/
# Should return nothing - secrets must NOT be in frontend
```

---

## Deployment Steps

### 1. Backend Deployment

#### Using Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t nitsu-health-backend .
docker run -e DATABASE_URL="postgresql://..." \
           -e JWT_SECRET_KEY="..." \
           -e OPENAI_API_KEY="..." \
           -e AI_PROVIDER="openai" \
           -p 8000:8000 \
           nitsu-health-backend
```

#### Using systemd (for VPS)

Create `/etc/systemd/system/nitsu-health.service`:

```ini
[Unit]
Description=NITSU Health API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/nitsu-health/backend
Environment="PATH=/opt/nitsu-health/.venv/bin"
Environment="DATABASE_URL=sqlite:///./nitsu_health.db"
Environment="JWT_SECRET_KEY=your-secret-key"
Environment="AI_PROVIDER=development"
Environment="ENVIRONMENT=production"
Environment="DEBUG=false"

ExecStart=/opt/nitsu-health/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable nitsu-health
sudo systemctl start nitsu-health
sudo systemctl status nitsu-health
```

### 2. Frontend Deployment

#### Using Nginx

```nginx
# /etc/nginx/sites-available/nitsu-health
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Serve frontend
    root /opt/nitsu-health/frontend/dist;
    index index.html;

    # React Router - route all non-asset requests to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API calls to backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Using Vercel/Netlify

1. Push frontend to GitHub
2. Connect repository to Vercel/Netlify
3. Set build command: `npm run build`
4. Set output directory: `dist`
5. Set environment variable: `VITE_API_URL=https://api.yourdomain.com`
6. Deploy

### 3. Database Setup

#### SQLite (Development/Small Scale)

Default configuration - file-based at `./nitsu_health.db`

Backup:

```bash
cp nitsu_health.db nitsu_health.db.backup
```

#### PostgreSQL (Production/Scale)

Install:

```bash
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb nitsu_health
sudo -u postgres createuser nitsu_health_user
```

Set password:

```bash
sudo -u postgres psql
ALTER USER nitsu_health_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE nitsu_health TO nitsu_health_user;
\q
```

Update connection string:

```
DATABASE_URL=postgresql://nitsu_health_user:your-secure-password@localhost:5432/nitsu_health
```

Backup:

```bash
pg_dump nitsu_health > nitsu_health.sql
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/api/health

# AI health
curl -H "Authorization: Bearer YOUR_TOKEN" https://yourdomain.com/api/ai/health
```

### Logs

**Backend:**

```bash
# If using systemd
journalctl -u nitsu-health -f

# If using Docker
docker logs -f nitsu-health-backend
```

**Frontend:**
Check browser console and network tab for any errors.

### Performance

Monitor:

- Response times for `/auth/login` and `/dashboard/summary`
- Database query performance (slow logs)
- Frontend bundle size (should stay ~300KB gzipped)
- Token generation/validation latency

### Database Maintenance

```bash
# SQLite
VACUUM;  # Reclaim disk space
ANALYZE;  # Update statistics

# PostgreSQL
VACUUM ANALYZE;
REINDEX DATABASE nitsu_health;
```

---

## Rollback Procedure

### Backend Rollback

```bash
# If using Docker
docker pull nitsu-health-backend:v1.0.0
docker stop nitsu-health-backend
docker run -d --name nitsu-health-backend nitsu-health-backend:v1.0.0

# If using systemd
git checkout v1.0.0
sudo systemctl restart nitsu-health
```

### Database Rollback

```bash
# Restore from backup
sqlite3 nitsu_health.db < nitsu_health.sql

# Or PostgreSQL
psql nitsu_health < nitsu_health.sql
```

### Frontend Rollback

```bash
# Revert to previous commit
git checkout v1.0.0
npm run build
# Deploy to your hosting
```

---

## Troubleshooting

### Backend won't start

```bash
# Check environment variables
env | grep DATABASE_URL JWT_SECRET_KEY

# Check database file permissions
ls -la nitsu_health.db

# Run with verbose output
python -m pytest tests -v
```

### Frontend won't connect to backend

```bash
# Check CORS configuration
curl -H "Origin: https://yourdomain.com" http://localhost:8000/health

# Verify API URL
# In browser console: console.log(import.meta.env.VITE_API_URL)

# Check backend is running
curl http://localhost:8000/health
```

### Users can't login

```bash
# Verify JWT secret is set
echo $JWT_SECRET_KEY

# Check user exists in database
sqlite3 nitsu_health.db "SELECT id, email FROM users WHERE email='user@example.com';"

# Verify token can be created
python -c "from app.services.auth_service import create_access_token; print('OK')"
```

### Database locked errors

```bash
# SQLite - restart the application
sudo systemctl restart nitsu-health

# Check for stuck connections
sqlite3 nitsu_health.db "PRAGMA database_list;"
```

---

## Security Hardening

### Additional Recommendations

1. **Rate Limiting** - Add via nginx or implement in-app:

```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

2. **HTTPS/TLS** - Use Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
```

3. **Secrets Manager** - Use AWS Secrets Manager, HashiCorp Vault, or similar in production

4. **Audit Logging** - Log all auth events:

```python
logger.info(f"Login successful for user {user.id}")
logger.warning(f"Failed login attempt for {email}")
```

5. **DDoS Protection** - Use Cloudflare or AWS WAF

6. **Database Encryption** - Use PostgreSQL extensions or full-disk encryption

---

## Performance Tuning

### Backend

- Pool database connections (SQLAlchemy pool_size, pool_recycle)
- Enable uvicorn workers: `--workers 4`
- Use caching for health endpoints (Redis optional)

### Frontend

- Enable gzip compression in nginx
- Cache-bust assets with content hashing (already done by Vite)
- Lazy-load routes and components

### Database

- Add indexes on frequently queried columns (user_id, created_at)
- Archive old records to cold storage
- Use connection pooling
