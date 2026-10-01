# Step 7 — Unified Research Workspace

## Purpose

Step 7 reorganizes the working Step 6 domain into a single research workspace. It does not change the core research logic or introduce React.

The product workflow remains:

`Thesis → Drivers / Risks → New Evidence → Human Review → Historical Report`

Valuation Implication remains a result/check layer inside research reports.

## UI delivered

- Left watchlist: WMT, MRVL, MCD, UBER, GOOGL.
- Company header with local evidence/report/thread freshness indicators.
- Four tabs: Overview, Financials, Research, News.
- Overview: current saved Evidence Snapshot and company/market context.
- Financials: focused Valuation Context, Financial Health and Analyst Consensus.
- Research: Historical Master Research Reports, Active Research Threads, Thread timeline, Personal Research Journal, current Master Research Report and Valuation Implication.
- News: recent news contained in the current Evidence Snapshot.

## External-call boundary

Selecting a watchlist company or clicking **Load Saved Research** reads local database history only. **Refresh Evidence** is the explicit provider call. **Generate AI Review** and **Force Full Review** are the explicit AI calls.

## Installation

Install this only after Step 6.1 is working. From `Implementation/MVP_Demo/slice2_new`:

```bash
python3 ~/Downloads/Step7_Research_Workspace/install_step7.py .
python3 -m uvicorn app.main:app --reload
```

Hard refresh the browser after restart. Step 7 does not require a database migration because this delivery reorganizes the existing Step 6/6.1 data and APIs.

## Acceptance checks

1. Click WMT/MRVL/MCD/UBER/GOOGL in the watchlist. The app loads saved local research without a provider/AI call.
2. Overview displays the latest locally saved Evidence Snapshot.
3. Financials displays the same snapshot's valuation, financial health and consensus sections.
4. Research displays history, Threads, Journal and a selected/current Master Research Report.
5. News displays the same snapshot's recent-news evidence.
6. Refresh Evidence remains explicit; Generate AI Review remains explicit.
7. Step 6.1 Edit & Approve and ThreadVersion continuity continue to work inside the Research tab.

## Intentionally deferred

No K-line chart, no automatic Fair Value recalculation, no portfolio P&L/trade ledger, no React migration, and no separate valuation-driver subsystem.
