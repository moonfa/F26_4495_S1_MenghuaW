# Step 5A — Vertical Slice Test

This patch connects the existing Slice 1 Evidence Layer to the new Master Research Report AI Slice.

## Compatibility strategy

- No new database tables.
- No database migration.
- Existing `Company`, `Source`, `EvidenceSnapshot`, `AnalysisDraft` remain usable.
- Existing `/api/v1/evidence/sync` is preserved.
- Existing `/api/v1/evidence/{ticker}` is preserved.
- Existing `/api/v1/analysis/evidence/{snapshot_id}` is preserved.
- `analysis_type="company_profile"` is retained for API compatibility; internally it now means Master Research Report.
- `AnalysisDraft.output_payload` temporarily stores report lineage / delta metadata. Step 6 will move this to the formal ResearchReport / Thread model.

## Files

- `ai/schemas.py`
- `ai/prompts.py`
- `ai/analyzer.py`
- `ai/provider.py`
- `ai/report_context.py`
- `routes.py`
- `static/step5a.html`
- `main_step5a_route.txt`

## Add the UI route

Add the route in `main.py` exactly as shown in `main_step5a_route.txt`, then open:

`/step5a`

## Environment

For real Gemini:

```env
AI_PROVIDER=gemini
AI_MODEL=gemini-3.8-flash
GEMINI_API_KEY=your_new_key
```

For a local plumbing test without Gemini:

```env
AI_PROVIDER=mock
```

## Test sequence

### Initial Review

1. Open `/step5a`.
2. Enter `WMT`.
3. Click `Sync Evidence`.
4. Click `Generate Review`.
5. Expect `review_type = initial`, `previous_report_id = None`.

### Follow-up Review

1. Click `Sync Evidence` again for WMT.
2. Click `Generate Review`.
3. Expect a new snapshot and a previous report/snapshot reference.
4. `review_type` should normally be `full_follow_up` if the evidence changed.
5. The report should contain a concise `What Changed Since the Last Review` section.
6. `Thread Actions` are proposals only in Step 5A; they are not persisted as formal Thread objects until Step 6.

### Exact duplicate / token-saving behavior

If the current evidence hash and AI context are identical, the endpoint reuses the successful AnalysisDraft instead of calling Gemini again, unless `force_refresh=true`.

## Important

Step 5A intentionally does not implement Thread tables or Thread lifecycle. That is Step 6.
