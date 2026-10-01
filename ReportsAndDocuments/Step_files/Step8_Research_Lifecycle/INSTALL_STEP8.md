# Step 8 Installation Guide

## Prerequisite
Install this patch only on the project that already has Step 6.1 and Step 7 working.

## 1. Stop the server
Press `Ctrl + C` in the terminal running Uvicorn.

## 2. Open the project directory
```bash
cd /path/to/F26_4495_S1_MenghuaW/Implementation/MVP_Demo/slice2_new
```

## 3. Install the patch
```bash
python3 /path/to/Step8_Research_Lifecycle/install_step8.py .
```

The installer backs up the files it replaces and makes a consistent SQLite backup.

## 4. Run the additive migration
```bash
python3 -m app.step8.migrate
```

This creates `company_research_state` and `research_updates` and adds report-language metadata. Existing evidence, reports, threads, versions, actions, and notes are preserved.

## 5. Start the application
```bash
python3 -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` and hard-refresh the page.

## 6. First validation
Use WMT first because it already has longitudinal research history. Confirm the old reports and approved threads are visible before generating anything new. Then test Watchlist → Following → Restore, followed by Refresh Evidence → Analyze New Evidence.

## 7. Language validation
Keep English for assignment screenshots. For personal use, choose `Report: 中文` before Analyze New Evidence or Generate Full Review. The language choice affects newly generated natural-language research; it does not rewrite old reports.

## Git note
Do not commit `.env`, API keys, `slice1.db`, or timestamped `.bak` files to a public repository.
