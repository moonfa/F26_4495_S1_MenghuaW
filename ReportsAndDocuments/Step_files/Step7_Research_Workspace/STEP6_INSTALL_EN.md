# Step 6 — Research History & Thread Continuity: Installation Guide

This implementation extends the existing `Implementation/MVP_Demo/slice2_new` application without replacing Slice 1, Slice 2, integer primary keys, or the existing SQLite database.

## Goal

Step 6 turns successful `AnalysisDraft` output into durable research history. It adds formal Research Reports, persistent Research Threads, Thread Versions, human-reviewed Thread Actions, and a separate Personal Research Journal.

## Installation sequence

1. Stop Uvicorn and commit or back up current work.
2. Back up `slice1.db` (or the database specified by `DATABASE_URL`).
3. Install the Step 6 files into the existing `app` package. Do not replace the project with the old UUID-based Muse model.
4. Run the additive migration. Existing `Company`, `EvidenceSnapshot`, and `AnalysisDraft` rows remain in place.
5. Restart with `python3 -m uvicorn app.main:app --reload`.
6. Open the application and use **Load Saved Research**. Reading history must not call OpenBB or Gemini.

## Core domain objects

- `ResearchReport`: immutable formal archive of a successful Master Research Report and its Evidence Snapshot.
- `ResearchThread`: a long-lived company-specific research question or thesis area.
- `ThreadVersion`: the state of a Thread at a specific approved report.
- `ThreadAction`: an AI proposal (`create`, `continue`, `update`, `deprioritize`, `close`, or `ephemeral`) that requires human review before changing persistent Thread state.
- `PersonalResearchNote`: user-authored, dated investment-research notes kept separate from AI output.

## Required behavior

A successful new report is archived and linked with `previous_report_id`. Failed AI attempts never overwrite a successful report. AI Thread Actions remain proposals until the user approves or rejects them. Opening saved history is database-only.

## Continuity acceptance test

Use one company for at least two real research reviews. Approve a Thread from the first report, then approve an update to the same Thread from a later report. The database should contain one `ResearchThread` and at least two `ThreadVersion` rows linked to two different `ResearchReport` rows.

## Scope boundary

The research workflow remains: Thesis → Drivers / Risks → New Evidence → Human Review → Historical Report. Valuation is an implication/check layer, not the center of the application.
