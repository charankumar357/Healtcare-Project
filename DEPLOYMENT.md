# HealthBridge AI — Deployment Guide

Deploy the full stack using **free tiers only** (no credit card needed for most).

---

## Architecture Overview

```
┌────────────────┐     ┌──────────────────┐     ┌──────────────┐
│  React Native  │────▶│  FastAPI Backend  │────▶│  Supabase    │
│  Expo App      │     │  (Render.com)     │     │  PostgreSQL  │
│  (Mobile)      │     │                   │────▶│  (Database)  │
└────────────────┘     │                   │     └──────────────┘
                       │  Gemini / Groq    │
                       │  LLM APIs         │
                       └──────────────────┘
```

---

## Step 1: Database (Supabase) — 5 minutes

1. Go to [supabase.com](https://supabase.com) → **Start your project**
2. Create a new project (choose a region close to India: **ap-south-1**)
3. Wait for project to initialize (~2 minutes)
4. Go to **SQL Editor** → **New Query**
5. Copy-paste the entire contents of `healthbridge-api/scripts/create_tables.sql`
6. Click **Run** → You should see 3 tables created
7. Go to **Settings** → **Database** → Copy the **Connection string (URI)**
8. Replace `postgresql://` with `postgresql+asyncpg://` in the URI

Your `DATABASE_URL` will look like:
```
postgresql+asyncpg://postgres.[ref]:[password]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

---

## Step 2: API Keys — 5 minutes

| Key | Where to Get |
|-----|-------------|
| **GEMINI_API_KEY** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → Create API Key |
| **GROQ_API_KEY** | [console.groq.com/keys](https://console.groq.com/keys) → Create API Key |

Generate secret keys (run in any terminal):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Run it twice — once for `SECRET_KEY`, once for `JWT_SECRET_KEY`.

---

## Step 3: Deploy Backend on Render.com — 10 minutes

### 3a. Prepare the repo

Your repo needs 2 extra files in `healthbridge-api/`. Create them:

**`healthbridge-api/Dockerfile`**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`healthbridge-api/render.yaml`** (optional — for blueprint deploy):
```yaml
services:
  - type: web
    name: healthbridge-api
    runtime: docker
    rootDir: healthbridge-api
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
```

### 3b. Deploy on Render

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **New** → **Web Service**
3. Connect your GitHub repo: `charankumar357/Healtcare-Project`
4. Configure:
   - **Name**: `healthbridge-api`
   - **Root Directory**: `healthbridge-api`
   - **Runtime**: `Docker`
   - **Instance Type**: `Free`
5. Add **Environment Variables** (click "Add Environment Variable"):

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | Your Supabase connection string |
   | `GEMINI_API_KEY` | Your Gemini key |
   | `GROQ_API_KEY` | Your Groq key |
   | `SECRET_KEY` | Your generated secret |
   | `JWT_SECRET_KEY` | Your generated JWT secret |
   | `DEBUG` | `false` |
   | `ALLOWED_ORIGINS` | `*` |

6. Click **Create Web Service**
7. Wait 3-5 minutes for build + deploy
8. Your API will be live at: `https://healthbridge-api.onrender.com`

### 3c. Verify Deployment

Open in browser:
```
https://healthbridge-api.onrender.com/health
```
You should see:
```json
{"status": "ok", "db": "connected", "version": "1.0.0"}
```

API docs at: `https://healthbridge-api.onrender.com/docs`

---

## Step 4: Frontend (Expo) — For Development

```bash
cd front_end
npm install
npx expo start
```

Update the API base URL in your frontend code to point to your Render deployment:
```
https://healthbridge-api.onrender.com
```

---

## Alternative: Deploy with Railway.app

If Render is slow (free tier sleeps after 15 min inactivity):

1. Go to [railway.app](https://railway.app) → Login with GitHub
2. **New Project** → **Deploy from GitHub Repo**
3. Select `charankumar357/Healtcare-Project`
4. Set **Root Directory** to `healthbridge-api`
5. Add environment variables (same as above)
6. Railway auto-detects Dockerfile and deploys

---

## Quick Reference

| Service | URL | Free Tier |
|---------|-----|-----------|
| **Supabase** | supabase.com | 500 MB DB, unlimited API |
| **Render** | render.com | 750 hours/month, sleeps after 15 min |
| **Railway** | railway.app | $5 free credit/month |
| **Gemini API** | aistudio.google.com | 15 requests/min |
| **Groq API** | console.groq.com | 30 requests/min |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `db: disconnected` on /health | Check DATABASE_URL has `postgresql+asyncpg://` prefix |
| `429 rate limit` on screening | Gemini free tier = 15 RPM. Groq fallback activates automatically |
| Render service sleeping | Free tier sleeps after 15 min. First request takes ~30s to wake up |
| CORS errors from frontend | Set `ALLOWED_ORIGINS=*` in env vars |
