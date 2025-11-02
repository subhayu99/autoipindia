# AutoIPIndia - Automated Indian Trademark Status Tracker

A comprehensive Python-based automation tool for tracking trademark statuses on the Indian IP office website.

## Features

### Backend (FastAPI)
- 🔐 **Secure API**: Bearer token authentication for all endpoints
- 🤖 **Automated Scraping**: Uses Playwright to automate trademark searches
- 🧩 **CAPTCHA Solving**: AI-powered CAPTCHA solving with Google Gemini
- 📊 **Database Storage**: DuckDB/MotherDuck for efficient data management
- 🚀 **FastAPI**: Modern, fast REST API with automatic documentation
- 🐳 **Docker Ready**: Containerized deployment with all dependencies

### Frontend (Dash)
- 🎨 **Professional Dashboard**: Interactive admin panel built with Plotly Dash
- 📋 **Interactive Tables**: Sort, filter, and search with AG Grid
- 🔄 **Click-to-Refresh**: Re-ingest any trademark with one click
- ➕ **Easy Ingestion**: Form-based interface for adding new trademarks
- 📈 **Real-time Stats**: Live dashboard with trademark statistics
- 🌐 **Separate Deployment**: Deploy frontend independently from backend

## 🏗️ Architecture

This project consists of two separate applications that can be deployed independently:

```
┌─────────────────────┐         HTTP + Bearer Token        ┌──────────────────────┐
│                     │ ───────────────────────────────────▶│                      │
│  Dash Frontend      │                                     │  FastAPI Backend     │
│  (Python/Plotly)    │ ◀───────────────────────────────────│  (Playwright)        │
│  Port 8050          │         JSON Responses              │  Port 8000           │
└─────────────────────┘                                     └──────────────────────┘
         │                                                            │
         │                                                            │
         ▼                                                            ▼
    User Browser                                          DuckDB/MotherDuck + IP India
```

**Benefits of Separation:**
- Deploy backend on Google Cloud Run (auto-scaling, pay-per-use)
- Deploy frontend on Render/Railway/Netlify (optimized for web apps)
- Scale independently based on usage
- Update frontend without touching backend and vice versa

## Quick Start

### Option 1: Run Backend Only (API)

Perfect if you want to use the API programmatically or build your own frontend.

#### 1. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your credentials:
# - API_TOKEN: Your chosen secret token for API authentication
# - GEMINI_API_KEY: From https://aistudio.google.com/apikey
# - MOTHERDUCK_TOKEN: From https://motherduck.com
```

#### 2. Build and run backend with Docker

```bash
# Build the Docker image
docker build -t autoipindia .

# Run the container
docker run -d \
  --name autoipindia \
  -p 8000:8000 \
  --env-file .env \
  autoipindia
```

#### 3. Access the API

The API will be available at `http://localhost:8000`

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

### Option 2: Run Full Stack (Backend + Frontend)

Get a complete admin dashboard with interactive UI.

#### 1. Start the Backend

```bash
# From project root
cp .env.example .env
# Edit .env with your credentials

docker build -t autoipindia-backend .
docker run -d --name autoipindia-backend -p 8000:8000 --env-file .env autoipindia-backend
```

#### 2. Start the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Configure frontend
cp .env.example .env
# Edit frontend/.env with:
# - API_BASE_URL=http://localhost:8000
# - API_TOKEN=<same token as backend>

# Run with Docker
docker build -t autoipindia-frontend .
docker run -d --name autoipindia-frontend -p 8050:8050 --env-file .env autoipindia-frontend

# OR run locally (development)
pip install -r requirements.txt
python app.py
```

#### 3. Access the Dashboard

- **Frontend Dashboard**: http://localhost:8050
- **Backend API**: http://localhost:8000/docs

**📚 For detailed frontend documentation, deployment options, and customization, see [frontend/README.md](frontend/README.md)**

## Authentication

All API endpoints require Bearer token authentication. Include your API token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" http://localhost:8000/retrieve/all
```

Or using Python:

```python
import requests

headers = {
    "Authorization": "Bearer YOUR_API_TOKEN"
}

response = requests.get("http://localhost:8000/retrieve/all", headers=headers)
print(response.json())
```

## Local Development Setup

### Prerequisites

- Python 3.11+
- Playwright
- API keys for Gemini and MotherDuck

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd autoipindia

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Running Locally

```bash
# Make sure .env is configured with your API_TOKEN and other credentials
python main.py
```

The server will start at http://localhost:8000 with hot reload enabled.

## API Endpoints

All endpoints require `Authorization: Bearer YOUR_API_TOKEN` header.

### Ingestion Endpoints

- `GET /ingest/all?stale_since_days=15` - Ingest stale trademarks
- `GET /ingest/tm?wordmark=X&class_name=Y` - Ingest specific trademark
- `GET /ingest/tm/{application_number}` - Ingest by application number

### Retrieval Endpoints

- `GET /retrieve/all` - Get all trademarks from database
- `GET /search/tm?wordmark=X&class_name=Y` - Search by wordmark and class
- `GET /search/tm/{application_number}` - Search by application number

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_TOKEN` | Yes | Secret token for API authentication |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for CAPTCHA solving |
| `MOTHERDUCK_TOKEN` | Yes | MotherDuck token for database access |
| `DATABASE_NAME` | No | Database name (default: `autoipindia`) |
| `DATABASE_PROTOCOL` | No | Database protocol (default: `duckdb:///`) |
| `TRADEMARKS_STATUS_TABLE_NAME` | No | Status table name (default: `trademark_status`) |
| `TRADEMARKS_FAILED_TABLE_NAME` | No | Failed table name (default: `failed_trademarks`) |
| `CAPTCHA_MAX_RETRIES` | No | Max CAPTCHA solve attempts (default: `5`) |

## 🌐 Deployment Recommendations

### Backend (FastAPI)
- **Google Cloud Run** - Best for auto-scaling, pay-per-request (recommended)
- **Railway** - Simple deployment with $5 free credit
- **Render** - Free tier available
- **Heroku** - Traditional PaaS (starts at $7/month)

### Frontend (Dash)
- **Render** - Easy deployment, free tier (recommended for frontend)
- **Railway** - Good for Python apps
- **PythonAnywhere** - Budget option ($5/month)
- **Google Cloud Run** - Can deploy alongside backend

See [frontend/README.md](frontend/README.md) for detailed deployment instructions for each platform.

---

## Docker Configuration

The Dockerfile includes:
- Python 3.11 slim base image
- All Playwright dependencies for Chromium
- Optimized layer caching for faster builds
- Non-root user for security
- Health checks for container monitoring
- Port 8000 exposed for API access

### Docker Commands

```bash
# Build
docker build -t autoipindia .

# Run with environment file
docker run -d -p 8000:8000 --env-file .env --name autoipindia autoipindia

# View logs
docker logs -f autoipindia

# Stop container
docker stop autoipindia

# Remove container
docker rm autoipindia
```

## Security Notes

- ⚠️ **Never commit your `.env` file** - it contains sensitive credentials
- 🔑 Use a strong, randomly generated `API_TOKEN`
- 🔒 Use HTTPS in production environments
- 🚫 Restrict network access to the API in production

## License

See LICENSE file for details.
