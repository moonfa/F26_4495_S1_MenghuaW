# Step 4 — Slice 1 Evidence Layer Patch

## Files

- `openbb_adapter.py` — drop-in replacement for the current adapter.
- `sync_evidence_replacement.txt` — compatibility-safe replacement for only the existing `/evidence/sync` body.
- `README.md` — integration notes.

## Intentionally unchanged

- `models.py`
- database tables
- `schemas.py`
- `operation = "equity.profile"`
- `/api/v1/evidence/sync` route
- `/api/v1/evidence/{ticker}` route
- AI analysis code

## Why

Step 4 is the Evidence Layer only. Do not mix AI interpretation or Thread logic into it.

## Additional safety change

The normalized payload now bounds:
- company descriptions to 2,500 characters
- news excerpts to 500 characters
- news items to 8
- cash-flow history to 4 annual observations

Raw provider payloads remain unchanged in `raw_payload`.

## Recommended test

1. Start the existing application.
2. `GET /api/v1/health`
3. `POST /api/v1/evidence/sync` with `{"ticker":"WMT"}`
4. Confirm:
   - status = success
   - operation = equity.profile
   - normalized_payload.schema_version = research-snapshot-v2.1
   - company / market / valuation / financial_health / analyst_consensus / recent_news exist
   - data_quality.sections_missing may be empty or contain optional sections
5. Confirm existing `GET /api/v1/evidence/WMT` still returns historical snapshots.
6. Confirm the AI Slice can consume `snapshot.normalized_payload` without reading `raw_payload`.

No database migration is required.