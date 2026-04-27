# EliseAI GTM Tool — SDR Acceleration Platform

Automated lead enrichment and SDR acceleration tool for EliseAI sales team.

## Overview

This tool transforms basic inbound leads into **SDR-ready opportunities** with:
- Market intelligence (Census, FRED)
- Company signals (NewsAPI, Wikipedia)
- Lead scoring (Tier A/B/C)
- Personalized email drafts
- Talking points for sales calls
- Deal-closing context (buying signals, objections, ROI)


<img width="503" height="502" alt="image" src="https://github.com/user-attachments/assets/30eb2c29-2e01-43b3-87a0-7d9f8bfed16b" />


## Quick Start

### 1. Install Dependencies

```bash
cd GTM
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `.env` file with your API keys:
```
GROQ_API_KEY=your_groq_key
CENSUS_API_KEY=your_census_key
FRED_API_KEY=your_fred_key
NEWS_API_KEY=your_newsapi_key
```

### 3. Run Backend

```bash
python main.py
```

Backend runs at `http://localhost:8000`

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

## Features

### SDR Toolkit
| Feature | Description |
|---------|-------------|
| **Lead Scoring** | Tier A/B/C based on ICP fit |
| **Talking Points** | 3 conversation starters per lead |
| **Email Draft** | Personalized, editable templates |
| **Buying Signals** | Expansion, funding, leadership changes |
| **Objection Handling** | Pre-built responses |
| **ROI Calculator** | Prospect-specific estimates |
| **Case Studies** | Social proof from similar operators |
| **Benchmarks** | Market vs industry comparison |

### APIs Used
| API | Data Retrieved |
|-----|---------------|
| **Census ACS** | Renter %, vacancy, income, renter units |
| **FRED** | Rent growth YoY |
| **NewsAPI** | Company news headlines |
| **Wikipedia** | Company summary |

### Scoring Logic

**Tier A (Priority — contact within 24h):**
- National operators (Greystar, Camden, Equity Residential, etc.)
- OR Markets with >40% renter population
- OR Recent expansion/funding signals

**Tier B (Follow Up — contact within 48h):**
- Regional/mid-market operators
- Growing Sun Belt metros (Austin, Phoenix, Atlanta)

**Tier C (Nurture — automated sequence):**
- Small local operators
- Markets with <30% renter population

### Automation

| Trigger | Description |
|---------|-------------|
| **Manual** | Button in dashboard |
| **Daily Schedule** | 9am ET via APScheduler |
| **Google Sheets** | Auto-process new rows |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/enrich` | POST | Enrich single lead |
| `/batch` | POST | Enrich multiple leads |
| `/sync-sheets` | POST | Sync with Google Sheets |
| `/trigger` | POST | Manual trigger |
| `/health` | GET | Service health |

## Project Structure

```
GTM/
├── agent/                 # Core agents
│   ├── router.py         # Lead router (strategy A/B/C)
│   ├── enrichment.py     # API executor
│   ├── pipeline.py       # Unified pipeline
│   └── validator.py     # Output validator
├── config/
│   └── strategies.py    # Routing rules
├── integrations/
│   └── sheets.py       # Google Sheets
├── tools/
│   ├── census_api.py  # Census API
│   ├── fred_api.py    # FRED API
│   └── news_api.py    # News/Wikipedia API
├── automation.py       # Scheduling
├── main.py            # FastAPI backend
└── prompts.py         # System prompts

frontend/
├── src/
│   ├── app/           # Next.js app
│   │   ├── page.tsx  # Main dashboard
│   │   └── api/enrich/ # API route
│   ├── components/    # UI components
│   │   ├── LeadDetail.tsx
│   │   ├── EmailPreview.tsx
│   │   ├── TalkingPoints.tsx
│   │   ├── BuyingSignals.tsx
│   │   ├── ObjectionPrep.tsx
│   │   ├── ROICalculator.tsx
│   │   ├── CaseStudy.tsx
│   │   └── IndustryBenchmark.tsx
│   └── types/         # TypeScript types
└── package.json
```

## Deployment

### Vercel (Frontend)
```bash
cd frontend
vercel deploy
```

### Railway/Render (Backend)
1. Push code to GitHub
2. Connect to Railway/Render
3. Set environment variables
4. Deploy

## Success Metrics

- **Time saved**: 45 min per lead (manual → automated)
- **Tier A response**: <24 hours
- **Validation score**: >80%
- **SDR adoption**: Daily active users

## License

Internal use only — EliseAI
