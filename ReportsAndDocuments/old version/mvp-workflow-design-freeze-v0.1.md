# MVP Workflow & Design Freeze v0.1

**Project:** AI-Assisted Personal Investment Research & Decision-Support System  
**Status:** Baseline for MVP design and development  
**Scope:** One-semester, individual prototype  
**Last updated:** 2026-09-21

## 1. Purpose and MVP boundary

This project is a personal investment-research tool. It helps a user preserve the reasoning behind a company thesis, add new evidence, assess whether that evidence matters to the thesis, and retain a history of approved changes.

The system is **not** a stock picker, an automated trading system, or a replacement for a financial-data terminal. It does not determine whether a company is a good investment or issue Buy/Sell recommendations.

The MVP delivers this closed loop:

```text
Thesis and key factors
        ↓
New evidence enters the system
        ↓
AI analysis draft
        ↓
Human review
        ↓
Optional assumption review
        ↓
Traceable history of the approved change
```

### 1.1 In scope

- Create one researched company and its current investment thesis.
- Add and maintain a small set of Drivers, Risks, and optionally KPIs.
- Add evidence manually.
- Retrieve a small, selected set of external data on demand for a user-entered ticker.
- Store the resulting evidence with its source and time information.
- Generate an AI impact-analysis draft from the evidence and the current thesis context.
- Require the user to Accept, Edit and Accept, or Reject the draft.
- Preserve approved thesis and valuation-assumption changes as history.
- Calculate a simple, deterministic value from user-approved assumptions, if used.

### 1.2 Explicitly out of scope for MVP

- Automatic trading or investment recommendations.
- Full-market screening, portfolio management, alerts, or real-time streaming data.
- Bulk or continuous news/SEC crawling.
- A comprehensive financial-data warehouse or a Yahoo Finance clone.
- Multiple-provider comparison, automatic provider fallback, or a provider-ranking system.
- Full DCF, SOTP, or a universal Bull/Base/Bear valuation engine.
- User accounts, multi-user collaboration, social publishing, or permissions.
- Automatically changing a thesis, forecast, or valuation assumption without human approval.

## 2. Frozen design decisions

The following decisions are stable for the MVP. They should guide later UI, API, database, and test work. Their technical implementation may still change.

1. **The unit of value is reasoning, not raw market data.** External data supports a personal thesis; it is not the product's main database.
2. **Evidence has two entry modes.** A user may enter it manually or request an on-demand sync.
3. **Every evidence record is traceable.** It retains its company/ticker, source or provider, date/time, content or normalized payload, and entry mode.
4. **A sync creates a snapshot.** A later sync must not silently overwrite an earlier result.
5. **AI proposes; the user decides.** AI output is always a reviewable draft.
6. **A thesis change does not automatically mean a valuation change.** The user decides whether to revise an assumption.
7. **History is preserved.** An approved material change creates an auditable version or change record rather than erasing the prior reasoning.
8. **The system provides decision support only.** Interface labels and generated text must not present an investment recommendation.

## 3. Core objects and plain-language meanings

| Object | Meaning in the MVP |
|---|---|
| Company | The company being researched, identified by a ticker and name. |
| Thesis | The user's current explanation of why the company is being followed and what may cause the thesis to hold or fail. |
| Thesis node | A Driver, Risk, KPI, or optional Sub-thesis connected to the overall thesis. |
| Evidence / Event | A specific new item of information that may or may not affect the thesis. |
| Evidence snapshot | The saved result of a manual entry or an on-demand data sync at a particular time. |
| AI analysis | A structured, non-final interpretation of an evidence item. |
| Review decision | The user's Accept, Edit and Accept, or Reject decision about the AI analysis. |
| Assumption | A user-controlled input such as EPS or P/E that may be used in a simple calculation. |
| History record | A preserved record of an approved thesis or assumption change and its reason. |

## 4. Evidence entry: the new on-demand sync feature

### 4.1 Manual entry

The user creates a public event/evidence record with:

- Company/ticker
- Title
- Source URL
- Event date
- Text or notes
- Optional category, such as earnings, company announcement, news, or other

The system validates that required fields are present and that the URL is syntactically valid. Manual entry remains a first-class path even when sync is available, because useful research evidence will not always be available through an API.

### 4.2 On-demand sync

The user enters a ticker, selects a limited evidence type, and presses **Sync**. The MVP should support only a small number of types selected during implementation; a suitable initial target is historical price data plus either company profile/fundamental metrics or news.

The backend calls an OpenBB-based adapter and one configured data provider. OpenBB is treated as a server-side integration layer, not as a promise that every dataset is available without credentials or provider limits.

The system then:

1. validates the ticker and selected sync type;
2. records a sync request and its status;
3. obtains and normalizes the provider result when available;
4. creates an evidence snapshot;
5. stores the provider/source, retrieval timestamp, query parameters, and a raw-response reference or payload;
6. displays a clear success, partial-success, or failure result to the user.

The user's browser must never hold provider API keys. Credentials remain server-side.

### 4.3 Minimum evidence provenance

Every saved evidence item must expose the following information in the UI or record details:

| Field | Why it is needed |
|---|---|
| Company/ticker | Identifies the research context. |
| Entry mode | Distinguishes `manual` from `sync`. |
| Source/provider | Makes the origin visible. |
| Source URL or provider query | Lets the user trace the evidence. |
| Event date and/or retrieved-at time | Separates when something happened from when it was obtained. |
| Saved content/payload | Preserves what the system actually analyzed or displayed. |
| Status | Makes failures, incomplete responses, and completed records distinguishable. |

## 5. End-to-end MVP workflow

This is the principal user workflow and the baseline for acceptance testing.

```text
1. Select or create a company
          ↓
2. Create current thesis and key Drivers/Risks
          ↓
3. Add evidence manually OR request an on-demand sync
          ↓
4. Save a traceable evidence snapshot
          ↓
5. Request AI impact-analysis draft
          ↓
6. Review: Accept / Edit and Accept / Reject
          ↓
7. If approved, optionally review an assumption
          ↓
8. Preserve a thesis and/or assumption history record
```

### 5.1 Detailed workflow responsibilities

| Step | User action | Program responsibility | AI responsibility | Output |
|---:|---|---|---|---|
| 1 | Select/create a company | Validate and save identity | None | Company context |
| 2 | Write thesis; add Drivers/Risks | Save current research context | May assist later, not decide | Current thesis structure |
| 3 | Enter event or press Sync | Validate inputs; call adapter if requested | None | New evidence candidate |
| 4 | Confirm saved evidence | Preserve source, timestamps, payload, status | None | Evidence snapshot |
| 5 | Request analysis | Send selected context; validate and save response | Classify, summarize, map impacts, state limitations | AI draft |
| 6 | Accept, edit, or reject | Persist review and audit link | None | Human decision |
| 7 | Optionally revise an assumption | Validate value; calculate deterministic result | May flag review need only | Before/after result |
| 8 | Confirm material change | Create history/version records; retain links | None | Traceable research history |

## 6. AI analysis contract

AI is used for structured interpretation, not for autonomous financial decisions. The exact model and prompt can change, but every MVP analysis should supply these conceptual fields:

- **What happened:** short evidence-grounded summary.
- **Affected nodes:** zero or more selected Drivers, Risks, KPIs, or Sub-theses.
- **Impact:** `strengthens`, `weakens`, `mixed`, `uncertain`, or `no_material_change`.
- **Materiality:** `low`, `medium`, or `high`.
- **Reasoning and evidence:** why the item was mapped to each node.
- **Confidence:** `low`, `medium`, or `high`.
- **Suggested next review:** whether the user may want to review a thesis or assumption.
- **Limitations:** missing information or uncertainty in the analysis.

The backend validates structured output before saving it. If an AI call fails or returns invalid content, the evidence record remains available and the user can retry or analyze manually.

## 7. Human review and history rules

### 7.1 Review choices

| User decision | Result |
|---|---|
| Accept | The user adopts the draft as presented. |
| Edit and Accept | The user modifies the draft before adopting it. |
| Reject | The evidence and AI draft remain in history, but no thesis/assumption change is applied. |

### 7.2 Versioning rules

- A new evidence item alone does not create a new thesis version.
- A rejected draft never changes the current thesis or assumptions.
- A user-approved, material thesis change creates a new thesis-history/version record.
- An assumption revision preserves its previous value, new value, reason, review link, and timestamp.
- A simple valuation calculation uses the saved, user-approved inputs only. Example: `Fair value = EPS × P/E`.
- The application records before/after differences but does not infer that an increase means the company is a good investment.

## 8. Functional acceptance criteria

The MVP is ready for a demonstration when the following can be completed with one primary company (initially MRVL) without direct database manipulation:

1. Create the company, a thesis, at least two Drivers, and one Risk.
2. Add one manual evidence record with title, source URL, date, and text; invalid required input is rejected with a useful message.
3. Enter a valid ticker, request one supported sync type, and see either a saved snapshot with source/provider and retrieval time or a clear error status.
4. Perform a second sync and verify that the earlier snapshot is still visible.
5. Request an AI analysis for an evidence record and see a structured draft with impact, affected node(s), reasoning, confidence, and limitations.
6. Reject one draft and verify that it does not alter the current thesis.
7. Edit and accept another draft, then verify that a linked thesis-history record identifies the triggering evidence and review.
8. If the simple valuation feature is implemented, change an EPS or P/E assumption and verify that the calculation and before/after values are deterministic and traceable.

## 9. Design questions deliberately deferred

These decisions are important but are not frozen now:

- Exact OpenBB version, provider, credentials, and production deployment method.
- The final two sync types supported in the first release.
- Exact PostgreSQL table names, field types, and normalization choices.
- Final API routes, frontend framework components, and page layout.
- Exact LLM, prompt wording, JSON schema library, and retry strategy.
- Whether Bull/Base/Bear is represented in the initial UI.
- Whether lightweight validation companies beyond MRVL are included before or after the main workflow is complete.

## 10. Next design artifacts and sequence

This document should now be used in the following order:

1. **Low-fidelity wireframes:** four screens only — Company/Thesis, Add Evidence & Sync, Review Impact, and History/Assumptions.
2. **Minimal API contract:** define requests and responses for company/thesis setup, manual evidence, sync, analysis, review, and history retrieval.
3. **Minimal database schema:** derive tables and relationships only from the frozen workflow.
4. **Vertical slice:** implement `ticker → sync → evidence snapshot → display` before adding more data types or AI features.
5. **Complete the closed loop:** add AI draft, human review, and traceable history.

No new feature should be added until it can be placed within Sections 1–8 of this document or explicitly approved as a later-phase item.
