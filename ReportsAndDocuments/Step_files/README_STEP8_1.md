# Step 8.1 UX / Language / Materiality refinement

Baseline: current GitHub `feature/step6-research-history` Step 8.

Install from `Implementation/MVP_Demo/slice2_new` after stopping Uvicorn:

```bash
python3 /path/to/Step8_1_UX_Refinement/install_step8_1.py .
python3 -m py_compile app/step8/routes.py app/routes.py
python3 -m uvicorn app.main:app --reload
```

Then `Cmd + Shift + R`.

Changes: ticker-only Watchlist; hover × moves to Following without deleting data; thread accordion open/close; clearer historical report hierarchy; expandable Research Timeline with Evidence Snapshot deltas; per-company English/中文 persistence; language-aware Full Review cache; conservative materiality rules and low-impact guardrail.

No database migration is required. Existing reports, evidence, threads, notes and research updates are preserved.
