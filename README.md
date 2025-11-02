# AutoIPIndia - Automated Indian Trademark Status Tracker

A comprehensive full-stack application for tracking trademark statuses on the Indian IP office website, with multiple frontend options.

## 📁 Project Structure

```
autoipindia/
├── backend/              # FastAPI backend with Playwright scraping
│   ├── main.py              # API endpoints
│   ├── config.py            # Configuration
│   ├── db.py                # Database connection
│   ├── logic/               # Business logic
│   ├── helpers/             # Utilities (CAPTCHA solver)
│   ├── sample_captchas/     # CAPTCHA training data
│   ├── Dockerfile           # Backend container
│   └── requirements.txt     # Python dependencies
│
│   ├── app.py               # Dash application
│   ├── Dockerfile           # Frontend container
│   └── requirements.txt     # Python dependencies
│
└── frontend/             # React (TypeScript) frontend
    ├── src/                 # React components
    ├── Dockerfile           # React container
    ├── package.json         # Node dependencies
    └── README.md            # React-specific docs
```

## ✨ Features

### Backend (FastAPI)
- 🔐 **Secure API**: Bearer token authentication for all endpoints
- 🤖 **Automated Scraping**: Uses Playwright to automate trademark searches
- 🧩 **CAPTCHA Solving**: AI-powered CAPTCHA solving with Google Gemini
- 📊 **Database Storage**: DuckDB/MotherDuck for efficient data management
- 🚀 **FastAPI**: Modern, fast REST API with automatic documentation
- 🐳 **Docker Ready**: Containerized deployment with all dependencies

### Frontend Options

#### Option 1: Dash (Python)
- 🎨 **Professional Dashboard**: Interactive admin panel built with Plotly Dash
- 📋 **Interactive Tables**: Sort, filter, and search with AG Grid
- 🔄 **Click-to-Refresh**: Re-ingest any trademark with one click
- ➕ **Easy Ingestion**: Form-based interface for adding new trademarks
- 📈 **Real-time Stats**: Live dashboard with trademark statistics
- 🐍 **Pure Python**: Easy to maintain if you're a Python developer

#### Option 2: React (TypeScript)
- ⚛️ **Modern React**: Built with React 18 + TypeScript + Vite
- 🎯 **Type-Safe**: Full TypeScript coverage
- ⚡ **Lightning Fast**: Vite for instant HMR and optimized builds
- 📊 **TanStack Table**: Advanced data grid with sorting, filtering, pagination
- 🎨 **TailwindCSS**: Beautiful, responsive design
- 🌐 **Deploy Anywhere**: Vercel, Netlify, S3, or any static host

## 🏗️ Architecture

```
┌─────────────────────┐         HTTP + Bearer Token        ┌──────────────────────┐
│                     │ ───────────────────────────────────▶│                      │
│  Frontend           │                                     │  FastAPI Backend     │
│  (Dash or React)    │ ◀───────────────────────────────────│  (Playwright)        │
│  Port 8050/3000     │         JSON Responses              │  Port 8000           │
└─────────────────────┘                                     └──────────────────────┘
         │                                                            │
         │                                                            │
         ▼                                                            ▼
    User Browser                                          DuckDB/MotherDuck + IP India
```

**Benefits of Separation:**
- Deploy backend on Google Cloud Run (auto-scaling, pay-per-use)
- Deploy Dash frontend on Render/Railway (Python hosting)
- Deploy React frontend on Vercel/Netlify (optimized for static sites)
- Scale independently based on usage
- Update frontend without touching backend and vice versa

## 🚀 Quick Start

### Option 1: Backend Only (API)

Perfect if you want to use the API programmatically or build your own frontend.

```bash
cd backend

# Configure environment
cp .env.example .env
# Edit .env with your API_TOKEN, GEMINI_API_KEY, MOTHERDUCK_TOKEN

# Run with Docker
docker build -t autoipindia-backend .
docker run -d -p 8000:8000 --env-file .env autoipindia-backend

# OR run locally
pip install -r requirements.txt
playwright install chromium
python main.py
```

**Access API:** http://localhost:8000/docs

---

### Option 2: Backend + Dash Frontend

Get a complete Python-based admin dashboard.

```bash
# Terminal 1 - Start Backend
cd backend
cp .env.example .env  # Edit with your credentials
docker build -t autoipindia-backend .
docker run -d -p 8000:8000 --env-file .env autoipindia-backend

# Terminal 2 - Start Dash Frontend
cd frontend
cp .env.example .env
# Edit with:
#   API_BASE_URL=http://localhost:8000
#   API_TOKEN=<same as backend>

pip install -r requirements.txt
python app.py
```

**Access:**
- **Dashboard:** http://localhost:8050
- **API Docs:** http://localhost:8000/docs

📚 **See [frontend/README.md](frontend/README.md) for detailed Dash deployment guides**

---

### Option 3: Backend + React Frontend

Modern, fast React + TypeScript UI.

```bash
# Terminal 1 - Start Backend
cd backend
cp .env.example .env  # Edit with your credentials
docker build -t autoipindia-backend .
docker run -d -p 8000:8000 --env-file .env autoipindia-backend

# Terminal 2 - Start React Frontend
cd frontend
npm install
cp .env.example .env
# Edit with:
#   VITE_API_BASE_URL=http://localhost:8000
#   VITE_API_TOKEN=<same as backend>

npm run dev
```

**Access:**
- **React App:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

📚 **See [frontend/README.md](frontend/README.md) for detailed React deployment guides**

---

## 🌐 Deployment Recommendations

### Backend (FastAPI)
- **Google Cloud Run** ⭐ - Best for auto-scaling, pay-per-request
- **Railway** - Simple deployment with $5 free credit
- **Render** - Free tier available
- **Heroku** - Traditional PaaS (starts at $7/month)

### Dash Frontend (Python)
- **Render** ⭐ - Easy deployment, free tier
- **Railway** - Good for Python apps
- **PythonAnywhere** - Budget option ($5/month)
- **Google Cloud Run** - Can deploy alongside backend

### React Frontend (TypeScript)
- **Vercel** ⭐ - Best for React, free tier, instant deploys
- **Netlify** ⭐ - Great for static sites, free tier
- **AWS S3 + CloudFront** - Very cheap, highly scalable
- **Google Cloud Run** - Can deploy alongside backend
- **Any static host** - GitHub Pages, Cloudflare Pages, etc.

## 🎯 Which Frontend Should You Choose?

| Criteria | Dash (Python) | React (TypeScript) |
|----------|---------------|-------------------|
| **Your Experience** | Python developer | JavaScript/TypeScript developer |
| **Learning Curve** | Easy | Medium |
| **Customization** | Good | Unlimited |
| **Performance** | Good | Excellent |
| **Deployment** | Python hosting | Static hosting (cheaper) |
| **Mobile UX** | Good | Excellent |
| **Development Speed** | Fast | Medium |
| **Best For** | Internal tools, Python teams | Public apps, custom UIs |

**Recommendation:**
- 🐍 **Dash** if you're a Python developer and want fast development
- ⚛️ **React** if you want maximum customization and best performance
- 🎯 **Both** work great! You can even deploy both and let users choose

## 📚 API Endpoints

All endpoints require `Authorization: Bearer YOUR_API_TOKEN` header.

### Ingestion Endpoints

- `GET /ingest/all?stale_since_days=15` - Ingest stale trademarks
- `GET /ingest/tm?wordmark=X&class_name=Y` - Ingest specific trademark
- `GET /ingest/tm/{application_number}` - Ingest by application number

### Retrieval Endpoints

- `GET /retrieve/all` - Get all trademarks from database
- `GET /search/tm?wordmark=X&class_name=Y` - Search by wordmark and class
- `GET /search/tm/{application_number}` - Search by application number

## 🔧 Environment Variables

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `API_TOKEN` | Yes | Secret token for API authentication |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for CAPTCHA solving |
| `MOTHERDUCK_TOKEN` | Yes | MotherDuck token for database access |
| `DATABASE_NAME` | No | Database name (default: `autoipindia`) |
| `CAPTCHA_MAX_RETRIES` | No | Max CAPTCHA solve attempts (default: `5`) |

### Dash Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `API_BASE_URL` | Yes | Backend API URL |
| `API_TOKEN` | Yes | API token (must match backend) |
| `PORT` | No | Port for frontend server (default: `8050`) |

### React Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | Backend API URL |
| `VITE_API_TOKEN` | Yes | API token (must match backend) |

## 🔒 Security Notes

- ⚠️ **Never commit `.env` files** - they contain sensitive credentials
- 🔑 Use strong, randomly generated `API_TOKEN`
- 🔒 Use HTTPS in production environments
- 🚫 Restrict network access to the API in production
- 🛡️ Keep all dependencies updated

## 🐳 Docker Compose (All Services)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - API_TOKEN=${API_TOKEN}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - MOTHERDUCK_TOKEN=${MOTHERDUCK_TOKEN}
    env_file:
      - ./backend/.env

  dash-frontend:
    build: ./frontend
    ports:
      - "8050:8050"
    environment:
      - API_BASE_URL=http://backend:8000
      - API_TOKEN=${API_TOKEN}
    depends_on:
      - backend

  react-frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_BASE_URL=http://localhost:8000
        - VITE_API_TOKEN=${API_TOKEN}
    ports:
      - "80:80"
    depends_on:
      - backend
```

Run everything:
```bash
docker-compose up -d
```

## 🛠️ Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
python main.py
```

### Dash Frontend Development

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

### React Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 📖 Documentation

- **Backend API:** http://localhost:8000/docs (Swagger UI)
- **Dash Frontend:** [frontend/README.md](frontend/README.md)
- **React Frontend:** [frontend/README.md](frontend/README.md)

## 🤝 Contributing

Contributions welcome! Each component (backend, Dash frontend, React frontend) can be developed independently.

## 📄 License

See LICENSE file for details.

---

## 🎉 What's Included

✅ Production-ready FastAPI backend with authentication
✅ Playwright automation with AI CAPTCHA solving
✅ Two complete frontend options (Dash + React)
✅ Docker support for all components
✅ Comprehensive deployment guides
✅ Type-safe TypeScript frontend
✅ Modern Python Dash frontend
✅ Real-time data updates
✅ Interactive data tables
✅ Responsive design
✅ Complete documentation

**Choose your stack and deploy!** 🚀
