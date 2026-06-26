# CreditSentinel Frontend

An interactive React UI for the CreditSentinel demo. It provides comprehensive credit analysis tools, risk profiling dashboards, real-time alert metrics, dynamic credit memo generators, and analyst decision logs. 

The application is built using a mock-first development pattern, enabling full UI operations even when background APIs are offline.

---

## Quick Start

Ensure you have Node.js installed, then run:

```bash
npm install
npm start
```

The application will run locally at [http://localhost:3000](http://localhost:3000).

---

## Key Features

### 1. Loan Approval Dashboard
- **Access Route**: `/dashboard/approvals` (Implemented in [src/pages/ApprovalDashboard.jsx](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/pages/ApprovalDashboard.jsx))
- **Live Metrics**: Displays Total Applications, Approved, Rejected, Under Review counts, Today's Decisions, Approval Rates, and Rejection Rates.
- **Trend Charts**: Renders interactive Weekly Approval Trend charts, Status distribution pie charts, and Risk distribution bar charts using `recharts`.
- **Advanced Filtering**: Allows multi-filtering by Application Status, Risk Band (Low/Medium/High), Analyst names, Search terms (applicant name), and Date Range (from/to).
- **Interactive Drill-downs**: Clicking on chart slices (e.g. Approved slice in the Pie chart, or Low risk bar in the Bar chart) automatically filters the application list accordingly.
- **Spike Warning System**: Features real-time alert cards for high rejection rates or low approval rate thresholds.
- **Performance Tools**: Includes API latency tracking and a manual switch to simulate high-latency conditions.

### 2. Export and Reporting
- **PDF Report Generation**: Exports comprehensive, formatted PDF reports featuring summary stats, status charts breakdown, and structured application tables using `jsPDF` and `jspdf-autotable`. Verified in [src/pages/REPORTING_VALIDATION.txt](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/pages/REPORTING_VALIDATION.txt).
- **Excel & CSV Export**: Downloads detailed tabular worksheets of application entries, including ID, Applicant Name, Loan Amount, Status, Decision History, and Approval Reasons via `xlsx` and `file-saver`.

### 3. Application Portfolio and Details
- **Dashboard Overview**: Access route `/` (Home) displays aggregate portfolio counts (Low, Medium, High risk bands) and cached metrics summaries. (Implemented in [src/App.js](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/App.js))
- **Application Detail View**: Access route `/application/:id` shows the applicant profiles, credit parameters (monthly income, CIBIL score, FOIR), automated risk indicators (risk score displayed as percent), and specific red flags (rule violations, severity, and evidence text). (Implemented in [src/App.js](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/App.js))
- **Dynamic Credit Memo**: Features a memo builder that triggers `/api/memo` and normalizes response shapes to render key sections (Executive Summary, Income and Obligations, Red Flags, Recommendation) as styled cards.
- **Decision Panel**: Component [src/components/DecisionPanel.jsx](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/components/DecisionPanel.jsx) is integrated directly within details page, allowing analysts to log audit actions (`APPROVE`, `REVIEW`, `REJECT`) with optional notes (max 500 characters) and review chronological decision audit history.

### 4. Risk Score Simulator
- **Access Route**: `/risk` contains a form to submit financial attributes to the risk classification endpoint `/api/score`. (Implemented in [src/App.js](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/App.js))

---

## Configuration

Edit the active API host URLs and mock-mode toggle in [src/api/config.js](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/api/config.js):

- **`USE_MOCK`**: Set to `true` (default) to force the UI to use offline mock datasets, or `false` to attempt fetching from live servers.
- **`APPLICATIONS_API`**: Base endpoint for credit applications and scores.
- **`REDFLAGS_API`**: Base endpoint for the rule engine checking red flags.
- **`MEMO_API`**: Base endpoint for generating summary memos.

*Note: When `USE_MOCK` is `false`, the client automatically falls back to local mocks if any live request times out or returns an error.*

---

## Mock Data Structures

All mock datasets and fallbacks are defined in [src/mocks/mockData.js](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/mocks/mockData.js):
- **`mockApplications`**: Array containing applicant list items with income, loan request size, FOIR, CIBIL score, and risk bands.
- **`mockRedFlags`**: Table mapping rule violations (Low CIBIL, EMI bounces, Night submissions, etc.) by application ID.
- **`mockRiskScores`**: Simulated risk coefficients and classification bands (Low, Medium, High).
- **`mockMemos`**: Structured memo sections parsed for individual candidates.
- **`mockHistories`**: Decision log trails including audit identifiers, decision states, notes, timestamps, analyst names, and api latencies.

---

## Accessibility and Validation

- **WCAG Compliance**: Tested for contrast, keyboard focus indicators, screen reader accessibility, and layout responsiveness. Verified passing in [src/pages/A11Y_VALIDATION.txt](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/pages/A11Y_VALIDATION.txt).
- **Limitations**: High load latency from backend endpoints is logged; UI handles async loading indicators dynamically. Checked in [src/pages/DEMO_READY_CHECKLIST.md](file:///home/Nihal/Downloads/creditsentinel-1/frontend/src/pages/DEMO_READY_CHECKLIST.md).

---

## Project Structure

```text
frontend/
├── public/
│   └── index.html
├── src/
│   ├── api/
│   │   └── config.js
│   ├── components/
│   │   └── DecisionPanel.jsx
│   ├── mocks/
│   │   └── mockData.js
│   ├── pages/
│   │   ├── A11Y_VALIDATION.txt
│   │   ├── ApprovalDashboard.jsx
│   │   ├── DEMO_READY_CHECKLIST.md
│   │   └── REPORTING_VALIDATION.txt
│   ├── App.js
│   ├── index.css
│   └── index.js
├── .gitignore
├── package.json
└── README.md
```
