# AI-Assisted Personal Investment App — Step 3
## Company Archetype & Candidate Thread Framework

**Document:** Company Archetype & Candidate Thread Framework  
**Version:** 1.0  
**Date:** 2026-09-24  
**Depends on:** MVP / Design Freeze v1.0; Domain Model & Schema Design v1.0  
**Status:** Frozen for Step 3; implementation follows later steps

---

## 1. Purpose

Step 3 defines the first reusable **Company Archetype** and **Candidate Persistent Thread** framework for the MVP.

The purpose is not to create a universal research checklist.

The purpose is to give the AI and the user a **starting research map**:

> Company Archetype → Candidate Thread Framework → Company-specific Persistent Threads → Dynamic lifecycle

A candidate thread is a suggestion. It is not automatically a persistent research object.

---

## 2. Core Design Principle

### Different company types have different persistent research themes.

A retail company should not be analyzed through the same persistent-thread structure as a semiconductor company, an internet platform, or a mobility marketplace.

However:

> **Archetype determines the candidate framework; the specific company and current investment logic determine the actual Threads.**

This means the system has three levels:

```text
Company Archetype
        ↓
Candidate Thread Library
        ↓
Company-specific Persistent Threads
        ↓
Current importance / lifecycle
```

For example, the Retail / Consumer archetype may suggest:

- Consumer Mix
- Same-store Sales
- E-commerce
- Advertising / Marketplace
- Store Network
- Membership Economics

But Walmart does not have to activate all six. A specific company may also create a new thread that does not exist in the archetype library.

---

## 3. Four Core Rules

### Rule 1 — Candidate Threads are optional

The archetype library is a discovery aid, not a checklist.

### Rule 2 — Persistent Threads are company-specific

Two companies in the same archetype may have very different persistent Threads.

### Rule 3 — Current importance is dynamic

A Thread may move:

```text
Candidate → Active → Watching → Dormant → Archived
```

and can later become active again.

### Rule 4 — Short-lived topics do not need persistence

A topic can be attached only to one Report as:

```text
ephemeral
```

or can exist for a short period without becoming a long-term Thread.

---

# 4. Archetype 1 — Retail / Consumer

## Economic structure

Typical businesses monetize consumer demand through stores, e-commerce, brands, memberships, advertising, or consumer services.

## Candidate Persistent Threads

| Candidate Thread | What it tracks | Typical persistence |
|---|---|---|
| Core Retail Economics | traffic, pricing, basket, same-store sales, unit economics | High |
| Consumer Mix | trade-down/up, income cohorts, category mix | Medium–High |
| Margin Structure | gross margin, shrink, labor, mix, operating leverage | High |
| E-commerce Economics | digital growth, fulfillment economics, profitability | Medium–High |
| Advertising / Marketplace | higher-margin monetization layer | Medium–High |
| Store Network / Distribution | density, convenience, fulfillment advantage | High |
| Membership Economics | members, renewal, fee income, engagement | Medium–High |
| International Expansion | geography-specific growth and economics | Medium |
| Capital Allocation | buybacks, dividends, capex, M&A | High |
| Brand / Product Power | pricing power, brand strength, category leadership | High |

## Usually not persistent by default

- One-week promotional events
- Short-lived product launches
- A single viral social-media story
- One isolated weather event
- One quarter's unusual inventory issue unless it exposes a structural problem
- Temporary stock-price volatility without a business mechanism

## Example — Walmart

Potential actual Threads:

```text
Core Retail Economics
Advertising / Marketplace
E-commerce Economics
Store Network
Sam's Club / Membership Economics
Consumer Mix
```

Potential ephemeral topic:

```text
Temporary tariff concern
```

The tariff topic becomes persistent only if it begins to alter a durable earnings mechanism.

---

# 5. Archetype 2 — Semiconductor / AI Infrastructure

## Economic structure

Businesses monetize semiconductor products, compute infrastructure, networking, custom silicon, memory, manufacturing, or critical data-center components.

## Candidate Persistent Threads

| Candidate Thread | What it tracks | Typical persistence |
|---|---|---|
| Product Cycle / Roadmap | node, product launches, refresh cycle | High |
| TAM / Demand Cycle | end-market demand and secular growth | High |
| Customer Concentration | major customers / hyperscalers / OEMs | High |
| Design Wins / Content | adoption, sockets, platform penetration | High |
| AI / Accelerator Exposure | AI-driven compute demand | High |
| Custom ASIC / Substitution | ASIC vs GPU / merchant silicon dynamics | High |
| Networking / Interconnect | bandwidth, switching, optical, fabric demand | High |
| Gross Margin Structure | mix, pricing, utilization, product economics | High |
| Capex / Supply Constraints | manufacturing, capacity, lead times | Medium–High |
| Competition / Technology Risk | rival products and technology transitions | High |

## Usually not persistent by default

- One specific product benchmark
- One customer rumor without evidence
- One temporary supply interruption
- Short-term component shortage once normalized
- One earnings-day price reaction

## Example — Marvell

Potential actual Threads:

```text
Custom ASIC
Hyperscaler Design Wins
AI Networking / Interconnect
Data-center Demand
Gross Margin / Mix
Customer Concentration
```

Potential ephemeral topic:

```text
One quarter's inventory normalization
```

The topic becomes persistent if inventory repeatedly affects the underlying earnings cycle.

---

# 6. Archetype 3 — Platform / Internet

## Economic structure

Businesses create network effects or platform economics around users, engagement, transactions, advertising, cloud, subscriptions, data, or ecosystems.

## Candidate Persistent Threads

| Candidate Thread | What it tracks | Typical persistence |
|---|---|---|
| User / Engagement Engine | MAU, DAU, engagement, retention | High |
| Monetization | ARPU, ad load, pricing, subscription economics | High |
| Network Effects | liquidity, sellers/buyers, ecosystem density | High |
| Unit Economics | CAC, contribution margin, take rate | High |
| AI / Product Disruption | AI impact on product and economics | High |
| Search / Discovery / Distribution | traffic and demand capture | Medium–High |
| Advertising Economics | ad demand, targeting, pricing | High |
| Cloud / Infrastructure Economics | consumption, margins, capex | High |
| Competitive Position | rival platforms, switching, bundling | High |
| Regulation / Policy | structural regulatory exposure | Medium–High |
| Capital Allocation | buybacks, M&A, capex | Medium–High |

## Usually not persistent by default

- One viral product feature
- One temporary traffic spike
- One app-store ranking change
- A single competitor announcement without a durable strategic implication
- Social-media sentiment

## Example — Google

Potential actual Threads:

```text
Search Monetization
AI Search / Gemini
Cloud Growth & Margin
YouTube Monetization
AI Capex / Return on Investment
Competitive Position
```

Potential ephemeral topic:

```text
One specific AI model benchmark
```

It becomes persistent only if it affects product adoption or economics.

---

# 7. Archetype 4 — Mobility / Marketplace

## Economic structure

Businesses coordinate supply and demand through a marketplace, often balancing users, providers, take rate, utilization, incentives, and regulatory constraints.

## Candidate Persistent Threads

| Candidate Thread | What it tracks | Typical persistence |
|---|---|---|
| Demand / Trips | bookings, trips, gross bookings | High |
| Take Rate / Monetization | platform share and pricing | High |
| Supply Economics | driver/provider supply and earnings | High |
| Network Effects | marketplace liquidity and density | High |
| Unit Economics | contribution margin, incentive intensity | High |
| Multi-product Cross-sell | mobility, delivery, adjacent products | Medium–High |
| Autonomous / New Technology | robotaxi, automation, replacement risk | Medium–High |
| Regulation | labor, safety, licensing | High |
| Competition | rivals, pricing, market structure | High |
| Capital Allocation | buybacks, M&A, investment | Medium |

## Usually not persistent by default

- One city launch
- One local regulatory hearing
- A single promotional campaign
- One celebrity/customer event
- One unusual surge-pricing episode

## Example — Uber

Potential actual Threads:

```text
Mobility Economics
Take Rate / Unit Economics
Delivery
Network Effects
Autonomous Driving / Robotaxi
Regulation
```

Potential ephemeral topic:

```text
One city's temporary licensing dispute
```

---

# 8. Company-Specific Threads

The framework must explicitly allow:

> **Company-specific Threads that do not exist in the archetype library.**

Examples:

### Walmart

```text
Sam's Club China
```

This is more specific than the generic `Membership Economics` candidate.

### Marvell

```text
Specific hyperscaler ASIC relationship
```

A particular strategic customer relationship may become a major company-specific thread.

### Uber

```text
Robotaxi commercialization
```

The general Mobility archetype contains `Autonomous / New Technology`, but Uber's robotaxi strategy can become a dedicated Thread.

### Google

```text
AI Search Cannibalization
```

This can be more specific than generic `AI / Product Disruption`.

## Rule

Company-specific Threads are allowed when at least one of these is true:

1. The topic materially affects the company's earnings mechanism.
2. It can change the long-term competitive position.
3. It requires repeated monitoring over multiple reports.
4. It is central to the user's personal thesis.

The Thread should not be created merely because the topic appears in one piece of news.

---

# 9. When Does a Candidate Become a Persistent Thread?

A candidate should generally become an Active Persistent Thread when **multiple** of the following are true:

### A. Economic relevance

It can materially affect:

- revenue
- margins
- cash flow
- capital intensity
- valuation assumptions
- competitive position

### B. Persistence

The topic is likely to matter across more than one reporting period.

### C. Monitoring value

There are observable indicators that can be tracked over time.

### D. Decision relevance

Changes in the topic could change the user's research conclusion.

### E. Recurrent evidence

New reports are likely to provide updates.

A one-off news item normally fails these tests.

---

# 10. Thread Lifecycle

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

Potentially important but not yet established.

### Active

Currently important to the company's research view.

### Watching

Not a main current driver, but worth monitoring.

### Dormant

No meaningful change across several reviews.

### Archived

No longer relevant under the current business model or thesis.

## Re-activation

An archived or dormant Thread may become active again when new evidence materially changes its importance.

---

# 11. Thread Importance

Importance should not be a permanent property.

The MVP uses:

```text
High
Medium
Low
```

with change:

```text
New
Increased
Unchanged
Decreased
```

Example:

```text
Advertising Monetization
August: Medium / New
September: High / Increased
October: High / Unchanged
December: Medium / Decreased
```

This records changing research attention without creating duplicate Threads.

---

# 12. Persistent vs Flexible vs Ephemeral

The MVP uses a practical three-level model:

| Level | Purpose | Time horizon | Example |
|---|---|---|---|
| Persistent | Core long-term research theme | Months–Years | Walmart store network |
| Flexible | Important but potentially cyclical | Weeks–Years | Consumer trade-down |
| Ephemeral | Local/temporary issue | Days–Weeks | Temporary tariff announcement |

Only Persistent and selected Flexible Threads need a durable Thread ID.

Ephemeral topics may live only inside the Report or Thread Action.

---

# 13. How AI Uses the Framework

The AI should NOT receive:

> “Create all candidate Threads.”

Instead it should receive:

```text
Company Archetype
+
Candidate Thread Library
+
Existing Active/Watching Threads
+
New Evidence
+
Latest Report context
```

Then it determines:

```text
continue existing thread
update existing thread
create new thread
deprioritize existing thread
close existing thread
mark ephemeral
```

This keeps the framework advisory rather than deterministic.

---

# 14. Example: WMT Across Time

### August

```text
Active
- Core Retail Economics
- Store Network
- E-commerce
- Advertising

Watching
- Sam's Club

No thread
- Temporary tariff concern
```

### September

New evidence shows stronger advertising monetization:

```text
Advertising
Medium → High

Store Network
High → Unchanged

Tariff
CREATE → Ephemeral
```

### October

Tariff issue fades:

```text
Tariff
Ephemeral → expires

Advertising
High → Unchanged

E-commerce
Medium → High
```

The system does not need to preserve a permanent tariff Thread.

---

# 15. Example: Same Archetype, Different Company

Two retail companies can have different Thread sets.

```text
Retail Archetype
       │
       ├── Walmart
       │    ├── Store Network
       │    ├── Advertising
       │    ├── E-commerce
       │    └── Sam's Club
       │
       └── Costco
            ├── Membership Economics
            ├── Renewal Rate
            ├── Merchandise Productivity
            └── International Expansion
```

Therefore:

> **Archetype similarity does not imply Thread similarity.**

---

# 16. MVP Scope — What Step 3 Defines

### Must define now

- First 4 archetypes
- Candidate Thread libraries
- Persistent / Flexible / Ephemeral distinction
- Thread activation logic
- Thread lifecycle
- Company-specific Thread rules
- AI's allowed Thread actions

### Not implemented in Step 3

- Database tables
- Thread similarity embeddings
- automatic semantic clustering
- vector database
- knowledge graph
- automatic taxonomy learning
- portfolio-level cross-company Threads
- multi-agent thread manager

These remain outside the current Step 3 implementation scope.

---

# 17. Frozen Decision

The MVP adopts this model:

```text
                  Company
                     │
              Company Archetype
                     │
          Candidate Thread Library
                     │
                     ▼
          Company-specific Threads
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   Persistent      Flexible     Ephemeral
       │             │
       └──────┬──────┘
              ▼
        Dynamic Lifecycle
              │
   Candidate → Active → Watching
                     ↓
                Dormant/Archived
```

The framework is intentionally **generative, not prescriptive**.

The system should help the user notice what deserves attention, while allowing each company to develop its own research structure over time.