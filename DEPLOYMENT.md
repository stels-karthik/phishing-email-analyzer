# Production Deployment Guide

This guide covers deploying the Phishing Email Analyzer to production using free/low-cost hosting options.

## Architecture Overview

```
Frontend (Vercel/Netlify) → API (Render/Railway) → Groq API (Free Tier)
                                    ↓
                            Threat Intel APIs (Free)
```

## Table of Contents
1. [Quick Deploy (Recommended)](#quick-deploy-recommended)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Custom Domain Setup](#custom-domain-setup)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Quick Deploy (Recommended)

### Prerequisites
- GitHub account (done ✅)
- Groq API key (done ✅)
- 10-15 minutes

### Option 1: Render + Vercel (Easiest)

**Step 1: Deploy Backend to Render**
1. Go to https://render.com and sign in with GitHub
2. Click "New +" → "Web Service"
3. Connect your repository: `stels-karthik/phishing-email-analyzer`
4. Configure:
   - **Name**: `phishing-analyzer-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
5. Add Environment Variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_SAFE_BROWSING_API_KEY=optional
   ```
6. Click "Create Web Service"
7. Copy your API URL (e.g., `https://phishing-analyzer-api.onrender.com`)

**Step 2: Deploy Frontend to Vercel**
1. Go to https://vercel.com and sign in with GitHub
2. Click "Add New..." → "Project"
3. Import `stels-karthik/phishing-email-analyzer`
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   ```
   VITE_API_URL=https://phishing-analyzer-api.onrender.com
   ```
6. Click "Deploy"
7. Your app will be live at `https://your-project.vercel.app`

**Done!** 🎉 Your app is now in production.

---

## Backend Deployment

### Option 1: Render.com (Recommended - Free Tier)

**Pros:**
- Free tier available (750 hours/month)
- Auto-deploy from GitHub
- Built-in SSL
- PostgreSQL available (if needed)

**Cons:**
- Spins down after 15 min inactivity (cold starts)
- 512 MB RAM on free tier

**Deployment Steps:**

1. **Create `render.yaml` in project root:**

```yaml
services:
  - type: web
    name: phishing-analyzer-api
    env: python
    region: oregon
    plan: free
    branch: master
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: GOOGLE_SAFE_BROWSING_API_KEY
        sync: false
      - key: DEBUG
        value: False
```

2. **Push to GitHub:**
```bash
git add render.yaml
git commit -m "Add Render deployment config"
git push origin master
```

3. **Deploy on Render:**
   - Visit https://dashboard.render.com/
   - Click "New +" → "Blueprint"
   - Connect repository
   - Render will auto-deploy

4. **Set Environment Variables** in Render dashboard

### Option 2: Railway.app (Free Tier)

**Pros:**
- $5 free credit per month
- No cold starts on free tier
- Simpler configuration

**Cons:**
- Limited free tier ($5/month credit)

**Deployment Steps:**

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
```

2. **Login and Deploy:**
```bash
cd C:\code\agentic-ai\phishing-analyzer\backend
railway login
railway init
railway up
```

3. **Set Environment Variables:**
```bash
railway variables set GROQ_API_KEY=your_key
railway variables set DEBUG=False
```

4. **Generate Domain:**
```bash
railway domain
```

### Option 3: Fly.io (Free Tier)

**Pros:**
- 3 shared VMs free
- No cold starts
- Global edge network

**Deployment Steps:**

1. **Install Fly CLI:**
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

2. **Create `fly.toml` in backend directory:**

```toml
app = "phishing-analyzer"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

3. **Deploy:**
```bash
cd backend
fly launch
fly secrets set GROQ_API_KEY=your_key
fly deploy
```

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

**Pros:**
- Free for personal projects
- Automatic HTTPS
- Global CDN
- Auto-deploy from GitHub

**Manual Deployment:**

1. **Update Frontend API URL:**

Create `frontend/.env.production`:
```bash
VITE_API_URL=https://your-backend-url.onrender.com
```

2. **Install Vercel CLI:**
```bash
npm install -g vercel
```

3. **Deploy:**
```bash
cd frontend
vercel --prod
```

**GitHub Integration (Recommended):**

1. Visit https://vercel.com
2. Import project from GitHub
3. Select `phishing-email-analyzer`
4. Set root directory to `frontend`
5. Add environment variable `VITE_API_URL`
6. Deploy

### Option 2: Netlify

**Deployment Steps:**

1. **Create `netlify.toml` in frontend directory:**

```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend-url.onrender.com/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Deploy:**
```bash
cd frontend
npm install -g netlify-cli
netlify deploy --prod
```

### Option 3: Cloudflare Pages

**Pros:**
- Unlimited bandwidth (free)
- Fastest CDN
- Built-in analytics

**Deployment:**

1. Visit https://pages.cloudflare.com/
2. Connect GitHub repository
3. Configure:
   - **Build command**: `cd frontend && npm run build`
   - **Output directory**: `frontend/dist`
4. Add environment variable `VITE_API_URL`
5. Deploy

---

## Environment Configuration

### Backend Environment Variables

**Required:**
```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

**Optional:**
```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Database (if using persistent storage)
DATABASE_PATH=/data/phishing_analyzer.db

# Threat Intelligence
GOOGLE_SAFE_BROWSING_API_KEY=your_key

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=30
CACHE_TTL_HOURS=24
```

### Frontend Environment Variables

**Production:**
```bash
VITE_API_URL=https://your-backend-url.onrender.com
```

**Development:**
```bash
VITE_API_URL=http://localhost:8000
```

---

## Production Optimizations

### 1. Update CORS Settings

Edit `backend/app/main.py`:

```python
# Update CORS origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.vercel.app",
        "https://yourdomain.com",
    ],  # Specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Enable Production Mode

Update `backend/.env` (on deployment platform):
```bash
DEBUG=False
```

### 3. Add Health Check Endpoint

Already included at `/api/v1/health` - configure your platform to ping it every 5 minutes to prevent cold starts.

### 4. Optimize Build

**Backend** - Add to `requirements.txt`:
```
gunicorn==21.2.0
```

Update start command:
```bash
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

---

## Custom Domain Setup

### Vercel (Frontend)

1. Go to Project Settings → Domains
2. Add your domain: `analyzer.yourdomain.com`
3. Add DNS records as instructed:
   ```
   Type: CNAME
   Name: analyzer
   Value: cname.vercel-dns.com
   ```

### Render (Backend)

1. Go to Settings → Custom Domain
2. Add: `api.yourdomain.com`
3. Add DNS record:
   ```
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

---

## Monitoring & Maintenance

### 1. Set Up Monitoring

**Render:**
- Built-in metrics dashboard
- Email alerts for crashes

**Better Stack (Free):**
```bash
# Add to your start command
curl https://uptime.betterstack.com/api/v1/heartbeat/YOUR_KEY
```

### 2. Log Monitoring

**Render:**
- View logs in dashboard
- Set up log drains to external services

**Add Structured Logging:**

```python
# backend/app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. Error Tracking

**Sentry (Free Tier):**

```bash
pip install sentry-sdk[fastapi]
```

```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 4. Uptime Monitoring

Free services:
- **UptimeRobot**: https://uptimerobot.com (50 monitors free)
- **Better Uptime**: https://betterstack.com/uptime (10 monitors free)

Add monitors for:
- Frontend: `https://your-app.vercel.app`
- Backend Health: `https://your-api.onrender.com/api/v1/health`

---

## Security Checklist

Before going live:

- [ ] Set `DEBUG=False` in production
- [ ] Update CORS to specific origins (not `*`)
- [ ] Never commit `.env` file
- [ ] Rotate API keys regularly
- [ ] Enable HTTPS (automatic on Vercel/Render)
- [ ] Set up rate limiting (if high traffic expected)
- [ ] Review API authentication (add if storing user data)
- [ ] Enable security headers:

```python
# backend/app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "*.vercel.app"]
)
```

---

## Cost Estimates

### Zero-Cost Stack (Recommended for Starting)

| Service | Tier | Limit | Cost |
|---------|------|-------|------|
| Groq API | Free | 14,400 req/day | $0 |
| Render | Free | 750 hours/month | $0 |
| Vercel | Hobby | Unlimited | $0 |
| URLhaus | Free | Unlimited | $0 |
| Google SB | Free | 10k lookups/day | $0 |
| **Total** | | | **$0/month** |

**Capacity:** ~10,000 email analyses/month

### Low-Cost Stack (For Growth)

| Service | Tier | Limit | Cost |
|---------|------|-------|------|
| Groq API | Pay-as-go | ~50k emails/month | ~$2.50 |
| Render | Starter | Always-on | $7 |
| Vercel | Pro | High traffic | $20 |
| **Total** | | | **~$30/month** |

**Capacity:** ~50,000 email analyses/month

---

## Troubleshooting

### Backend Issues

**Cold Starts on Render:**
- Add a cron job to ping `/api/v1/health` every 10 minutes
- Upgrade to paid tier ($7/month) for always-on

**Out of Memory:**
- Reduce worker count in gunicorn
- Upgrade instance size
- Optimize agent prompts to use fewer tokens

**API Timeouts:**
- Increase timeout in Render settings (default: 30s)
- Optimize slow endpoints
- Consider background job processing for batch analysis

### Frontend Issues

**API Connection Errors:**
- Verify `VITE_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is deployed and healthy

**Build Failures:**
- Check Node.js version compatibility
- Clear build cache and retry
- Review build logs for specific errors

---

## Scaling Considerations

### When to Scale

Monitor these metrics:
- Response time > 5 seconds
- Error rate > 1%
- Memory usage > 80%
- Groq API rate limits hit

### Scaling Options

1. **Horizontal Scaling** (Multiple Instances)
   - Render: Enable autoscaling ($25/month+)
   - Add load balancer

2. **Vertical Scaling** (Bigger Instances)
   - Render: Upgrade to 2GB RAM ($25/month)
   - Railway: Increase resources

3. **Caching Layer**
   - Add Redis for result caching
   - Render Redis: $5/month

4. **Background Jobs**
   - Use Celery + Redis for async processing
   - Handle batch analysis in background

---

## Quick Reference: Deployment Commands

### Initial Setup
```bash
# Update API URL in frontend
echo "VITE_API_URL=https://your-api-url.onrender.com" > frontend/.env.production

# Commit deployment configs
git add .
git commit -m "Add production deployment configs"
git push origin master
```

### Render Deployment
```bash
# Just push to GitHub - auto-deploys
git push origin master
```

### Vercel Deployment
```bash
cd frontend
vercel --prod
```

### Check Deployment Status
```bash
# Backend health check
curl https://your-api-url.onrender.com/api/v1/health

# Frontend
curl -I https://your-app.vercel.app
```

---

## Next Steps

1. **Deploy Backend** to Render (follow Quick Deploy)
2. **Deploy Frontend** to Vercel
3. **Test Production** with example email
4. **Set Up Monitoring** (UptimeRobot)
5. **Add Custom Domain** (optional)
6. **Share Your App!** 🎉

Need help? Check the logs:
- Render: Dashboard → Logs
- Vercel: Dashboard → Deployments → Logs

---

**Remember:** All these platforms offer free tiers perfect for getting started. You can always upgrade as your usage grows!
