Sendra – AI-Powered Email Management System

Sendra is an intelligent email application tracker that uses AI to analyze job-related emails, extract opportunities, and turn them into actionable insights for learners and job seekers.

Sendra is part of a future open-source education startup focused on helping people bridge the gap between theory and real-world practice. Instead of just learning concepts, users work with real data (like emails, applications, and skill signals) to build practical experience and career readiness.

Core Features

Smart Email Analysis

Automatically detects job opportunities, interview invites, rejections, and follow-ups

Extracts important data such as company name, role, skills required, and timelines

Career & Skill Insights

Analyzes skills based on existing emails, applications, and user history

Identifies skill gaps and strengths for specific roles

Interview Preparation

Converts real job opportunities into interview-ready data

Personalized preparation plans for future interviews

Voice AI Practice & Feedback

Practice interviews using Voice AI

Receive post-interview feedback on answers, clarity, and confidence

Email & Application Statistics

Track application success rates

Analyze response times, interview conversion rates, and trends

Role-Specific Training & Tests

AI-generated tests and exercises tailored to specific job roles

Training based on real-world job requirements, not just theory  

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Motor (async MongoDB driver)
- Google Gmail API
- Google Generative AI (Gemini) / OpenAI API
- JWT Authentication

**Frontend:**
- React 18 with React Router
- Zustand (state management)
- Chart.js (visualizations)
- Tailwind CSS (styling)
- Axios (HTTP client)

**Infrastructure:**
- Docker & Docker Compose
- MongoDB (database)
- Nginx (reverse proxy)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Google Cloud Console account (for OAuth credentials)
- Gmail account
- Gemini API key (free) or OpenAI API key (optional)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone and configure
git clone <repo-url>
cd Sendra
cp .env.example .env

# 2. Edit .env with your credentials
# - GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET from Google Console
# - GEMINI_API_KEY from https://aistudio.google.com/app/apikey
# - Optional: OPENAI_API_KEY

# 3. Start services
docker-compose up

# Access at http://localhost
```

### Option 2: Manual Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
npm start
```

## Configuration

### Google OAuth Setup

1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Web application)
3. Add authorized redirect URI: `http://localhost:3000/callback`
4. Copy Client ID and Secret to `.env`

### Gemini API (Free)

1. Go to https://aistudio.google.com/app/apikey
2. Generate API key
3. Add to `.env`

### OpenAI API (Optional)

1. Go to https://platform.openai.com/api-keys
2. Create API key
3. Update `.env` with `OPENAI_API_KEY` and set `LLM_PROVIDER=openai`

## Project Structure

```
Sendra/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── requirements.txt            # Python deps
│   └── src/
│       ├── config.py              # Settings
│       ├── models.py              # Pydantic models
│       ├── dependencies.py         # Auth middleware
│       ├── services/              # Business logic
│       └── routes/                # API endpoints
├── frontend/
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── App.js
│       ├── pages/
│       ├── components/
│       ├── services/
│       └── hooks/
├── nginx.conf                      # Reverse proxy
├── docker-compose.yml              # Orchestration
├── .env.example                    # Config template
├── .gitignore                      # Git exclusions
└── README.md                       # This file
```

## API Reference

### Authentication
- `GET /api/auth/google` - Start OAuth flow
- `POST /api/auth/google/exchange` - Exchange code for token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Gmail & Search
- `POST /api/gmail/natural-query` - Natural language email search
- `POST /api/gmail/sync` - Sync emails

### Analytics
- `GET /api/analytics/dashboard-summary` - Overview metrics
- `GET /api/analytics/by-status` - Status breakdown
- `GET /api/analytics/by-job-type` - Job type breakdown
- `GET /api/analytics/application-funnel` - Conversion funnel

## Troubleshooting

**OAuth redirect_uri_mismatch**
- Check `GOOGLE_REDIRECT_URI` matches Google Console
- Should be: `http://localhost:3000/callback`

**Gemini/OpenAI API errors**
- Verify API key in `.env`
- Check backend logs: `docker-compose logs backend`

**Gmail emails not showing**
- Re-authenticate (logout and login)
- Check Firebase credentials in browser dev tools

**Docker issues**
- Clear containers: `docker-compose down -v`
- Rebuild: `docker-compose up --build`

## License

MIT License

## Contributing

Pull requests welcome!

## Features

- 🤖 Natural language email search ("Show me job offers")
- 📊 Advanced analytics dashboard
- 💼 Smart job application tracking
- 🔐 Google OAuth authentication
- 📈 Application funnel visualization

## Tech Stack

- **Backend**: FastAPI, Motor (async MongoDB), OpenAI/Anthropic
- **Frontend**: React 18, Zustand, Chart.js, Tailwind CSS
- **Database**: MongoDB

## Documentation

See `/docs` folder for detailed guides:
- Setup instructions
- API documentation
- Deployment guides
