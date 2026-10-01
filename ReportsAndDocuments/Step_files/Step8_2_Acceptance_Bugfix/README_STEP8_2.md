# Step 8.2 — Acceptance / bug-fix pass

This package is based on the current GitHub `feature/step6-research-history` code.

The core patch fixes three confirmed issues without a DB migration: Full Review cache now respects report language; Step 8 materiality no longer treats ordinary market price/volume moves as thesis-level materiality and uses narrower event phrases; Research Timeline treats Full Reviews as activity markers rather than repeating the report synopsis already shown in Historical Master Research Reports. It also hides the old second Thread-history output box, which was one source of visual duplication.

Two diagnostic scripts are included. `acceptance_step8_2.py` performs read-only API acceptance for WMT, MCD and MRVL. `diagnose_thread_actions.py` prints persisted Thread Action statuses so we can distinguish a UI bug from genuinely new proposals before changing historical decisions.

Install after stopping Uvicorn, from `Implementation/MVP_Demo/slice2_new`:

```bash
python3 /path/to/Step8_2_Acceptance_Bugfix/install_step8_2.py .
python3 -m py_compile app/routes.py app/step8/routes.py
python3 -m uvicorn app.main:app --reload
```

No database migration is required. Hard refresh with `Cmd + Shift + R`.

Then run:

```bash
python3 /path/to/Step8_2_Acceptance_Bugfix/acceptance_step8_2.py
python3 /path/to/Step8_2_Acceptance_Bugfix/diagnose_thread_actions.py
```

Finally perform one real workflow for each ticker: `Refresh Evidence → Analyze New Evidence`. Do not generate a Full Review unless the targeted update genuinely warrants one.

Important: this package intentionally does **not** automatically rewrite old `proposed` Thread Actions. The diagnostic output should be reviewed first. An old approved/rejected action and a later AI action with the same title are not necessarily the same decision if the new evidence or change summary differs.
