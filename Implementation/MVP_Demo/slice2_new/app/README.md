# Step 5A-1 — Integration Cleanup

This patch replaces the front-end entry page only.

## Replace

Copy:

`static/index.html`

into the existing project and replace the current `static/index.html`.

## Backend contracts used

- `POST /api/v1/evidence/sync`
- `POST /api/v1/analysis/evidence/{snapshot_id}`

No backend route or database schema change is required for this cleanup.

## What the page now shows

### Slice 1 — Evidence Layer

- Company information
- Market Snapshot
- Valuation Context
- Financial Health
- Analyst Consensus
- Data Quality / missing sections / warnings
- Recent News
- Snapshot/provider/retrieval metadata

### Slice 2 + Step 5A — AI Research Layer

- Review Type
- Material Change
- Previous Snapshot / Previous Report
- What Changed
- Evidence Delta (collapsible JSON)
- Key Takeaways
- Thread Actions
- Full Master Research Report

## Flow

`Sync Evidence`

→ receives the normalized snapshot from `/evidence/sync`

→ renders the full Evidence Snapshot

→ stores `snapshot_id`

→ enables `Generate AI Review`

→ `/analysis/evidence/{snapshot_id}` consumes the current snapshot

→ renders the Step 5A research output without replacing the evidence view.

## Important

The page does not add K-line/chart collection.

The page does not send raw provider payloads to the browser beyond what the existing API returns.

The known backend query bug has already been fixed separately:

`AnalysisDraft.snapshot_id != snapshot_id`

Do not reapply an older Step 5A route file that contains the incorrect `AnalysisDraft.id != snapshot_id` comparison.
