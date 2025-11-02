# AutoIPIndia React Frontend

Modern, professional React + TypeScript frontend for managing Indian trademark statuses.

## ✨ Features

- 🎨 **Modern UI** - Built with React 18 + TypeScript + TailwindCSS
- 📊 **Advanced Data Table** - TanStack Table with sorting, filtering, pagination
- ⚡ **Fast & Responsive** - Vite for lightning-fast development and builds
- 🔄 **Real-time Updates** - TanStack Query for data fetching and caching
- 🎯 **Type-Safe** - Full TypeScript coverage for better DX
- 🔐 **Secure** - Bearer token authentication
- 🐳 **Production-Ready** - Multi-stage Docker build with Nginx
- 📱 **Mobile Friendly** - Responsive design works on all devices

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see `../backend`)

### Local Development

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env
# Edit .env:
#   VITE_API_BASE_URL=http://localhost:8000
#   VITE_API_TOKEN=your-token-from-backend

# 3. Start development server
npm run dev
```

Visit: **http://localhost:3000**

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

## 🐳 Docker Deployment

### Build & Run

```bash
# Build with environment variables
docker build \
  --build-arg VITE_API_BASE_URL=https://your-backend-url.com \
  --build-arg VITE_API_TOKEN=your-secret-token \
  -t autoipindia-react .

# Run container
docker run -d -p 80:80 --name autoipindia-react autoipindia-react
```

Visit: **http://localhost**

### Using docker-compose

```yaml
version: '3.8'
services:
  frontend:
    build:
      context: .
      args:
        VITE_API_BASE_URL: http://backend:8000
        VITE_API_TOKEN: ${API_TOKEN}
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 🌐 Deployment Options

### 1. **Vercel** (Recommended - Best for React)

**Why Vercel:**
- ✅ Built by Next.js team, optimized for React
- ✅ Free tier with great performance
- ✅ Auto-deploy from Git
- ✅ CDN + Edge network
- ✅ Zero configuration

**Steps:**

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Set environment variables in Vercel dashboard:
   - `VITE_API_BASE_URL`: Your backend URL
   - `VITE_API_TOKEN`: Your API token

**Cost:** Free tier (no credit card required)

---

### 2. **Netlify** (Great for static sites)

**Why Netlify:**
- ✅ Easy deployment
- ✅ Free tier
- ✅ Built-in CI/CD
- ✅ Instant cache invalidation

**Steps:**

1. Create `netlify.toml`:
   ```toml
   [build]
     command = "npm run build"
     publish = "dist"
   ```

2. Deploy via CLI:
   ```bash
   npm install -g netlify-cli
   netlify deploy --prod
   ```

3. Set environment variables in Netlify dashboard.

**Cost:** Free tier available

---

### 3. **Google Cloud Run** (Scalable, same as backend)

**Why Cloud Run:**
- ✅ Runs alongside backend
- ✅ Auto-scales to zero
- ✅ Pay per request
- ✅ HTTPS included

**Steps:**

```bash
# Build and push
docker build \
  --build-arg VITE_API_BASE_URL=https://your-backend.run.app \
  --build-arg VITE_API_TOKEN=your-token \
  -t gcr.io/YOUR_PROJECT/autoipindia-react .

gcloud builds submit --tag gcr.io/YOUR_PROJECT/autoipindia-react

# Deploy
gcloud run deploy autoipindia-react \
  --image gcr.io/YOUR_PROJECT/autoipindia-react \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Cost:** Free tier includes 2M requests/month

---

### 4. **AWS S3 + CloudFront** (Static hosting)

**Why S3:**
- ✅ Very cheap
- ✅ Highly available
- ✅ CloudFront CDN
- ✅ Good for production

**Steps:**

1. Build:
   ```bash
   npm run build
   ```

2. Upload to S3:
   ```bash
   aws s3 sync dist/ s3://your-bucket --delete
   ```

3. Configure CloudFront distribution pointing to S3 bucket.

**Cost:** ~$1-5/month depending on traffic

---

### 5. **Docker + Any Cloud Provider**

Works on:
- **Railway** - `railway up`
- **Render** - Connect Git repo
- **DigitalOcean** - App Platform
- **Azure** - Container Instances
- **Heroku** - Container registry

---

## 📁 Project Structure

```
react_fe/
├── src/
│   ├── components/        # React components
│   │   ├── Dashboard.tsx      # Main dashboard layout
│   │   ├── StatsCards.tsx     # Statistics cards
│   │   ├── AddTrademarkForm.tsx  # Form for adding trademarks
│   │   └── TrademarkTable.tsx # Data table with sorting/filtering
│   ├── hooks/            # Custom React hooks
│   │   └── useTrademarks.ts   # Data fetching hook
│   ├── services/         # API clients
│   │   └── api.ts            # Axios-based API client
│   ├── types/            # TypeScript types
│   │   └── index.ts          # Type definitions
│   ├── App.tsx          # Root component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles (Tailwind)
├── public/              # Static assets
├── Dockerfile           # Multi-stage production build
├── nginx.conf           # Nginx configuration
├── package.json         # Dependencies
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite config
└── tailwind.config.js   # Tailwind config
```

## 🎨 Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI framework | 18.2+ |
| **TypeScript** | Type safety | 5.2+ |
| **Vite** | Build tool | 5.0+ |
| **TailwindCSS** | Styling | 3.4+ |
| **TanStack Table** | Data grid | 8.11+ |
| **TanStack Query** | Data fetching | 5.14+ |
| **Axios** | HTTP client | 1.6+ |
| **Lucide React** | Icons | Latest |
| **date-fns** | Date formatting | 3.0+ |

## 🔧 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_BASE_URL` | Yes | Backend API URL | `http://localhost:8000` or `https://api.example.com` |
| `VITE_API_TOKEN` | Yes | API authentication token (must match backend) | `your-secret-token-123` |

**Note:** All Vite env vars must be prefixed with `VITE_` to be exposed to the browser.

## 💻 Development

### Available Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- TypeScript strict mode enabled
- ESLint for linting
- Functional components with hooks
- TailwindCSS for styling (no CSS modules)

## 🎯 Features Walkthrough

### 1. **Dashboard Overview**
   - Real-time statistics cards (total, registered, pending, other)
   - Color-coded status indicators
   - Refresh all button

### 2. **Add New Trademark**
   - Enter Application Number OR (Wordmark + Class)
   - One-click ingestion
   - Success/error feedback
   - Automatic table refresh

### 3. **Interactive Table**
   - **Sort**: Click column headers
   - **Search**: Global search across all fields
   - **Filter**: Real-time filtering
   - **Paginate**: 20 items per page
   - **Select**: Click row to highlight
   - **Re-ingest**: Button per row to refresh that trademark

### 4. **Status Colors**
   - 🟢 Green: Registered
   - 🟡 Yellow: Pending/Examination
   - ⚪ Gray: Other statuses

## 🔒 Security

- Environment variables for config (never commit .env)
- Bearer token authentication
- Nginx security headers in production
- No sensitive data in client-side code
- HTTPS recommended for production

## 🐛 Troubleshooting

### "Network Error" or CORS issues
- ✅ Check `VITE_API_BASE_URL` is correct
- ✅ Ensure backend is running and accessible
- ✅ Verify backend has CORS enabled for your frontend domain
- ✅ Check `VITE_API_TOKEN` matches backend

### Build fails
- ✅ Run `npm install` to ensure all dependencies are installed
- ✅ Check Node.js version (18+)
- ✅ Clear cache: `rm -rf node_modules package-lock.json && npm install`

### Table not loading
- ✅ Open browser console (F12) and check for errors
- ✅ Verify API token is correct
- ✅ Check backend `/retrieve/all` endpoint is working

### Styles not applying
- ✅ Ensure TailwindCSS is properly configured
- ✅ Check `index.css` imports Tailwind directives
- ✅ Clear browser cache

## 🆚 Comparison: React vs Dash

| Feature | React Frontend | Dash Frontend |
|---------|---------------|---------------|
| **Language** | TypeScript/JavaScript | Python |
| **Performance** | Faster (client-side) | Good |
| **Customization** | Unlimited | Good |
| **Learning Curve** | Steeper | Easier (if you know Python) |
| **Ecosystem** | Massive | Smaller |
| **Deployment** | More options | Python hosting needed |
| **Mobile Experience** | Excellent | Good |
| **Best For** | Public-facing, custom UIs | Internal tools, data apps |

**When to use React:**
- You need pixel-perfect custom design
- Public-facing application
- Team has JS/TS experience
- Need maximum performance

**When to use Dash:**
- Python-only team
- Internal admin tool
- Rapid prototyping
- Data science focus

## 🤝 Contributing

Contributions welcome! Please follow the existing code style and add tests where applicable.

## 📄 License

See main project LICENSE file.

---

## 🎉 What's Included

✅ Modern React 18 with TypeScript
✅ Vite for fast development
✅ TailwindCSS for styling
✅ TanStack Table for advanced data grid
✅ TanStack Query for data fetching
✅ Responsive design
✅ Dark mode ready (easy to add)
✅ Production-optimized Docker build
✅ Nginx with caching & compression
✅ Full TypeScript coverage
✅ ESLint configuration
✅ Multiple deployment guides

**Ready to deploy!** 🚀
