# Step 8 — Research Lifecycle & Update Intelligence

## Goal
Step 8 changes the workbench from a "new snapshot → new full report" workflow into a longitudinal research lifecycle:

`Thesis → Drivers / Risks → New Evidence → Human Review → Historical Report`

A full Master Research Report remains a low-frequency historical anchor. Small evidence changes no longer create repetitive full reports.

## What is added

### 1. Watchlist lifecycle
Companies have a research status: `watching`, `following`, or `archived`. Removing a company from the main Watchlist moves it to Following; it does **not** delete Evidence Snapshots, reports, threads, versions, or personal notes.

### 2. Three update levels
- **Evidence Update** — deterministic small change; stored without an AI call.
- **Research Update** — targeted AI analysis of driver/risk and valuation-input implications.
- **Material change** — the targeted update can recommend a Full Review, but the system never generates the full report automatically.

`Generate Full Review` is the manual override / low-frequency action that creates a complete Master Research Report.

### 3. Unified Research Timeline
The timeline combines Evidence/Research Updates, Full Reviews, and Personal Research Notes into a chronological research-memory view. Existing ResearchReport and Thread history is preserved.

### 4. Compact history and thread areas
Historical reports, active threads, and the timeline use bounded scroll regions so the Research workspace remains usable as history grows.

### 5. Report language
The report language selector supports `English` and `中文`.
- Structured enum values remain canonical English (`up`, `medium`, `high`, etc.).
- Natural-language AI fields use the selected language.
- Historical reports are not overwritten when the language changes.
- English remains the default for assignment/demo output.

## Valuation scope
Valuation remains an implication/check layer, not the center of the product. Research Updates may indicate whether `base_metric` or `multiple` assumptions deserve review. The AI does not automatically change assumptions or calculate a new fair value.

## Data model additions
- `company_research_state`
- `research_updates`
- additive `language` metadata on `research_reports`

No existing Step 6 tables are deleted or replaced.

## News behavior
News remains evidence supplied by the current OpenBB/yfinance snapshot. An empty News panel means the provider returned no news items for that snapshot; Step 8 does not fabricate missing news. Separate provider-specific news refresh is intentionally deferred because the current adapter fetches the evidence bundle together.

## Installation
Stop Uvicorn and run from the existing `Implementation/MVP_Demo/slice2_new` project directory:

```bash
python3 /path/to/Step8_Research_Lifecycle/install_step8.py .
python3 -m app.step8.migrate
python3 -m uvicorn app.main:app --reload
```

Then hard-refresh the browser (`Cmd + Shift + R` on macOS).

The installer creates a source/database safety backup outside `slice2_new`. The migration also creates a timestamped SQLite backup before schema changes.

## Acceptance test
1. Existing WMT reports, threads, and notes still load.
2. Add a ticker to Watchlist; refresh evidence once if the company does not exist yet.
3. Click `−`: the company moves to Following and its history remains intact.
4. Restore it: history reappears immediately.
5. Refresh Evidence, then choose **Analyze New Evidence**.
6. A small change becomes an Evidence Update without a Gemini full-report call.
7. A research-relevant change creates a targeted Research Update.
8. A material change may show `Full review recommended`, but no full report is automatically generated.
9. **Generate Full Review** still creates the complete Master Research Report on explicit user request.
10. Switch Report Language to 中文 and create a new AI update/full review; natural-language output is Chinese while structured enums remain English.
11. Existing historical English reports remain unchanged.

## Scope intentionally deferred
- Automatic fair-value recalculation and valuation-model management
- Position/cost-basis portfolio accounting
- Independent news-provider refresh endpoint
- Automatic full-report generation
- Machine translation of old historical reports
