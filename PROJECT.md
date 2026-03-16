# StreamFinder 🎬

## What We're Building
A web app that lets users search for any movie or TV show and see which streaming services carry it — filtered by country (Singapore-first, 24+ countries supported).

## Tech Stack
- **Framework:** Next.js 14 (React)
- **Styling:** Tailwind CSS
- **Data:** TMDB API (free, official) — uses their JustWatch-powered watch provider data
- **Hosting:** Vercel (free tier) — builds in the cloud, avoids server RAM issues

## File Structure
```
streamfinder/
├── pages/
│   ├── index.js          ← Main search page
│   ├── _app.js           ← App wrapper
│   └── api/
│       ├── search.js     ← TMDB search endpoint
│       └── providers.js  ← Streaming availability endpoint
├── components/
│   ├── ResultCard.js     ← Movie/show card with expandable streaming info
│   ├── ProviderBadges.js ← Streaming service logos + type labels
│   └── CountrySelector.js← Country dropdown (24+ countries)
├── styles/globals.css
├── .env.local            ← API key (never commit this!)
└── .env.local.example    ← Template for API key
```

## Environment Variables
```
TMDB_READ_TOKEN=<your TMDB Read Access Token>
```

## How to Run Locally
```bash
npm install
cp .env.local.example .env.local
# Edit .env.local with your TMDB token
npm run dev
# Visit http://localhost:3000
```

## How to Deploy (Vercel)
1. Push code to GitHub
2. Connect repo to Vercel (vercel.com)
3. Add TMDB_READ_TOKEN in Vercel environment variables
4. Deploy ✅

## Status
- [x] Project scaffolded
- [x] API routes built (search + providers)
- [x] UI components built
- [x] Country selector (24+ countries, SG default)
- [ ] API key added
- [ ] Deployed to Vercel

## Countries Supported
SG, US, GB, AU, IN, CA, DE, FR, JP, KR, MY, ID, TH, PH, NZ, ZA, BR, MX, ES, IT, NL, SE, NO, AE
