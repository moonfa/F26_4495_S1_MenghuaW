# Design Package: Minimal API Contract v0.1

**Purpose:** Define the smallest stable HTTP boundary required by the four MVP screens. This is a design contract, not an implementation commitment.

## 1. Conventions

- Base path: `/api/v1`
- Payloads: JSON; dates use ISO 8601 (`YYYY-MM-DD` or timestamp with timezone).
- IDs: opaque UUID strings in implementation; examples use readable placeholders.
- The API is initially single-user. Authentication fields are deliberately omitted.
- Error response shape:

```json
{
  "error": {
    "code": "INVALID_TICKER",
    "message": "Enter a valid supported ticker.",
    "details": []
  }
}
```

## 2. Shared representations

### Company

```json
{
  "id": "company_mrvl",
  "ticker": "MRVL",
  "name": "Marvell Technology",
  "created_at": "2026-09-21T10:00:00Z"
}
```

### Evidence snapshot summary

```json
{
  "id": "evidence_24",
  "company_id": "company_mrvl",
  "entry_mode": "sync",
  "evidence_type": "historical_price",
  "title": "MRVL historical price sync",
  "source_name": "Configured provider",
  "source_url": null,
  "provider": "configured_provider",
  "event_date": null,
  "retrieved_at": "2026-09-21T10:05:02Z",
  "status": "saved",
  "summary": "Retrieved 30 daily observations.",
  "created_at": "2026-09-21T10:05:02Z"
}
```

`entry_mode` is `manual` or `sync`. `status` is `saved`, `partial`, or `failed`. A failed sync remains a traceable evidence attempt but has no analysis action.

## 3. Company and thesis setup

| Method and path | Purpose | MVP phase |
|---|---|---|
| `POST /companies` | Create a company context. | Setup |
| `GET /companies` | Populate company picker/list. | Setup |
| `GET /companies/{company_id}` | Retrieve company and current thesis context. | Setup |
| `PUT /companies/{company_id}/thesis` | Create/update current thesis text. | Setup |
| `POST /companies/{company_id}/nodes` | Add a Driver, Risk, or KPI. | Setup |
| `GET /companies/{company_id}/nodes` | Retrieve nodes used in review. | Setup |

### `POST /companies`

Request:

```json
{ "ticker": "MRVL", "name": "Marvell Technology" }
```

Response: `201 Created` with a Company. Return `409 Conflict` if the ticker already exists in the single-user prototype.

### `PUT /companies/{company_id}/thesis`

Request:

```json
{
  "title": "Base thesis",
  "current_summary": "AI infrastructure demand may support long-term growth.",
  "change_reason": "Initial thesis"
}
```

Response: `200 OK` with thesis ID and current summary. Before version history exists, this endpoint only updates the working thesis; later, an approved material change must also create a thesis version through the review workflow.

### `POST /companies/{company_id}/nodes`

Request:

```json
{
  "node_type": "driver",
  "title": "Data-center demand",
  "description": "Demand for AI data-center infrastructure.",
  "importance": "high"
}
```

Response: `201 Created`. Valid `node_type` values: `driver`, `risk`, `kpi`, `sub_thesis`.

## 4. Evidence endpoints

### `POST /companies/{company_id}/evidence` — create manual event

Request:

```json
{
  "title": "Q2 earnings release",
  "source_url": "https://example.com/investor-release",
  "event_date": "2026-09-20",
  "content": "Company-released text or the user's research notes.",
  "evidence_type": "earnings"
}
```

Response: `201 Created` with an Evidence snapshot summary and `entry_mode: "manual"`.

Validation failures return `422 Unprocessable Entity`, including missing title/content/date or malformed URL. No AI analysis is requested by this endpoint.

### `POST /sync` — on-demand ticker sync

This is the first vertical-slice endpoint. It deliberately receives a ticker so the user can invoke Sync from the evidence page; the backend finds or creates no company implicitly. The client must first select/create the company and then provide its ticker.

Request:

```json
{
  "company_id": "company_mrvl",
  "ticker": "MRVL",
  "data_type": "historical_price",
  "range": "1m"
}
```

Valid initial `data_type`: `historical_price`. Future types such as `company_profile`, `fundamentals`, or `news` require an explicit contract update.

Successful response: `201 Created` with the evidence snapshot plus a compact, normalized display payload:

```json
{
  "evidence": {
    "id": "evidence_24",
    "entry_mode": "sync",
    "evidence_type": "historical_price",
    "provider": "configured_provider",
    "retrieved_at": "2026-09-21T10:05:02Z",
    "status": "saved",
    "summary": "Retrieved 30 daily observations."
  },
  "display_data": {
    "currency": "USD",
    "interval": "1d",
    "observations": [
      { "date": "2026-09-18", "close": 75.12 }
    ]
  }
}
```

Failure semantics:

| Status | Meaning |
|---|---|
| `422` | Invalid ticker, unsupported data type, or invalid range. |
| `404` | Selected company does not exist. |
| `424` | Upstream provider could not complete the request; save a failed sync attempt where possible. |
| `429` | Provider or application request limit reached. |
| `503` | OpenBB adapter/service is unavailable. |

The endpoint is synchronous for MVP. The UI should show an in-progress state and use a timeout; an eventual background-job design is deferred.

### `GET /companies/{company_id}/evidence`

Returns saved evidence newest-first. Optional query parameters: `entry_mode`, `status`, `limit`. The screen uses this to show both manual records and prior sync snapshots.

### `GET /evidence/{evidence_id}`

Returns full provenance and the stored manual text or normalized/raw data reference. It does not request fresh provider data.

## 5. AI analysis and review endpoints

These endpoints are designed now but implemented only after the Sync vertical slice works.

### `POST /evidence/{evidence_id}/analyze`

Request:

```json
{ "thesis_id": "thesis_mrvl_current" }
```

The server loads the selected evidence, current thesis, and eligible thesis nodes. It returns `201 Created` with an immutable AI-analysis draft:

```json
{
  "id": "analysis_17",
  "evidence_id": "evidence_24",
  "status": "draft",
  "summary": "The evidence indicates ...",
  "impacts": [
    {
      "node_id": "node_data_center",
      "impact": "strengthens",
      "materiality": "medium",
      "reasoning": "..."
    }
  ],
  "confidence": "medium",
  "thesis_review_suggested": true,
  "assumption_review_suggested": false,
  "limitations": ["The evidence does not establish duration of demand."],
  "model": "implementation-defined",
  "prompt_version": "v1"
}
```

Return `409 Conflict` if the evidence is not `saved`/`partial`, or an active draft already exists. Return `502 Bad Gateway` when the model provider fails; evidence remains unchanged.

### `POST /ai-analyses/{analysis_id}/review` — review impact

Request:

```json
{
  "decision": "edit_and_accept",
  "edited_result": {
    "summary": "User-approved wording.",
    "impacts": [
      {
        "node_id": "node_data_center",
        "impact": "strengthens",
        "materiality": "medium",
        "reasoning": "User-approved reason."
      }
    ],
    "thesis_review_suggested": true,
    "assumption_review_suggested": false
  },
  "reviewer_note": "Changed confidence interpretation."
}
```

Valid decisions: `accept`, `edit_and_accept`, `reject`.

Response: `201 Created` with the review ID, final accepted/rejected result, and links to the evidence and analysis. This endpoint **does not** overwrite the thesis or any assumption. A later explicit action creates a thesis version or assumption change.

## 6. History and assumption endpoints

| Method and path | Purpose |
|---|---|
| `GET /companies/{company_id}/history` | Retrieve thesis and assumption history with linked evidence/review IDs. |
| `POST /companies/{company_id}/assumptions` | Create or revise a simple user-controlled assumption. |
| `POST /theses/{thesis_id}/versions` | Explicitly preserve an approved material thesis change. |

### `POST /companies/{company_id}/assumptions`

Request:

```json
{
  "metric": "eps",
  "period": "2028",
  "value": 5.3,
  "unit": "USD",
  "reason": "User review after evidence #24",
  "review_id": "review_8"
}
```

The server returns `201 Created` including the prior value, new value, and any deterministic calculation currently supported. Assumptions are user-controlled; `review_id` is optional.

## 7. Implementation order

Only these routes are required for the first executable vertical slice:

```text
POST /companies
POST /sync
GET  /companies/{company_id}/evidence
GET  /evidence/{evidence_id}
```

All other routes exist here to keep the design consistent with the reviewed MVP workflow, but are implemented later in this order: thesis/nodes → analyze → review → history/assumptions.
