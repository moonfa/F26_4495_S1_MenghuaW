# Step 6 — Research History & Thread Continuity

Status: implementation plan; not yet deployed or verified against the user's running database.

## Scope
Preserve working Slice 1 evidence sync, normalized snapshot, Step5A one-pass report generation, existing integer primary keys, and the user's fixed `AnalysisDraft.snapshot_id != snapshot_id`. No React rewrite. Historical reports are immutable; AI thread actions are proposed, not auto-applied.

## Pre-migration gates (Step5A-2 regression fixes)
1. Force-review failure leaves the last successful report rendered and stored. Display an error banner separately; never replace the report with an error. Pending and failed drafts do not appear as successful history.
2. `force_refresh` bypasses report reuse; if button says **Force Full Review**, explicitly set a `full_follow_up` review mode (or `initial` if no earlier report), instead of only bypassing cache. Persist the requested and actual review modes.
3. Use a stable evidence-reuse key (company + canonical normalized evidence content hash + AI model + prompt version + relevant thread-context version); exclude snapshot ID and volatile request timestamps. Check prior successful report across snapshots. Preserve a separate full input hash for auditing. A forced full review bypasses this cache.
4. Low-change classification is separate from cache-hit status. Expose `cache_hit`, `reused_report_id`, and `provider_called` in development diagnostics. Verify using an instrumented mock AI provider; don't infer from `low_change` alone.
5. Select prior snapshot/report strictly earlier than current snapshot by timestamp, with ID as deterministic tie-breaker.
6. Introduce deterministic materiality thresholds, initially as configuration, and unit-test price-only changes, financial changes, news-only changes, and missing data.

## Incremental schema (additive migration)
Existing `Company`, `Source`, `EvidenceSnapshot`, and `AnalysisDraft` remain intact. Add new tables using the existing integer PK/FK conventions:

### ResearchReport
`id` integer PK; `company_id` FK; `snapshot_id` FK; `source_analysis_draft_id` unique nullable FK (compatibility/backfill); `previous_report_id` nullable self-FK; `created_at`; `status` (`success` only in visible history); `review_type`; `material_change`; `model`; `prompt_version`; `evidence_content_hash`; `input_hash`; `cache_key`; `report_markdown`; `key_takeaways` JSON; `what_changed`; `evidence_delta` JSON; `input_tokens` nullable; `output_tokens` nullable. Immutable once successful. Index `(company_id, created_at DESC, id DESC)`.

### ResearchThread
`id` integer PK; `company_id` FK; `title`; `thread_type` nullable; `status` (`active`, `watching`, `dormant`, `archived`); `importance`; `created_at`; `last_active_at`. Stable identity across reports; do not create all archetype candidates automatically.

### ThreadVersion
`id` integer PK; `thread_id` FK; `report_id` FK; `state_summary`; `importance`; `importance_change`; `created_at`; `valid_from` nullable; `valid_to` nullable. Append a new version on each approved material change; keep historical content immutable. If valid_to needs adjustment, treat it as a derived view or explicitly document the metadata exception to append-only.

### ThreadAction
`id` integer PK; `report_id` FK; `thread_id` nullable FK; `action` (`continue`, `update`, `create`, `deprioritize`, `close`, `ephemeral`); `title`; `importance`; `importance_change`; `change_summary`; `review_status` (`proposed`, `approved`, `rejected`, `edited`); `reviewer_note`; `reviewed_at`; `created_at`. AI creates proposals only; approved changes applied in one database transaction. `ephemeral` remains report-local.

### PersonalResearchNote
`id` integer PK; `company_id` FK; `report_id` nullable FK; `thread_id` nullable FK; `created_at`; `note_type` (`hypothesis`, `valuation_assumption`, `planned_action`, `review_outcome`, `general`); `body`; `valuation_assumptions` JSON nullable; `review_due_at` nullable; `supersedes_note_id` nullable self-FK. User-authored, never overwritten by AI. No inferred trade P&L without explicit execution records.

## Migration strategy
1. Add tables with Alembic (or explicit versioned SQL migration); never use `create_all` as a substitute for production migrations.
2. Backfill successful `AnalysisDraft` records into `ResearchReport` using unique `source_analysis_draft_id`; do not backfill failed/pending drafts. Preserve original snapshot and timestamps. Link `previous_report_id` per company in chronological order only where appropriate; identify reused report references rather than duplicating report text.
3. Dual-read compatibility temporarily: new history API prefers ResearchReport; legacy AnalysisDraft remains readable during transition. Avoid dual-writing without transaction boundaries and idempotency.
4. Add proposal persistence from existing Step5A `thread_actions` JSON after a successful report. Require user approval before creating/updating ResearchThread or ThreadVersion.
5. Add PersonalResearchNote endpoints and a minimal input UI after the report/thread flow passes tests.

## Minimal APIs
- `GET /api/v1/companies/{ticker}/reports?limit=20&cursor=...` — successful history, newest first, no external calls.
- `GET /api/v1/reports/{report_id}` — full saved report, evidence snapshot ID, linked thread actions.
- `GET /api/v1/companies/{ticker}/threads` — current thread list.
- `GET /api/v1/threads/{thread_id}/timeline` — chronological versions, linked reports, evidence and user notes.
- `POST /api/v1/thread-actions/{action_id}/review` — approve/reject/edit; enforce valid transitions and idempotency.
- `GET/POST /api/v1/companies/{ticker}/notes` — personal journal; optional report/thread associations.

## UI delivery (Step 6 minimal, Step 7 full)
Step 6 minimal: below existing report, add **Report History** list and **Proposed Thread Actions** review controls. When a request fails, keep last successful report visible. Clicking history must read the database only. Step 7: sidebar company watchlist, Overview/Financials/Research/News tabs, thread timelines, full personal journal, Yahoo Finance links and visible freshness labels.

## Acceptance tests
A. Failed forced request retains prior report and adds only a failed attempt; no partial ResearchReport.
B. Two analyses on same snapshot return same successful report with zero additional provider calls unless forced.
C. Two different snapshots with identical canonical evidence and identical AI context reuse the same successful report; preserve both snapshot records and explain the reuse relationship.
D. A forced full review generates a new full report, with requested and actual review mode recorded.
E. Two reports on different dates have correct previous_report_id and independently retrievable evidence.
F. Proposed thread action does not mutate a thread until approved; approval creates exactly one version; retry is idempotent; rejection creates none.
G. Personal notes remain user-authored, timestamped and linked to the intended report/thread.
H. All historical views work with AI and market-data providers unavailable.

## Deferred
No trading execution/P&L engine, autonomous buy/sell actions, portfolio broker integration, chart/K-line dependency, or React migration in Step 6. Analyst target prices are third-party estimates, not the application's own price forecasts.
