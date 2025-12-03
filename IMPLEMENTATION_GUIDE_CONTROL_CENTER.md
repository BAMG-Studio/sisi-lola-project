# SISI LOLA CONTROL CENTER - IMPLEMENTATION GUIDE

## Quick Start Implementation

### Step 1: Update Environment Variables

Add to `.env`:
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
DATABASE_URL=sqlite:///./sisi_lola_control.db  # Use PostgreSQL in production

# Domain Configuration
DOMAIN_PUBLIC=https://sisilola.io
DOMAIN_APP=https://app.sisilola.io
DOMAIN_API=https://api.sisilola.io
```

### Step 2: Install Dependencies

```bash
cd sisi_lola_api
pip install -r requirements_control_center.txt
```

### Step 3: Replace main.py

```bash
# Backup current main.py
copy app\main.py app\main_backup.py

# Use updated version
copy app\main_updated.py app\main.py
```

### Step 4: Initialize Database

```bash
python -c "from app.database import init_db; init_db()"
```

### Step 5: Create First Admin User

```python
# create_admin.py
from app.database import SessionLocal, UserModel, RoleModel
from app.auth import get_password_hash

db = SessionLocal()

# Create admin user
admin = UserModel(
    email="admin@sisilola.io",
    password_hash=get_password_hash("ChangeThisPassword123!")
)
db.add(admin)
db.commit()
db.refresh(admin)

# Assign SUPER_ADMIN role
role = db.query(RoleModel).filter(RoleModel.name == "SUPER_ADMIN").first()
admin.roles.append(role)
db.commit()

print(f"Admin user created: {admin.email}")
db.close()
```

Run: `python create_admin.py`

### Step 6: Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Test Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sisilola.io","password":"ChangeThisPassword123!"}'

# Response will include access_token and refresh_token
```

---

## API Endpoints Reference

### Authentication (`/api/v2/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Create new user | No (add SUPER_ADMIN check in production) |
| POST | `/login` | Login and get tokens | No |
| POST | `/refresh` | Refresh access token | No |
| GET | `/me` | Get current user info | Yes |
| GET | `/users` | List all users | SUPER_ADMIN |
| PUT | `/users/{id}/roles` | Update user roles | SUPER_ADMIN |
| DELETE | `/users/{id}` | Delete user | SUPER_ADMIN |

### Control Center (`/api/v2/control`)

#### Assets
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/assets` | List assets | assets:read |
| POST | `/assets` | Create asset | assets:write |
| PUT | `/assets/{id}/status` | Update status | assets:write |

#### Content Pipeline
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/content/queue` | Get content queue | content:read |
| POST | `/content/queue` | Add to queue | content:write |
| PUT | `/content/{id}/approve` | Approve content | content:approve |
| POST | `/content/{id}/publish` | Publish content | platforms:write |

#### ML Operations
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/ml/jobs` | List training jobs | ml:read |
| POST | `/ml/train` | Trigger training | ml:execute |

#### Platforms
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/platforms` | List platforms | platforms:read |
| POST | `/platforms/sync/{id}` | Sync platform | platforms:write |

#### Analytics
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| GET | `/analytics/dashboard` | Dashboard metrics | analytics:read |

---

## Frontend Integration Example (React)

### 1. Auth Service

```javascript
// services/authService.js
const API_BASE = 'https://api.sisilola.io/api/v2';

export const authService = {
  async login(email, password) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  },

  async getCurrentUser() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE}/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};
```

### 2. Protected Route Component

```javascript
// components/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  if (requiredRole && !user.roles.includes(requiredRole)) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};
```

### 3. Dashboard Component

```javascript
// pages/Dashboard.jsx
import { useEffect, useState } from 'react';
import { apiClient } from '../services/apiClient';

export const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    apiClient.get('/control/analytics/dashboard')
      .then(data => setMetrics(data));
  }, []);

  return (
    <div className="dashboard">
      <h1>Sisi Lola Control Center</h1>
      {metrics && (
        <div className="metrics-grid">
          <MetricCard title="Total Assets" value={metrics.assets.total} />
          <MetricCard title="Queue Size" value={metrics.content.queue_size} />
          <MetricCard title="Active Jobs" value={metrics.ml.active_jobs} />
        </div>
      )}
    </div>
  );
};
```

---

## Mobile App Integration (React Native)

### Setup

```bash
npx react-native init SisiLolaControl
cd SisiLolaControl
npm install @react-navigation/native @react-navigation/stack
npm install axios react-native-keychain
```

### Auth Context

```javascript
// context/AuthContext.js
import React, { createContext, useState, useEffect } from 'react';
import * as Keychain from 'react-native-keychain';
import axios from 'axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const credentials = await Keychain.getGenericPassword();
      if (credentials) {
        const response = await axios.get('https://api.sisilola.io/api/v2/auth/me', {
          headers: { Authorization: `Bearer ${credentials.password}` }
        });
        setUser(response.data);
      }
    } catch (error) {
      console.error('Failed to load user', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post('https://api.sisilola.io/api/v2/auth/login', {
      email, password
    });
    await Keychain.setGenericPassword('token', response.data.access_token);
    await loadUser();
  };

  const logout = async () => {
    await Keychain.resetGenericPassword();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

## Domain Setup

### DNS Configuration

Point these domains to your server:

```
A     sisilola.io              -> YOUR_SERVER_IP
A     app.sisilola.io          -> YOUR_SERVER_IP
A     api.sisilola.io          -> YOUR_SERVER_IP
CNAME www.sisilola.io          -> sisilola.io
```

### SSL Certificates (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d sisilola.io -d www.sisilola.io -d app.sisilola.io -d api.sisilola.io
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/sisilola.io

# API Backend
server {
    listen 443 ssl http2;
    server_name api.sisilola.io;

    ssl_certificate /etc/letsencrypt/live/sisilola.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sisilola.io/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# Frontend App
server {
    listen 443 ssl http2;
    server_name app.sisilola.io;

    ssl_certificate /etc/letsencrypt/live/sisilola.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sisilola.io/privkey.pem;

    root /var/www/sisilola-app/build;
    index index.html;

    location / {
        try_files $uri /index.html;
    }
}

# Public Site
server {
    listen 443 ssl http2;
    server_name sisilola.io www.sisilola.io;

    ssl_certificate /etc/letsencrypt/live/sisilola.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sisilola.io/privkey.pem;

    root /var/www/sisilola-public;
    index index.html;
}
```

---

## Production Deployment Checklist

- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Switch to PostgreSQL database
- [ ] Enable HTTPS only
- [ ] Set up proper CORS origins
- [ ] Configure rate limiting
- [ ] Set up monitoring (Datadog, Sentry)
- [ ] Configure automated backups
- [ ] Set up CI/CD pipeline
- [ ] Enable audit logging
- [ ] Configure IP whitelisting for admin routes
- [ ] Set up 2FA for SUPER_ADMIN accounts
- [ ] Review and test all permissions
- [ ] Load test the API
- [ ] Set up CDN for assets
- [ ] Configure email notifications

---

## Testing the System

### Create Test Users

```python
# test_users.py
from app.database import SessionLocal, UserModel, RoleModel
from app.auth import get_password_hash

db = SessionLocal()

users = [
    ("director@sisilola.io", "CONTENT_DIRECTOR"),
    ("tech@sisilola.io", "TECHNICAL_OPERATOR"),
    ("creative@sisilola.io", "CREATIVE_PRODUCER"),
    ("social@sisilola.io", "SOCIAL_MEDIA_MANAGER"),
]

for email, role_name in users:
    user = UserModel(email=email, password_hash=get_password_hash("Test123!"))
    db.add(user)
    db.commit()
    db.refresh(user)
    
    role = db.query(RoleModel).filter(RoleModel.name == role_name).first()
    user.roles.append(role)
    db.commit()
    print(f"Created: {email} with role {role_name}")

db.close()
```

### Test Permission System

```bash
# Login as content director
TOKEN=$(curl -s -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"director@sisilola.io","password":"Test123!"}' | jq -r .access_token)

# Should work - content:read permission
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v2/control/content/queue

# Should fail - no ml:execute permission
curl -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v2/control/ml/train
```

---

## Next Steps

1. **Week 1**: Deploy backend API with authentication
2. **Week 2**: Build React dashboard for app.sisilola.io
3. **Week 3**: Integrate with existing asset generation pipelines
4. **Week 4**: Build mobile app
5. **Week 5**: Add analytics and monitoring
6. **Week 6**: User acceptance testing
7. **Week 7**: Production launch

---

## Support

- **Documentation**: See CONTROL_CENTER_ARCHITECTURE.md
- **Issues**: Create GitHub issue
- **Contact**: tech@sisilola.io
