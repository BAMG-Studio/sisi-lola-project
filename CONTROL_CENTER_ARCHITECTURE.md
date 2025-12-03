# SISI LOLA CONTROL CENTER ARCHITECTURE
## Domain: https://sisilola.io & https://app.sisilola.io

**Created**: 2025-01-XX  
**Status**: Architecture Design Phase  
**Purpose**: Unified control center for all Sisi Lola operations

---

## SYSTEM OVERVIEW

### Primary Domain Structure
- **Public Site**: `https://sisilola.io` - Public-facing brand presence
- **Control Center**: `https://app.sisilola.io` - Internal operations dashboard
- **API Gateway**: `https://api.sisilola.io` - Backend services

### Core Capabilities
1. **Asset Management** - Control 200+ generated assets
2. **Content Pipeline** - Schedule, generate, and publish content
3. **Platform Integration** - Manage YouTube, Instagram, TikTok, etc.
4. **AI Model Control** - Monitor and trigger ML training pipelines
5. **Analytics Dashboard** - Real-time performance metrics
6. **User Management** - Role-based access control (RBAC)

---

## ROLE-BASED ACCESS CONTROL (RBAC)

### Role Hierarchy

#### 1. SUPER_ADMIN
- **Access Level**: Full system control
- **Permissions**:
  - User management (create, modify, delete roles)
  - System configuration
  - API key management
  - Database access
  - Billing and subscription management
  - Emergency shutdown controls

#### 2. CONTENT_DIRECTOR
- **Access Level**: Content strategy and approval
- **Permissions**:
  - Approve/reject content queue
  - Modify content calendar
  - Access analytics dashboards
  - Manage brand guidelines
  - Schedule posts across platforms

#### 3. TECHNICAL_OPERATOR
- **Access Level**: Technical operations
- **Permissions**:
  - Trigger ML training pipelines
  - Monitor API health
  - Access logs and error reports
  - Manage asset generation workflows
  - Configure integrations

#### 4. CREATIVE_PRODUCER
- **Access Level**: Asset creation and editing
- **Permissions**:
  - Upload/modify assets
  - Generate new content via AI tools
  - Access asset library
  - Preview content before publishing
  - Manage DNA consistency (avatar, voice, brand)

#### 5. SOCIAL_MEDIA_MANAGER
- **Access Level**: Platform management
- **Permissions**:
  - Post to social platforms
  - Respond to comments/messages
  - View engagement metrics
  - Schedule content
  - Access platform credentials (read-only)

#### 6. ANALYST
- **Access Level**: Read-only analytics
- **Permissions**:
  - View all dashboards
  - Export reports
  - Access historical data
  - No modification rights

#### 7. VIEWER
- **Access Level**: Limited preview
- **Permissions**:
  - View published content
  - Access public-facing dashboards
  - No backend access

### Role Combinations
Users can have multiple roles for hybrid access:
- `CONTENT_DIRECTOR + CREATIVE_PRODUCER`
- `TECHNICAL_OPERATOR + SUPER_ADMIN`
- `SOCIAL_MEDIA_MANAGER + ANALYST`

---

## AUTHENTICATION LAYERS

### Layer 1: Email/Password + 2FA
- Standard login with email verification
- TOTP-based 2FA (Google Authenticator, Authy)
- Password requirements: 12+ chars, special chars, numbers

### Layer 2: Role Verification
- JWT tokens with role claims
- Token expiration: 1 hour (access), 7 days (refresh)
- Role-based route protection

### Layer 3: IP Whitelisting (Optional)
- Restrict access to specific IP ranges
- Configurable per role
- Bypass for mobile app with device fingerprinting

### Layer 4: Action-Level Permissions
- Granular permissions per API endpoint
- Audit logging for sensitive actions
- Approval workflows for critical operations

---

## SYSTEM ARCHITECTURE

### Frontend (React/Next.js)
```
app.sisilola.io/
├── /login                    # Authentication
├── /dashboard                # Main control center
├── /assets                   # Asset library browser
│   ├── /avatar-dna
│   ├── /environments
│   ├── /media
│   └── /audio
├── /content                  # Content management
│   ├── /queue
│   ├── /calendar
│   └── /templates
├── /platforms                # Social media integrations
│   ├── /youtube
│   ├── /instagram
│   └── /tiktok
├── /ml-ops                   # ML training controls
│   ├── /models
│   ├── /training-jobs
│   └── /datasets
├── /analytics                # Performance metrics
├── /settings                 # System configuration
└── /admin                    # User & role management
```

### Backend (FastAPI - Existing)
```
api.sisilola.io/
├── /auth                     # Authentication endpoints
├── /assets                   # Asset CRUD operations
├── /content                  # Content generation & scheduling
├── /platforms                # Platform API integrations
├── /ml                       # ML pipeline triggers
├── /analytics                # Data aggregation
└── /admin                    # User management
```

### Database Schema (PostgreSQL)
```sql
-- Users & Authentication
users (id, email, password_hash, created_at, last_login)
roles (id, name, description, permissions_json)
user_roles (user_id, role_id, assigned_at, assigned_by)
sessions (id, user_id, token, expires_at, ip_address)

-- Assets
assets (id, category, subcategory, filename, url, metadata_json, status)
asset_versions (id, asset_id, version, created_by, created_at)

-- Content Pipeline
content_queue (id, title, script, status, scheduled_at, platform)
content_calendar (id, date, content_id, platform, posted_at)

-- Platform Integrations
platform_accounts (id, platform, handle, credentials_encrypted, status)
platform_posts (id, account_id, content_id, post_url, metrics_json)

-- ML Operations
training_jobs (id, model_type, status, started_at, completed_at, metrics)
model_registry (id, model_name, version, path, performance_metrics)

-- Analytics
daily_metrics (date, platform, views, engagement, revenue)
audit_logs (id, user_id, action, resource, timestamp, ip_address)
```

---

## MOBILE APP INTEGRATION

### React Native App Structure
```
SisiLolaControl/
├── screens/
│   ├── LoginScreen.js
│   ├── DashboardScreen.js
│   ├── AssetBrowserScreen.js
│   ├── ContentQueueScreen.js
│   ├── QuickPostScreen.js
│   └── AnalyticsScreen.js
├── components/
│   ├── RoleGate.js           # Permission wrapper
│   ├── AssetCard.js
│   └── MetricsWidget.js
├── services/
│   ├── AuthService.js
│   ├── APIService.js
│   └── NotificationService.js
└── navigation/
    └── RoleBasedNavigator.js
```

### Key Mobile Features
- **Push Notifications**: Content approval requests, system alerts
- **Quick Actions**: Emergency post, content approval, system status
- **Offline Mode**: View cached analytics and content
- **Biometric Auth**: Face ID / Fingerprint for quick access

---

## SECURITY MEASURES

### Data Protection
- All credentials encrypted at rest (AES-256)
- API keys stored in AWS Secrets Manager / HashiCorp Vault
- HTTPS only (TLS 1.3)
- CORS restricted to whitelisted domains

### Audit Trail
- All actions logged with user, timestamp, IP
- Immutable audit logs (append-only)
- 90-day retention for compliance

### Rate Limiting
- 100 requests/minute per user
- 1000 requests/minute per IP
- Exponential backoff for failed auth attempts

### Backup & Recovery
- Daily automated backups
- Point-in-time recovery (7 days)
- Disaster recovery plan with 4-hour RTO

---

## DEPLOYMENT STRATEGY

### Infrastructure (AWS)
- **Frontend**: Vercel / AWS Amplify
- **Backend**: AWS ECS (Fargate) or EC2 with Auto Scaling
- **Database**: AWS RDS (PostgreSQL) Multi-AZ
- **Storage**: AWS S3 for assets
- **CDN**: CloudFront for global delivery
- **Secrets**: AWS Secrets Manager
- **Monitoring**: CloudWatch + Datadog

### CI/CD Pipeline
```
GitHub → GitHub Actions → Docker Build → ECR → ECS Deploy
                ↓
         Run Tests (pytest, jest)
                ↓
         Security Scan (Snyk, Trivy)
                ↓
         Deploy to Staging → Manual Approval → Production
```

---

## INTEGRATION POINTS

### Existing Systems
1. **YouTube API** - Already configured
2. **HeyGen Avatar** - Video generation
3. **ElevenLabs** - Voice cloning
4. **KlingAI** - Video effects
5. **Perplexity** - Content research
6. **Cohere** - Language model
7. **N-ATLaS** - Nigerian language model

### New Integrations Needed
1. **Stripe** - Subscription management (if monetizing)
2. **SendGrid** - Email notifications
3. **Twilio** - SMS 2FA
4. **Sentry** - Error tracking
5. **Mixpanel** - User analytics

---

## IMPLEMENTATION PHASES

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up domain DNS (sisilola.io, app.sisilola.io, api.sisilola.io)
- [ ] Deploy backend API with auth endpoints
- [ ] Create database schema
- [ ] Implement JWT authentication
- [ ] Build basic login/dashboard UI

### Phase 2: Core Features (Weeks 3-4)
- [ ] Asset management system
- [ ] Content queue interface
- [ ] Platform integration dashboard
- [ ] Role-based access control
- [ ] User management admin panel

### Phase 3: Advanced Features (Weeks 5-6)
- [ ] ML pipeline controls
- [ ] Analytics dashboards
- [ ] Mobile app (React Native)
- [ ] Push notifications
- [ ] Audit logging

### Phase 4: Polish & Launch (Week 7-8)
- [ ] Security audit
- [ ] Performance optimization
- [ ] User acceptance testing
- [ ] Documentation
- [ ] Production deployment

---

## COST ESTIMATES (Monthly)

| Service | Tier | Cost |
|---------|------|------|
| AWS EC2 (t3.medium) | 2 instances | $60 |
| AWS RDS (db.t3.small) | Multi-AZ | $50 |
| AWS S3 + CloudFront | 500GB storage | $30 |
| Domain + SSL | sisilola.io | $15 |
| Vercel Pro | Frontend hosting | $20 |
| Monitoring (Datadog) | Basic | $15 |
| **Total** | | **~$190/month** |

---

## NEXT STEPS

1. **Immediate**: Review architecture with stakeholders
2. **Week 1**: Set up domains and SSL certificates
3. **Week 1**: Extend existing FastAPI with auth system
4. **Week 2**: Build React dashboard prototype
5. **Week 3**: Implement RBAC and user management
6. **Week 4**: Connect to existing asset generation pipelines

---

## CONTACT & SUPPORT

- **Technical Lead**: [Your Name]
- **Repository**: GitHub (private)
- **Documentation**: Confluence / Notion
- **Support**: support@sisilola.io
