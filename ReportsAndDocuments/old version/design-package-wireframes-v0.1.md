# Design Package: Low-Fidelity Wireframes v0.1

**Companion documents:** `mvp-workflow-design-freeze-v0.1.md`, `design-package-api-contract-v0.1.md`, and `design-package-schema-v0.1.md`  
**Purpose:** Confirm the four MVP screens and their required user actions before visual design or application code begins.

## Shared application shell

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Thesis Research                                    [Company: MRVL ▾]     │
├───────────────┬──────────────────────────────────────────────────────────┤
│ Company       │                                                          │
│ Evidence      │                 Selected page content                    │
│ Review        │                                                          │
│ History       │                                                          │
└───────────────┴──────────────────────────────────────────────────────────┘
```

The navigation is intentionally limited to these four tasks. There is no market screener, price dashboard, portfolio view, or Buy/Sell control.

---

## Screen 1 — Company / Thesis

**User goal:** See and maintain the current research context before evaluating new evidence.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Thesis Research                                    [Company: MRVL ▾]     │
├───────────────┬──────────────────────────────────────────────────────────┤
│ Company       │ MRVL — Marvell Technology                                │
│ Evidence      │ Ticker: MRVL                         [Edit company]      │
│ Review        │                                                          │
│ History       │ Current Thesis                                  [Edit]   │
│               │ ┌──────────────────────────────────────────────────────┐ │
│               │ │ AI infrastructure demand, custom silicon, and        │ │
│               │ │ connectivity may support long-term growth; execution │ │
│               │ │ and AI spending durability remain key uncertainties. │ │
│               │ └──────────────────────────────────────────────────────┘ │
│               │                                                          │
│               │ Drivers                                      [+ Add]    │
│               │ • Data-center demand                         High       │
│               │ • Custom silicon adoption                    High       │
│               │                                                          │
│               │ Risks                                        [+ Add]    │
│               │ • AI capital-expenditure slowdown             High      │
│               │                                                          │
│               │ Optional KPIs                                 [+ Add]    │
│               │ • Data-center revenue growth                             │
│               │                                                          │
│               │ Recent evidence                    [Go to Evidence →]   │
└───────────────┴──────────────────────────────────────────────────────────┘
```

### Required interactions

- Create/select a company.
- Create or edit the current thesis text.
- Add, edit, archive, and display a small set of nodes: Driver, Risk, and optional KPI.
- Navigate to evidence entry with this company preselected.

### Display rules

- The current thesis is user-owned; an AI result is never written here automatically.
- Node importance is a simple user-selected level: low, medium, or high.
- This screen shows context, not a recommendation or price target.

---

## Screen 2 — Add Evidence & Sync

**User goal:** Preserve a new piece of evidence through either manual entry or an intentional, on-demand API request.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Thesis Research                                    [Company: MRVL ▾]     │
├───────────────┬──────────────────────────────────────────────────────────┤
│ Company       │ Evidence for MRVL                                        │
│ Evidence      │                                                          │
│ Review        │ [Manual entry]  [On-demand sync]                         │
│ History       │ ──────────────────────────────────────────────────────── │
│               │ Manual entry                                             │
│               │ Title        [______________________________________]    │
│               │ Source URL   [______________________________________]    │
│               │ Event date   [____________]                              │
│               │ Text         [                                      ]    │
│               │              [                                      ]    │
│               │                                  [Save evidence]         │
│               │                                                          │
│               │ On-demand sync                                           │
│               │ Ticker       [MRVL____________]                          │
│               │ Data type    [Historical price ▾]                        │
│               │                                  [Sync latest data]      │
│               │                                                          │
│               │ Latest saved evidence                                   │
│               │ 21 Sep 2026 · Sync · Provider: ___ · Historical price   │
│               │ Status: Saved                  [View] [Analyze]         │
└───────────────┴──────────────────────────────────────────────────────────┘
```

### Required interactions

- Choose one of two clearly labelled entry modes.
- Manual mode validates title, URL, event date, and text before saving.
- Sync mode validates the ticker and lets the user choose only supported data types.
- Sync shows one of: `Saved`, `Partial result`, or `Failed`, with a human-readable reason.
- A completed sync shows provider/source and retrieval time. A new sync adds a new saved snapshot; it never replaces the prior item.
- A saved evidence record can be sent to AI analysis later. Sync itself does not invoke AI.

### Initial supported values

The selector should be intentionally small. Start with **Historical price**, then add either **Company profile/fundamentals** or **News** only after the vertical slice works. Unsupported types are not shown as disabled aspirational features.

---

## Screen 3 — Review Impact

**User goal:** Inspect an AI draft against the original evidence and explicitly decide whether it should influence the user's research.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Thesis Research                                    [Company: MRVL ▾]     │
├───────────────┬──────────────────────────────────────────────────────────┤
│ Company       │ Review AI analysis                         Evidence #24  │
│ Evidence      │                                                          │
│ Review        │ Evidence                                                │
│ History       │ Q2 results / provider result · 21 Sep 2026              │
│               │ Source: _________                         [Open source] │
│               │ ┌──────────────────────────────────────────────────────┐ │
│               │ │ Saved text or normalized data summary                │ │
│               │ └──────────────────────────────────────────────────────┘ │
│               │                                                          │
│               │ AI draft                                                 │
│               │ Summary: [evidence-grounded summary________________]    │
│               │ Affected nodes: Data-center demand · Custom silicon     │
│               │ Impact: [Strengthens ▾]  Materiality: [High ▾]          │
│               │ Confidence: [Medium ▾]                                  │
│               │ Reasoning: [_______________________________________]    │
│               │ Limitations: [_____________________________________]    │
│               │                                                          │
│               │ Suggested follow-up: [ ] Review thesis                  │
│               │                      [ ] Review assumption              │
│               │                                                          │
│               │ [Reject]       [Edit and accept]       [Accept]         │
└───────────────┴──────────────────────────────────────────────────────────┘
```

### Required interactions

- Display the evidence beside, or immediately before, the AI interpretation.
- Allow the user to accept as is, edit before accepting, or reject.
- Require a reason/comment when the user edits a material interpretation; a reject comment is optional but encouraged.
- Do not show an automatic thesis update. Acceptance may create a review result and offer the next step, but the user remains responsible for the thesis text and assumptions.

### Display rules

- “Strengthens” means the evidence supports the existing thesis. It never means “buy.”
- Confidence is an explanation of AI uncertainty, not a probability of investment success.
- If analysis fails, show the evidence and a retry action; do not remove the evidence snapshot.

---

## Screen 4 — History & Valuation

**User goal:** Understand what changed, why it changed, and which evidence/review caused the change.

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Thesis Research                                    [Company: MRVL ▾]     │
├───────────────┬──────────────────────────────────────────────────────────┤
│ Company       │ History and assumptions                                  │
│ Evidence      │                                                          │
│ Review        │ Current simple calculation                               │
│ History       │ EPS [5.30____] × P/E [30____] = Fair value 159.00        │
│               │ Reason for change [_______________________________]     │
│               │                                      [Save assumption]  │
│               │                                                          │
│               │ Thesis history                                           │
│               │ ┌──────────────────────────────────────────────────────┐ │
│               │ │ v2 · 21 Sep 2026                                    │ │
│               │ │ Custom silicon confidence updated                    │ │
│               │ │ Trigger: Evidence #24 · Review: accepted             │ │
│               │ │ [View snapshot]                                      │ │
│               │ ├──────────────────────────────────────────────────────┤ │
│               │ │ v1 · 01 Sep 2026 · Initial thesis                    │ │
│               │ └──────────────────────────────────────────────────────┘ │
│               │                                                          │
│               │ Assumption changes                                      │
│               │ 2028 EPS: 5.00 → 5.30 · reason · linked review          │
└───────────────┴──────────────────────────────────────────────────────────┘
```

### Required interactions

- Show newest-first thesis history with links to its triggering evidence and review.
- Let a user add or revise a simple assumption. The program calculates `EPS × P/E`; it does not choose values.
- Preserve old and new assumption values, reason, time, and linked review where applicable.
- The first vertical slice may show the history area empty and omit calculation editing; it must not block evidence sync.

## Cross-screen navigation and MVP sequence

```text
Company / Thesis
      ↓
Add Evidence & Sync
      ↓
Review Impact
      ↓
History & Valuation
```

The development order is different from the final navigation order:

1. Build Screen 2's sync path and a minimal evidence list first.
2. Add enough of Screen 1 to select a company/ticker.
3. Add Screen 3 only after saved evidence can be retrieved.
4. Add Screen 4 after review and version-history rules are implemented.
