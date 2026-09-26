# AI-Assisted Personal Investment App — MVP Specification

**Document:** MVP / Design Freeze  
**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Frozen for MVP design; implementation follows in subsequent steps

---

## 1. Purpose

This document freezes the product scope and core workflow for the MVP of the **AI-Assisted Personal Investment Research App**.

The MVP is designed around one central problem:

> An investor needs to continuously research a company over time, while allowing the research focus to change as new evidence, events, valuation, competition, and business conditions change.

The system therefore does **not** attempt to build a fixed company knowledge tree or generate a large set of structured AI objects at every run.

Instead, it uses a lightweight research loop:

```text
User Input
    ↓
Slice 1 — Evidence Snapshot
    ↓
AI Slice — One Deep Research Pass
    ↓
Master Research Report
    ↓
Key Takeaways + Thread Actions
    ↓
Research Threads
    ↓
Timeline / Continuity
    ↓
Research Workbench UI
```

The MVP optimizes for:

1. High-quality and coherent investment analysis.
2. Freshness of the research snapshot.
3. Efficient token usage.
4. Flexible research themes that evolve over time.
5. Clear continuity between important research topics across different dates.
6. A small, controllable implementation scope suitable for a roughly 120-hour course project.

---

# 2. Core Product Thesis

The product is **not** another financial-data lookup tool.

OpenBB/yfinance and similar sources already provide:

- price data;
- financial metrics;
- valuation metrics;
- analyst information;
- recent news.

The product's differentiated value is:

> **What matters about this company right now, what changed since the previous research point, and which research topics remain worth following?**

Therefore:

```text
Evidence = What is observable now

Report = What the research assistant thinks matters now

Thread = What is worth following across time

Timeline = How that research topic changed over time
```

---

# 3. Frozen MVP Principles

## 3.1 Report is a snapshot

A `Research Report` represents the analyst's view at one point in time.

A report should be coherent and narrative-driven, similar to a strong investment research note.

It is **not** the permanent knowledge structure of the company.

---

## 3.2 Thread is continuity

A `Research Thread` represents a topic that may remain relevant across multiple research dates.

Examples:

- Advertising monetization
- Store network advantage
- Search monetization
- Custom ASIC design wins
- Autonomous driving economics

A Thread exists only when the topic is worth following across time.

---

## 3.3 Not every topic becomes a Thread

The system explicitly allows three research lifecycles:

### Persistent / Long-lived

Topics that may matter for years.

### Flexible / Medium-lived

Topics that may matter for months or several research cycles and can become more or less important.

### Ephemeral / Short-lived

Topics that are important only temporarily.

Examples:

- a tariff announcement;
- a temporary supply disruption;
- a one-quarter regulatory issue;
- a specific earnings surprise.

An ephemeral topic does **not** need a persistent Thread.

---

## 3.4 Different companies have different Persistent Thread frameworks

The system must **not** impose one universal research-topic list on every company.

Instead:

```text
Company Archetype
       ↓
Candidate Thread Framework
       ↓
Company-specific Threads
       ↓
Dynamic importance and lifecycle
```

For example:

| Company Archetype | Example Persistent Thread Candidates |
|---|---|
| Retail / Consumer | Same-store sales, consumer mix, pricing, margins, e-commerce, advertising, membership, store network |
| Semiconductor | Product cycle, hyperscaler design wins, AI/custom ASIC, customer concentration, gross margin, capex |
| Platform / Internet | Users, engagement, monetization, network effects, advertising, AI impact, take rate |
| Mobility / Marketplace | Trips, take rate, supply, unit economics, autonomy, regulation |
| Telecom | Subscribers, ARPU, churn, capex, spectrum, FCF, satellite competition |
| Banking | NIM, loan growth, credit losses, deposits, capital ratios, capital return |
| Utility | Rate base, capex, allowed ROE, power demand, regulation, financing cost |

These are **candidate frameworks**, not mandatory Threads.

---

## 3.5 Deep narrative first, structure second

The first AI pass should prioritize the quality of reasoning rather than producing a large number of structured fields.

The preferred AI workflow is:

```text
Evidence
   ↓
One coherent deep analysis
   ↓
Master Research Report
   ↓
Lightweight extraction of key takeaways and thread actions
```

The MVP should not ask one AI call to simultaneously generate dozens of `Insight`, `Driver`, `Risk`, `KPI`, and `Research Node` objects.

---

# 4. End-to-End MVP Workflow

## 4.1 User Input

The MVP input is intentionally small:

```text
Ticker
```

Optional future inputs may include a research question or event, but they are outside the first MVP freeze.

Example:

```text
WMT
```

---

# 5. Slice 1 — Evidence Layer

## Objective

Create a reliable, reproducible snapshot of current company evidence.

Slice 1 answers:

> What do we know right now?

It must not attempt to generate investment conclusions.

## Evidence categories

### Company

- Symbol
- Company name
- Sector
- Industry
- Business description
- Corporate metadata when available

### Market

- Current price
- Market capitalization
- 52-week high
- 52-week low
- Beta
- Volume when available

### Valuation

- Trailing P/E
- Forward P/E
- PEG
- P/S
- P/B
- P/FCF
- EV/EBITDA
- FCF yield when available

### Financial quality

- Revenue growth
- Earnings / EPS growth
- Gross margin
- Operating margin
- Profit margin
- ROE
- ROIC when available
- Debt / leverage
- Liquidity
- Free cash flow indicators when available

### Analyst context

- Consensus target
- High / low target range
- Number of analysts
- Consensus rating where available

### Recent news

The MVP should provide a small recent-news set rather than full article bodies.

Store, where available:

- Date
- Title
- Publisher / source
- URL
- Short excerpt / summary

## Evidence rules

1. Preserve the raw provider payload.
2. Store a normalized payload for AI consumption.
3. Record timestamp and content hash.
4. Do not silently overwrite historical evidence snapshots.
5. Do not include chart generation in the MVP.

---

# 6. AI Slice — Research Analysis

## Objective

Transform the Evidence Snapshot into one high-quality English investment research report.

The AI Slice answers:

> Given what we know now, what matters about this company and why?

## AI output

The MVP uses **one primary AI reasoning pass**.

The main output is:

```text
Master Research Report
```

The report should be written in English and should read like a strong fundamental investment research note.

### Recommended report structure

1. Business Model & Earnings Logic
2. Investment Classification
3. Moat Analysis
4. Competitive Position
5. Growth Drivers
6. Catalysts / What Could Change Next
7. Key Risks
8. Valuation Context
9. What Matters Most Now
10. What to Monitor

These are report sections, not independent AI database objects.

## Key Takeaways

After producing the report, the AI should provide approximately 3–6 concise takeaways.

They must summarize the report rather than introduce new information.

## Evidence discipline

The AI may use stable background knowledge to explain business and industry mechanisms, but it must not invent current numerical facts, recent events, management statements, analyst estimates, or other time-sensitive claims that are not in the evidence.

The model should distinguish:

```text
Evidence-backed fact
vs.
Stable background knowledge
vs.
Interpretation / inference
```

The AI should not provide buy/sell recommendations, target prices, or overall stock rankings in the MVP.

---

# 7. Thread Action Layer

After generating the report, the AI performs a lightweight continuity step.

The purpose is **not** to rewrite all existing research Threads.

The AI answers:

> What changed relative to the existing research state?

## Possible Thread Actions

| Action | Meaning |
|---|---|
| `continue` | Same research topic remains relevant with no material change |
| `update` | Same topic remains relevant, but state / importance / evidence changed |
| `create` | A meaningful new cross-time research topic has emerged |
| `deprioritize` | Existing topic is temporarily less important |
| `close` | Topic is no longer worth tracking |
| `ephemeral` | Important for this report but not worth a persistent Thread |

Optional future actions such as `split` and `merge` are not required for the first MVP.

## Thread importance

The MVP uses simple qualitative importance:

```text
High
Medium
Low
```

And a directional change:

```text
Increased
Unchanged
Decreased
New
```

---

# 8. Research Thread Layer

A Thread is a persistent research object for a company.

A Thread contains at minimum:

- Thread ID
- Company ID
- Title
- Thread type / lifecycle class
- Status
- Current importance
- Created time
- Last active time

## Lifecycle

```text
Candidate
    ↓
Active
    ↓
Watching
    ↓
Dormant
    ↓
Archived
```

### Candidate

New topic that may become worth tracking.

### Active

Currently important to the investment case.

### Watching

Relevant but not a dominant research topic.

### Dormant

No meaningful change for a period of time.

### Archived

Historical topic that is no longer active.

The lifecycle must not delete the historical record.

---

# 9. Thread Version / Timeline

The MVP must preserve the state of an important Thread across research dates.

A Thread is therefore not merely a title.

It has a sequence of time-specific states:

```text
Thread
  ├── Version @ T1
  ├── Version @ T2
  ├── Version @ T3
  └── Version @ T4
```

Each Thread Version records only the relevant change and current state.

The system should not force a new version when nothing material has changed.

## Example

```text
Advertising Monetization

2026-08-01
Importance: Medium
State: Emerging

2026-09-01
Importance: High
State: Becoming a meaningful margin-expansion driver

2026-09-23
Importance: High
State: Still important; evidence continues to support the theme
```

For an ephemeral topic:

```text
Tariff Exposure

2026-09-10 → 2026-09-25
Ephemeral
```

It may remain attached to one or more reports without becoming a long-term Thread.

---

# 10. How Time Continuity Works

The MVP must not rely on matching identical topic names across dates.

Continuity is established through:

```text
Thread ID
+
Thread Action
+
Thread Version
```

For example:

```text
Sep 1
"AI impact on Search"
        ↓
Thread: Search / AI Monetization
        ↓
Sep 20
"Gemini monetization"
        ↓
Same Thread
```

The title can change while the underlying research object remains the same.

Conversely, the same words can represent different research states and should not automatically be merged.

---

# 11. Timeline UI Concept

The MVP UI should make change visible without requiring the user to read every historical report.

Example:

```text
WMT — Current Research State

HIGH IMPORTANCE
↑ Advertising / Marketplace
↑ Consumer mix

MEDIUM
→ Store network
→ E-commerce

WATCHING
↓ Sam's Club international

NEW / TEMPORARY
△ Tariff exposure

---------------------------------

WHAT CHANGED SINCE LAST REVIEW?

↑ Advertising became more important
→ Store network thesis unchanged
↓ Sam's Club temporarily less important
NEW tariff-related topic
```

The historical timeline can then show:

```text
Aug ───── Sep ───── Oct
  ●────────●────────● Advertising
           ●──●             Tariff
     ●──────●               E-commerce
```

---

# 12. UI / MVP Pages

The MVP only requires a small number of screens.

## Screen 1 — Company Research Home

Purpose:

- Enter ticker
- Sync current evidence
- Generate / refresh research analysis

## Screen 2 — Current Research Dashboard

Displays:

- company identity;
- current market / valuation snapshot;
- current research importance changes;
- active / watching / temporary Threads;
- latest Master Research Report.

## Screen 3 — Research Timeline

Displays:

- historical reports;
- Thread history;
- importance changes;
- created / updated / deprioritized / closed topics.

A dedicated K-line chart is **not part of the MVP**.

---

# 13. MVP Data Flow

```text
                    USER
                     │
                   Ticker
                     │
                     ▼
          ┌─────────────────────┐
          │     SLICE 1         │
          │ Evidence Acquisition│
          └──────────┬──────────┘
                     │
             Evidence Snapshot
                     │
                     ▼
          ┌─────────────────────┐
          │      AI SLICE       │
          │  One Deep Analysis  │
          └──────────┬──────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Report    Takeaways   Thread Actions
          │          │          │
          └──────────┼──────────┘
                     ▼
             Research Threads
                     │
                Thread Versions
                     │
                     ▼
                  Timeline
                     │
                     ▼
                     UI
```

---

# 14. MVP Must-Have

| Area | Must Have |
|---|---|
| Company | Ticker-based company creation / lookup |
| Evidence | Market, valuation, financial, analyst, news snapshot |
| Evidence history | Historical snapshots retained |
| AI | One deep company-analysis pass |
| Report | Coherent English Master Research Report |
| Takeaways | 3–6 key takeaways |
| Threads | Company-specific research Threads |
| Thread actions | Continue / update / create / deprioritize / close / ephemeral |
| Lifecycle | Candidate / Active / Watching / Dormant / Archived |
| Timeline | Cross-date Thread continuity |
| UI | Current state + report + timeline |
| Reliability | Provider errors and AI errors isolated from stored evidence |
| Reproducibility | Prompt version, model, input hash, timestamp |

---

# 15. MVP Explicitly Not Doing

The following are deliberately excluded from the MVP.

## Not included: automatic trading

No order execution, portfolio rebalancing, or brokerage integration.

## Not included: investment recommendations

The AI does not output buy/sell recommendations, target prices, or ranked stocks.

## Not included: universal valuation engine

No attempt to build one valuation method for every company type.

Future valuation work may be company-archetype-specific.

## Not included: full knowledge graph

No complex entity graph or semantic graph database.

## Not included: multi-agent architecture

No autonomous network of specialized agents in the MVP.

## Not included: social publishing automation

No automatic publishing to X, WeChat, Xueqiu, Discord, etc.

## Not included: follower / community management

Community features are future scope.

## Not included: full article ingestion

The MVP does not ingest full web articles into the AI pipeline.

## Not included: K-line visualization

Market charts are explicitly excluded from the MVP.

## Not included: exhaustive Thread creation

The system must avoid creating a permanent Thread for every observation.

## Not included: forced historical linkage

Short-lived or low-value topics may remain attached only to the relevant report.

---

# 16. Token / Efficiency Design

The MVP deliberately uses a **Deep Report First** strategy.

The AI should receive a compact but sufficiently rich Evidence Snapshot and produce one coherent analysis.

Avoid:

```text
One call → dozens of structured objects
```

Prefer:

```text
One call → Master Report + Takeaways + Lightweight Thread Actions
```

The application should use deterministic application logic wherever possible for:

- section parsing;
- persistence;
- timestamps;
- content hashes;
- lifecycle bookkeeping;
- timeline rendering.

AI should be reserved for reasoning and interpretation.

---

# 17. Definition of Done for the MVP

A company analysis is considered successful when the system can:

1. Accept a ticker.
2. Build a current Evidence Snapshot.
3. Persist that snapshot without overwriting history.
4. Generate one coherent English research report.
5. Produce a small set of key takeaways.
6. Identify which existing research Threads changed.
7. Create a new Thread only when a topic is sufficiently persistent or important.
8. Keep ephemeral topics attached to a report without forcing persistence.
9. Show what changed since the previous research point.
10. Display the latest report and current Thread state in the UI.
11. Preserve historical Thread versions.
12. Re-run analysis deterministically using model / prompt / input metadata.
13. Recover cleanly from data-provider or AI-provider failures.

---

# 18. Example MVP Scenario — Walmart

```text
User enters: WMT
        ↓
Evidence Snapshot
        ↓
Gemini Research Pass
        ↓
Master Report
        ↓
Key Takeaways
        ↓
Thread Actions
```

Possible current state:

```text
ACTIVE
● Core Retail Economics
● Advertising / Marketplace
● E-commerce
● Store Network

WATCHING
○ Sam's Club

EPHEMERAL
△ Tariff Exposure
```

Next month, the system may produce:

```text
↑ Advertising / Marketplace
→ Store Network
↓ Sam's Club
NEW Consumer Mix
CLOSE Tariff Exposure
```

The product does not assume in advance which of these must exist forever.

---

# 19. Next Implementation Steps

After this document is frozen, development proceeds in this order:

### Step 2 — Domain Schema

Define the minimum database schema for:

- Company
- Company Archetype
- Evidence Snapshot
- Research Report
- Research Thread
- Thread Version
- Thread Action

### Step 3 — Company Archetype / Candidate Thread Framework

Define the first small set of archetypes and their candidate thread libraries.

### Step 4 — Slice 1

Stabilize OpenBB/yfinance evidence acquisition and normalization.

### Step 5 — AI Slice

Replace the current over-structured AI output with:

```text
Master Report
Key Takeaways
Thread Actions
```

and keep AI output token-efficient.

### Step 6 — Thread Continuity

Implement Thread lifecycle and cross-date versions.

### Step 7 — UI

Implement Current Research + Timeline views.

### Step 8 — Integration Test

Validate at least four different company archetypes:

- WMT — Retail / Consumer
- MRVL — Semiconductor / AI infrastructure
- UBER — Platform / Mobility
- GOOGL — Platform / Advertising / Cloud / AI

---

# 20. Final Frozen Architecture

```text
                         COMPANY
                            │
                    Company Archetype
                            │
                 Candidate Thread Framework
                            │
                            ▼
                   ┌────────────────┐
                   │    SLICE 1     │
                   │ Evidence Layer │
                   └───────┬────────┘
                           │
                    Evidence Snapshot
                           │
                           ▼
                   ┌────────────────┐
                   │    AI SLICE    │
                   │ One Deep Pass  │
                   └───────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Report      Takeaways   Thread Actions
              │            │            │
              └────────────┼────────────┘
                           ▼
                    Research Threads
                           │
                    Thread Versions
                           │
                           ▼
                        Timeline
                           │
                           ▼
                      Research UI
```

**This architecture is frozen for MVP design.** Subsequent work should modify implementation details only when necessary to satisfy this specification; it should not add new product features without an explicit scope review.
