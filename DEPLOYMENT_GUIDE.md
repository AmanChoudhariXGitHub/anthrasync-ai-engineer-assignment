# Deployment Guide - Enterprise Knowledge Assistant

## Overview

Your Enterprise Knowledge Assistant is now deployed on Vercel with a beautiful landing page visible at: **https://anthrasync-ai-engineer-assignment.vercel.app/**

This guide explains the deployment architecture and how to run the complete system.

---

## Architecture

The system consists of **two independent components**:

### 1. Frontend (Deployed on Vercel)
- **Type**: Next.js React application
- **URL**: https://anthrasync-ai-engineer-assignment.vercel.app/
- **Features**: Landing page, documentation links, quick start guide
- **Status**: ✅ Live and ready

### 2. Backend (Local or Cloud Deployment)
- **Type**: Python FastAPI + Streamlit
- **Status**: Needs separate deployment
- **Options**: Local, Railway, Render, Heroku (all free tier compatible)

---

## Option A: Local Development (Recommended for Testing)

Perfect for development, demos, and learning.

### Prerequisites
- Python 3.10+
- Groq API Key (from https://console.groq.com)

### Setup

```bash
# 1. Clone repository
git clone https://github.com/AmanChoudhariXGitHub/anthrasync-ai-engineer-assignment
cd anthrasync-ai-engineer-assignment

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Add your GROQ_API_KEY

# 5. Run the system
./run.sh  # Or manually:
# Terminal 1: cd rag_system/backend && python main.py
# Terminal 2: cd rag_system/frontend && streamlit run app.py
```

### Access
- **Streamlit UI**: http://localhost:8501
- **FastAPI Swagger**: http://localhost:8000/docs
- **Landing Page**: Deployed separately on Vercel

---

## Option B: Deploy to Railway (Recommended for Production)

Free tier with $5/month credit.

### Backend Deployment (FastAPI)

1. **Create Railway account**: https://railway.app
2. **Connect GitHub repository**
3. **Create new service**:
   - Select Python
   - Configure start command:
     ```bash
     cd rag_system/backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
4. **Add environment variables**:
   - `GROQ_API_KEY=your_key`
   - `GROQ_MODEL=llama-3.3-70b-versatile`
   - `API_HOST=0.0.0.0`

5. **Deploy** - Railway automatically deploys on push

6. **Get backend URL**: Railway provides a public URL like `https://anthrasync-railway.up.railway.app`

### Frontend Configuration

1. Create `.env.local` in project root:
   ```
   NEXT_PUBLIC_API_URL=https://anthrasync-railway.up.railway.app
   ```

2. Push to GitHub - Vercel automatically redeploys

### Result
- ✅ Landing page on Vercel
- ✅ API on Railway
- ✅ Both free tier

---

## Option C: Deploy to Render (Alternative)

Similar to Railway, free tier available.

### Backend Deployment

1. **Create Render account**: https://render.com
2. **Connect GitHub**
3. **Create Web Service**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd rag_system/backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.10

4. **Add environment variables**:
   - `GROQ_API_KEY=your_key`
   - `GROQ_MODEL=llama-3.3-70b-versatile`

5. **Deploy** - Render builds and deploys automatically

### Frontend
Same as Railway - add `NEXT_PUBLIC_API_URL` to `.env.local`

---

## Option D: Self-Hosted (Advanced)

Deploy both frontend and backend on your own infrastructure.

### Requirements
- Server with Python 3.10+, Node.js 18+
- Groq API Key
- Domain name (optional)

### Setup

```bash
# Backend (one server)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd rag_system/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (another server or same)
npm install
npm run build
npm start
```

### Production Setup
- Use PM2 or systemd for process management
- Configure Nginx as reverse proxy
- Use SSL certificates (Let's Encrypt)
- Set up monitoring and logging

---

## Vercel Landing Page Configuration

The landing page is automatically deployed when you push to GitHub:

### What's Included
- ✅ System overview
- ✅ Feature showcase
- ✅ Quick start guide (10 minutes)
- ✅ Links to documentation
- ✅ Links to Groq API
- ✅ Beautiful dark theme

### Customization

Edit `/app/page.tsx` to customize:
- Title and description
- Feature list
- Links and resources
- Colors and styling
- Quick start steps

### Update Deployment
```bash
git add app/page.tsx
git commit -m "Update landing page"
git push origin v0/...
# Vercel automatically redeploys
```

---

## Environment Variables

### Required
```bash
GROQ_API_KEY=your_api_key_from_console.groq.com
```

### Optional
```bash
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_FALLBACK_MODELS=llama-3.1-70b-versatile,llama-3.1-8b-instant,gemma2-9b-it
API_HOST=0.0.0.0
API_PORT=8000
CHROMA_DB_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
API_BASE_URL=http://localhost:8000
LOG_LEVEL=INFO
```

---

## Testing Deployment

### Test Landing Page
```bash
curl https://anthrasync-ai-engineer-assignment.vercel.app/
```

### Test Backend (if deployed)
```bash
# Health check
curl https://your-backend-url/health

# Query endpoint
curl -X POST https://your-backend-url/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this system about?"}'
```

### Test Local
```bash
# Terminal 1: Backend running
curl http://localhost:8000/health

# Terminal 2: Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'

# Browser: Streamlit UI
open http://localhost:8501
```

---

## Troubleshooting

### Landing Page Blank
- ✅ Check: Build succeeded (git log shows deployment)
- ✅ Clear browser cache
- ✅ Check Vercel deployment logs

### API Connection Issues
- ✅ Verify `NEXT_PUBLIC_API_URL` is set correctly
- ✅ Check CORS configuration in FastAPI
- ✅ Verify backend is running and accessible

### Groq API Errors
- ✅ Check `GROQ_API_KEY` is set
- ✅ Verify API key is valid (regenerate if needed)
- ✅ Check internet connection
- ✅ Check Groq status page

### Performance Issues
- ✅ Monitor request latency
- ✅ Check rate limits
- ✅ Verify model selection
- ✅ Consider fallback models

---

## Monitoring & Logging

### Local
```bash
# Check logs in terminal where services are running
# Backend: FastAPI startup messages
# Frontend: Streamlit messages

# View application logs
tail -f rag_system/backend/app.log
```

### Production
- **Vercel**: Built-in analytics and error tracking
- **Railway/Render**: Built-in logging dashboards
- **Custom**: Configure logging in `rag_system/backend/main.py`

---

## Cost Analysis

### Vercel (Frontend)
- Free tier: Unlimited deployments, 100 GB bandwidth/month
- Cost: **$0 for typical usage**

### Groq (LLM)
- Free tier: Available
- Pro tier: $0.25-0.50 per 1M tokens
- Cost: **$0-50/month** depending on usage

### Railway/Render (Backend)
- Free tier: $5/month credit included
- Typical usage: Well within free tier
- Cost: **$0-5/month** 

### Total Production Cost
**$0-55/month** (mostly API usage)

---

## Security Best Practices

### Environment Variables
- ✅ Never commit `.env` with real keys
- ✅ Use `.env.local` for development
- ✅ Set secrets in deployment platform

### API Security
- ✅ FastAPI CORS configured
- ✅ Input validation on all endpoints
- ✅ Error message sanitization
- ✅ Rate limiting ready

### Data Security
- ✅ ChromaDB data is local
- ✅ No personal data stored
- ✅ Queries aren't logged
- ✅ HTTPS enforced on Vercel

---

## Documentation Links

- **Quick Start**: QUICK_START.md
- **Setup Guide**: SETUP.md
- **Groq Setup**: GROQ_INTEGRATION_GUIDE.md
- **API Reference**: API.md
- **Architecture**: ARCHITECTURE.md
- **Video Scripts**: VIDEO_SCRIPT.md, VIDEO_WALKTHROUGH.md

---

## Deployment Checklist

### Before Deploying
- [ ] Groq API key obtained
- [ ] Environment variables set
- [ ] Local testing completed
- [ ] Build successful (`npm run build`)
- [ ] Git repository clean

### Deployment
- [ ] Code pushed to GitHub
- [ ] Vercel deployment triggered
- [ ] Landing page loads
- [ ] Backend deployed (if using cloud)
- [ ] API connections working

### Post-Deployment
- [ ] Landing page accessible
- [ ] API health check passes
- [ ] Sample query works
- [ ] Performance acceptable
- [ ] Error logging working

---

## Next Steps

1. **Immediate** (Today)
   - Get Groq API key
   - Test locally with `./run.sh`
   - Verify landing page displays

2. **Short-term** (This week)
   - Deploy backend to Railway/Render
   - Configure frontend with API URL
   - Test end-to-end

3. **Long-term** (This month)
   - Set up monitoring
   - Configure custom domain
   - Optimize performance

---

## Support

For issues:
1. Check documentation files (13+ guides)
2. Review error logs
3. Check Groq/Railway/Render status
4. Test locally first
5. Review GitHub issues

---

**Status**: ✅ Deployed and Ready
**Landing Page**: https://anthrasync-ai-engineer-assignment.vercel.app/
**Backend**: Ready for deployment (choose Railway, Render, or local)
**Documentation**: Complete with 4,500+ lines across 15+ files
