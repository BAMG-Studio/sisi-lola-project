# SISI LOLA CONTROL CENTER - QUICK START

## What You're Building

A unified control center at **https://app.sisilola.io** that manages:
- 200+ AI-generated assets
- Content scheduling across YouTube, Instagram, TikTok
- ML training pipelines
- Role-based team access
- Real-time analytics

## 5-Minute Setup

### 1. Add JWT Secret to .env

```bash
cd sisi_lola_api
echo JWT_SECRET_KEY=sisi-lola-super-secret-key-2025-change-in-production >> .env
```

### 2. Install Dependencies

```bash
pip install python-jose[cryptography] passlib[bcrypt] sqlalchemy python-multipart
```

### 3. Update main.py

```bash
copy app\main.py app\main_backup.py
copy app\main_updated.py app\main.py
```

### 4. Create Admin User

```bash
cd ..
python create_admin.py
```

Output:
```
✓ Admin user created: admin@sisilola.io
✓ Password: SisiLola2025!
✓ Role: SUPER_ADMIN
```

### 5. Start Server

```bash
cd sisi_lola_api
uvicorn app.main:app --reload
```

### 6. Test Login

Open browser: http://localhost:8000/docs

Try the `/api/v2/auth/login` endpoint:
```json
{
  "email": "admin@sisilola.io",
  "password": "SisiLola2025!"
}
```

You'll get back:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

## What's Available Now

### API Endpoints (http://localhost:8000/docs)

**Authentication** (`/api/v2/auth`)
- POST `/login` - Get access tokens
- GET `/me` - Current user info
- GET `/users` - List all users (admin only)

**Assets** (`/api/v2/control/assets`)
- GET `/assets` - List all assets
- POST `/assets` - Upload new asset
- PUT `/assets/{id}/status` - Update status

**Content** (`/api/v2/control/content`)
- GET `/queue` - View content queue
- POST `/queue` - Add content
- PUT `/{id}/approve` - Approve content
- POST `/{id}/publish` - Publish to platform

**ML Operations** (`/api/v2/control/ml`)
- GET `/jobs` - Training job status
- POST `/train` - Trigger training

**Analytics** (`/api/v2/control/analytics`)
- GET `/dashboard` - Dashboard metrics

## User Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| SUPER_ADMIN | Everything | You (system owner) |
| CONTENT_DIRECTOR | Approve content, view analytics | Content strategy |
| TECHNICAL_OPERATOR | ML training, system logs | Technical operations |
| CREATIVE_PRODUCER | Create/edit assets | Content creation |
| SOCIAL_MEDIA_MANAGER | Post to platforms | Social media |
| ANALYST | View-only analytics | Data analysis |
| VIEWER | Limited preview | Stakeholders |

## Create More Users

```bash
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "creative@sisilola.io",
    "password": "SecurePass123!",
    "roles": ["CREATIVE_PRODUCER"]
  }'
```

## Next Steps

### Option A: Build Web Dashboard (React)
See `IMPLEMENTATION_GUIDE_CONTROL_CENTER.md` → Frontend Integration

### Option B: Build Mobile App (React Native)
See `IMPLEMENTATION_GUIDE_CONTROL_CENTER.md` → Mobile App Integration

### Option C: Connect to Domain
1. Point `api.sisilola.io` to your server
2. Set up SSL with Let's Encrypt
3. Configure Nginx reverse proxy
4. Update CORS_ORIGINS in .env

## Testing Permissions

```bash
# Login as admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sisilola.io","password":"SisiLola2025!"}' \
  | jq -r .access_token)

# Use token to access protected routes
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v2/control/analytics/dashboard

# Create an asset
curl -X POST http://localhost:8000/api/v2/control/assets \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "AVATAR_DNA",
    "subcategory": "Reference_Sheets",
    "filename": "sisi_lola_ref_001.png",
    "url": "https://storage.sisilola.io/assets/ref_001.png",
    "metadata": {"resolution": "4K", "style": "photorealistic"}
  }'
```

## Architecture Overview

```
sisilola.io (Public Site)
    ↓
app.sisilola.io (Control Center Dashboard)
    ↓
api.sisilola.io (This FastAPI Backend)
    ↓
    ├── Authentication (JWT + RBAC)
    ├── Asset Management
    ├── Content Pipeline
    ├── ML Operations
    ├── Platform Integrations
    └── Analytics
```

## Files Created

```
Sisi_Lola/
├── CONTROL_CENTER_ARCHITECTURE.md      # Full system design
├── IMPLEMENTATION_GUIDE_CONTROL_CENTER.md  # Detailed guide
├── QUICK_START_CONTROL_CENTER.md       # This file
├── create_admin.py                     # Admin user setup
└── sisi_lola_api/
    ├── app/
    │   ├── auth.py                     # JWT + RBAC logic
    │   ├── database.py                 # SQLAlchemy models
    │   ├── main_updated.py             # Updated FastAPI app
    │   └── routers/
    │       ├── auth_router.py          # Auth endpoints
    │       └── control_center_router.py # Control endpoints
    ├── .env.example                    # Config template
    └── requirements_control_center.txt # Dependencies
```

## Troubleshooting

**"Module not found" errors**
```bash
pip install -r requirements_control_center.txt
```

**"Database locked" error**
```bash
# SQLite limitation - switch to PostgreSQL for production
# Or restart the server
```

**"Invalid token" error**
```bash
# Token expired (1 hour lifetime)
# Login again to get new token
```

**Can't access from mobile/other computer**
```bash
# Change --host to 0.0.0.0
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Checklist

Before going live:
- [ ] Change JWT_SECRET_KEY to random 32+ char string
- [ ] Switch DATABASE_URL to PostgreSQL
- [ ] Set up HTTPS with SSL certificate
- [ ] Configure proper CORS_ORIGINS
- [ ] Change admin password
- [ ] Enable rate limiting
- [ ] Set up monitoring (Sentry, Datadog)
- [ ] Configure automated backups
- [ ] Review all user permissions
- [ ] Load test the API

## Support

- **Full Documentation**: `CONTROL_CENTER_ARCHITECTURE.md`
- **Implementation Guide**: `IMPLEMENTATION_GUIDE_CONTROL_CENTER.md`
- **Project Overview**: `README.md`

---

**Status**: Ready to deploy  
**Estimated Setup Time**: 5 minutes  
**Next Milestone**: Build frontend dashboard
