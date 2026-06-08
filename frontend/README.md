# CreditSentinel Frontend

React UI for the CreditSentinel demo. The app supports mock-first development so the UI keeps working even when ngrok APIs are down.

## Quick start

```bash
npm install
npm start
```

App runs at http://localhost:3000

## Configuration

Edit the API base URLs and mock toggle in:

- src/api/config.js

Key settings:

- USE_MOCK: true or false
- APPLICATIONS_API: Divya applications + score API base
- REDFLAGS_API: Guru Prasad red flags API base
- MEMO_API: Yuva Teja memo API base

When USE_MOCK is true, the UI uses local mock data and fallbacks. When false, it calls the live APIs and falls back to mocks if any request fails.

## Mock data

Mock data lives in:

- src/mocks/mockData.js

It includes:

- mockApplications: application list
- mockRedFlags: red flag responses by application_id
- mockRiskScores: risk score responses by application_id
- mockMemos: memo responses by application_id
- defaultMockMemo: fallback memo if no match

## Main UI

The main React app is in:

- src/App.js

Key screens and behaviors:

- Dashboard: shows summary counts
- Applications: list view, click row to open detail
- Application Detail:
  - Risk score uses risk_score and risk_tier
  - Risk score is shown as percent: (risk_score * 100).toFixed(1)
  - Red flags show rule and evidence text
  - Generate Memo calls /api/memo and renders sections in cards
  - Memo uses a spinner while loading
- Risk Score page: form submits to /api/score

## API contracts

Expected responses used by the UI:

- /api/score
  - risk_score (number between 0 and 1)
  - risk_tier (Low, Medium, High)

- /api/redflags
  - flags: array of { rule, evidence, severity }

- /api/memo
  - supports either { sections: [ { title, content } ] } or key/value object
  - UI normalizes common shapes into card sections

## Project structure

Top level:

- public/index.html: main HTML template
- src/index.js: app bootstrap
- src/index.css: global styles
- src/App.js: main UI
- src/api/config.js: API configuration
- src/mocks/mockData.js: mock data

## Notes

- If live APIs do not include income or loan fields in /api/applications, the list will show N/A unless you use mock mode.
- If memo API is down, the UI falls back to mock memos automatically.
