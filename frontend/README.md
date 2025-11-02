# AutoIPIndia Dashboard - Dash Frontend

Professional admin panel for managing Indian trademark statuses, built with Plotly Dash.

## ✨ Features

- 🔐 **Secure Authentication** - Token-based API authentication
- 📊 **Interactive Data Table** - Sort, filter, search with AG Grid
- 🔄 **Click-to-Refresh** - Re-ingest any trademark with one click
- ➕ **Add New Trademarks** - Easy form for ingesting new data
- 📈 **Real-time Statistics** - Dashboard with trademark counts
- 🎨 **Professional UI** - Bootstrap-themed responsive design
- 🔍 **Advanced Search** - Filter by any field in real-time

## 🚀 Quick Start

### Local Development

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your API_BASE_URL and API_TOKEN

# 5. Run the app
python app.py
```

The dashboard will be available at http://localhost:8050

### Docker Deployment

```bash
# Build the image
docker build -t autoipindia-frontend .

# Run the container
docker run -d \
  --name autoipindia-frontend \
  -p 8050:8050 \
  -e API_BASE_URL=http://your-backend-url:8000 \
  -e API_TOKEN=your-secret-token \
  autoipindia-frontend

# Or use environment file
docker run -d \
  --name autoipindia-frontend \
  -p 8050:8050 \
  --env-file .env \
  autoipindia-frontend
```

## 🌐 Deployment Options

### 1. **Render** (Recommended for production)

**Why Render:**
- ✅ Free tier available
- ✅ Auto-deploys from Git
- ✅ Easy environment variable management
- ✅ HTTPS included
- ✅ Good for Python apps

**Steps:**

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - **Name**: `autoipindia-frontend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server --bind 0.0.0.0:$PORT --workers 4`
   - **Environment Variables**:
     - `API_BASE_URL`: Your backend URL
     - `API_TOKEN`: Your API token
6. Click "Create Web Service"

**Cost**: Free tier available (spins down after inactivity)

---

### 2. **Railway** (Easy deployment)

**Why Railway:**
- ✅ Simple deployment
- ✅ Free $5 credit monthly
- ✅ Good documentation

**Steps:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables
railway variables set API_BASE_URL=http://your-backend-url:8000
railway variables set API_TOKEN=your-secret-token
```

**Cost**: $5 free credit/month, then usage-based

---

### 3. **Google Cloud Run** (Scalable, same as backend)

**Why Cloud Run:**
- ✅ Scales to zero (no cost when idle)
- ✅ Pay per request
- ✅ Great performance
- ✅ Easy to manage alongside backend

**Steps:**

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/autoipindia-frontend

# Deploy to Cloud Run
gcloud run deploy autoipindia-frontend \
  --image gcr.io/YOUR_PROJECT_ID/autoipindia-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars API_BASE_URL=https://your-backend-url.run.app,API_TOKEN=your-token
```

**Cost**: Free tier includes 2 million requests/month

---

### 4. **Heroku** (Traditional PaaS)

**Why Heroku:**
- ✅ Well-documented
- ✅ Easy deployment
- ✅ Add-ons ecosystem

**Steps:**

1. Create `Procfile` in frontend directory:
   ```
   web: gunicorn app:server --bind 0.0.0.0:$PORT --workers 4
   ```

2. Deploy:
   ```bash
   heroku create autoipindia-frontend
   heroku config:set API_BASE_URL=http://your-backend-url
   heroku config:set API_TOKEN=your-secret-token
   git subtree push --prefix frontend heroku main
   ```

**Cost**: Free tier discontinued, starts at $7/month

---

### 5. **Netlify** (With workaround)

**Note:** Netlify is primarily for static sites, but you can use it with serverless functions.

For pure Python Dash app, better to use Render, Railway, or Cloud Run.

---

### 6. **PythonAnywhere** (Budget option)

**Why PythonAnywhere:**
- ✅ Very cheap ($5/month)
- ✅ Simple Python hosting
- ✅ Good for small projects

**Steps:**

1. Sign up at [PythonAnywhere](https://www.pythonanywhere.com)
2. Upload your code
3. Create web app with manual configuration
4. Set WSGI file to use Gunicorn
5. Configure environment variables in web app settings

**Cost**: Free tier available, $5/month for custom domains

---

## 🔧 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `API_BASE_URL` | Yes | Backend API URL | `http://localhost:8000` or `https://api.example.com` |
| `API_TOKEN` | Yes | API authentication token (must match backend) | `your-secret-token-123` |
| `PORT` | No | Port for frontend server (default: 8050) | `8050` |
| `DEBUG` | No | Enable debug mode (default: False) | `True` or `False` |

## 📱 How to Use the Dashboard

### 1. **View All Trademarks**
   - The main table shows all trademarks in your database
   - Use the search bar to filter by any field
   - Click column headers to sort

### 2. **Add New Trademark**
   - Enter **either**:
     - Application Number, **OR**
     - Wordmark + Class
   - Click "Ingest" to fetch from IP India website
   - System will solve CAPTCHA automatically

### 3. **Refresh Existing Trademark**
   - Click on any row in the table to select it
   - Click "Re-ingest" button to update that trademark
   - Useful for checking status changes

### 4. **Statistics**
   - Dashboard shows real-time counts:
     - Total trademarks tracked
     - Registered trademarks
     - Pending/examination
     - Other statuses

### 5. **Refresh All**
   - Click "Refresh All" button to reload data from backend
   - Auto-updates statistics

## 🏗️ Architecture

```
┌─────────────────┐         HTTP + Bearer Token        ┌──────────────────┐
│                 │ ───────────────────────────────────▶│                  │
│  Dash Frontend  │                                     │  FastAPI Backend │
│  (Port 8050)    │ ◀───────────────────────────────────│  (Port 8000)     │
│                 │         JSON Responses               │                  │
└─────────────────┘                                     └──────────────────┘
      │                                                          │
      │                                                          │
      ▼                                                          ▼
  User Browser                                          Playwright + DuckDB
```

**Communication Flow:**
1. User interacts with Dash UI
2. Dash app makes authenticated API calls to FastAPI backend
3. Backend performs web scraping and database operations
4. Results returned to frontend
5. UI updates reactively

## 🎨 Customization

### Themes

The app uses Bootstrap theme. To change:

```python
# In app.py, change the external_stylesheets
external_stylesheets=[dbc.themes.DARKLY]  # Dark theme
# Options: BOOTSTRAP, CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL,
#          LITERA, LUMEN, LUX, MATERIA, MINTY, MORPH, PULSE, QUARTZ,
#          SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR, SPACELAB, SUPERHERO,
#          UNITED, VAPOR, YETI, ZEPHYR
```

### Table Configuration

Modify `columnDefs` in `update_table()` function to customize columns, widths, filters, etc.

### Auto-refresh

Uncomment and configure the interval component to enable auto-refresh:

```python
dcc.Interval(id="auto-refresh-interval", interval=60000, n_intervals=0, disabled=False)
```

## 🔒 Security Notes

- ⚠️ **Never commit `.env` file** with real credentials
- 🔑 Always use HTTPS in production (enabled by default on Render, Railway, Cloud Run)
- 🔐 Keep `API_TOKEN` secret and rotate regularly
- 🚫 Don't expose admin dashboards publicly without authentication

## 🐛 Troubleshooting

### "Connection Error" or "Unable to fetch data"
- ✅ Check `API_BASE_URL` is correct
- ✅ Verify backend is running and accessible
- ✅ Ensure `API_TOKEN` matches between frontend and backend
- ✅ Check firewall/network settings

### "401 Unauthorized"
- ✅ Verify `API_TOKEN` environment variable is set correctly
- ✅ Check token matches backend configuration

### Table not loading
- ✅ Click "Refresh All" button
- ✅ Check browser console for errors (F12)
- ✅ Verify backend `/retrieve/all` endpoint is working

### Slow performance
- ✅ Reduce `paginationPageSize` in table config
- ✅ Increase timeout in API calls
- ✅ Deploy backend and frontend in same region

## 📚 Dependencies

- **Dash** - Web framework for building analytical web applications
- **Dash Bootstrap Components** - Bootstrap themes and components
- **Dash AG Grid** - Professional data grid component
- **Pandas** - Data manipulation and analysis
- **Requests** - HTTP library for API calls
- **Gunicorn** - Production WSGI server

## 🤝 Contributing

Feel free to submit issues or pull requests!

## 📄 License

See main project LICENSE file.
