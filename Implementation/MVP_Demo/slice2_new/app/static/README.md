# Step 5A-2 — UI formatting patch + continuity audit

## Installation
Back up your current `static/index.html`, then replace it with the included `index.html`. No route, model, or adapter replacement is included. You already fixed the `AnalysisDraft.snapshot_id != snapshot_id` issue; retain that fix.

## What this patch changes
- Percent fields include `profit_margin`, `earnings_growth`, `return_on_assets`, and related metrics. Normalized ratio input `0.125` renders `12.50%`. It does **not** use the unsafe `abs(value) <= 1` heuristic. **Verify provider-normalized units before use.**
- `target_low`, `target_consensus`, and `target_high` use a common currency formatter. Currency is read from the current snapshot, falling back to USD if absent. For ambiguous `$` currencies, the explicit code is used for non-USD snapshots.
- Common valuation multiples render with `x`; no backend behavior is modified.

## Tests
`node tests/format_test.js index.html`
`python tests/test_continuity.py`

The continuity tests use a frozen copy of the prior Step5A report-context implementation for regression reference. They are **not** live tests of your running backend.

## Backend acceptance tests to run against your local app
1. Initial: sync a never-before-analyzed ticker and generate its first report. Expect `initial`, no previous report.
2. Follow-up: sync same ticker after meaningful evidence change. Expect `previous_report_id` pointing to the first report; check actual evidence delta.
3. Same snapshot duplicate: POST analysis for the same snapshot twice with `force_refresh=false`. Verify identical report ID and exactly one AI provider call.
4. Cross-snapshot duplicate: create a new snapshot with the same normalized evidence and generate a report. Expect zero new provider calls **only after** implementing company+evidence content hash+model+prompt version reuse. The reference Step5A currently hashes snapshot-specific review context and may miss this case.
5. Small price move: verify that a trivial change does not trigger an expensive full follow-up after introducing materiality thresholds. The reference Step5A currently marks any change material.
6. Historical order: the previous snapshot/report must predate the current snapshot; avoid selecting a later snapshot merely because it is the newest row other than the current one.

## Proposed minimal backend follow-up (not automatically patched)
- Add a separate stable analysis-cache key from canonical normalized evidence, model, prompt version and **relevant** thread context; do not include snapshot IDs. Keep the full input hash for audit. Reuse the prior report if the evidence cache key matches and no manual force-refresh is requested.
- For the initial MVP, classify small price changes as `low_change`; materiality should depend on configurable thresholds and meaningful financial/event changes. Record the deterministic delta even when not material.
- Ensure previous snapshot/report selection uses a strict earlier-than-current timestamp or monotonically increasing ID where guaranteed.

## Deferred to Step 6
ResearchReport, ResearchThread, ThreadVersion, ThreadAction, and PersonalResearchNote (append-only; user-authored, distinct from AI output). A journal entry may refer to a company, report, thread, thesis assumption, intended action, and later review outcome. Do not infer real trading P&L from notes alone.
