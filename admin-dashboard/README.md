# Daily Quote Admin Dashboard

A comprehensive admin interface for managing the Daily Quote project's backend processes, analytics, and content.

## Project Structure

```
admin-dashboard/
├── src/                    # React frontend source code
│   ├── components/         # Reusable UI components
│   ├── pages/             # Page components
│   ├── hooks/             # Custom React hooks
│   ├── store/             # Redux store configuration
│   ├── services/          # API service functions
│   ├── utils/             # Utility functions
│   └── types/             # TypeScript type definitions
├── public/                # Static assets
├── api/                   # FastAPI backend
│   ├── routers/           # API route handlers
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   ├── utils/             # Backend utilities
│   └── tests/             # API tests
└── docs/                  # Additional documentation
```

## Features

### 📊 Dashboard Overview
- System health monitoring
- Real-time quote statistics
- Sentiment analysis overview
- Recent activity feed

### 📝 Quote Management
- File browser and editor
- Database CRUD operations
- Duplicate detection and cleanup
- Import/export functionality

### 🎭 Sentiment Analysis
- Visual sentiment distribution
- Batch processing controls
- Detailed analysis views
- Export capabilities

### 🔍 Vector Management
- Vector generation and visualization
- Similarity analysis
- Clustering insights
- Recommendation engine

### 🔧 System Monitoring
- Process status tracking
- Error log management
- Performance metrics
- API monitoring

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Git

### Frontend Setup
```bash
cd admin-dashboard
npm install
npm run dev
```

### Backend Setup
```bash
cd admin-dashboard/api
pip install -r requirements.txt
uvicorn main:app --reload
```

### Database Setup
```bash
# Initialize database
python scripts/init_db.py

# Run migrations
alembic upgrade head
```

## Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run test` - Run tests
- `npm run lint` - Run ESLint

### API Development
- `uvicorn main:app --reload` - Start API server
- `pytest` - Run API tests
- `alembic revision --autogenerate` - Create migration

## Deployment

### Frontend (Netlify/Vercel)
```bash
npm run build
# Deploy dist/ folder
```

### Backend (Docker)
```bash
docker build -t daily-quote-admin .
docker run -p 8000:8000 daily-quote-admin
```

## Contributing

1. Create feature branch from `v2.0`
2. Make changes and add tests
3. Submit pull request
4. Ensure CI passes

## License

Same as parent project - see LICENSE file.
