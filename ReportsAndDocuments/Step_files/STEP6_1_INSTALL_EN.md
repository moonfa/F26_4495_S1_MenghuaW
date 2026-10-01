# Step 6.1 — Fixes and Acceptance Testing

This package is installed on top of a working Step 6 project at `Implementation/MVP_Demo/slice2_new`. Do not reinstall the older Step 6 package and do not delete the existing database.

## Installation

1. Stop Uvicorn (`Ctrl+C`) and commit or back up local changes in VS Code Source Control.
2. Extract the ZIP to Downloads and open a terminal in `Implementation/MVP_Demo/slice2_new`.
3. Run:

```bash
python3 ~/Downloads/Step6_1_Research_Continuity_Fixes/install_step61.py .
python3 -m app.step6.migrate
python3 -m uvicorn app.main:app --reload
```

If the browser still shows the previous UI, hard refresh (`Cmd+Shift+R` on macOS). The installer backs up replaced files and the default `slice1.db`. The migration script also backs up the active SQLite database. If `DATABASE_URL` points elsewhere, back up that database separately first.

## Changes in Step 6.1

- `app/static/index.html`: replaces prompt-based Edit & Approve with an inline editor; improves report labels and summaries; explains Evidence Delta in plain language; displays lightweight Valuation Implication.
- `app/step6/routes.py`: report APIs return summary and valuation implication; edited approval can update a Thread title; duplicate ThreadVersion creation from the same report is blocked; a proposed create action may be linked to an existing Thread during human review.
- `app/step6/models.py` + `migrate.py`: adds only nullable `valuation_implications` JSON to formal `research_reports`; existing integer primary keys and history are preserved.
- `app/ai/schemas.py` + `prompts.py`: the same Gemini response may describe effects on the active valuation model's base metric and multiple, including direction, magnitude, confidence, reason and overall action. It does not calculate or update Fair Value.
- `app/step6/service.py`: archives valuation implications from successful AI analysis into the formal historical report.

The GitHub version inspected did not contain `valuation_models` or `assumptions` tables. This patch therefore does not invent an automatic valuation calculator. Without an active valuation model, valuation implication may be null and older reports display Not assessed.

## Financial-unit check

For the supplied WMT evidence, `dividend_yield=0.92` and `debt_to_equity=71.65` are treated as provider percentage values, producing 0.92% and 71.65%. Other providers must still be checked against the adapter normalization contract; the UI must not infer units only from numeric size.

## Acceptance checks

1. WMT → Load Saved Research: history shows readable date, review type and summary while retaining technical Report/Evidence IDs.
2. Open a report with a proposed Thread Action → Edit & Approve: an inline editor exposes Title, Summary, Importance and Reviewer Note.
3. Confirm the original AI proposal remains preserved; a second approval of the same action returns HTTP 409.
4. Approve `create` from report A, then approve `update` for the same thread from report B. The timeline must contain two versions with different `report_id` values and one shared `thread_id`.
5. New reports may contain `valuation_implications`; older reports may remain null and user valuation assumptions are not changed automatically.
6. Optional local test: `python3 -m pytest tests/test_step6_integration.py -q`. Tests use mock fixtures, not the real SQLite database.

## Not included

No automatic Fair Value engine, no new valuation-model tables, no real Gemini/OpenBB online acceptance test, and no React migration. Other provider field units still require provider-specific verification.
