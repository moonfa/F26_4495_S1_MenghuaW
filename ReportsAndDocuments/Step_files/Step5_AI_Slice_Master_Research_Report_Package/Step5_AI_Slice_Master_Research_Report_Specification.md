# AI-Assisted Personal Investment App — Step 5
## AI Slice / Master Research Report Specification

**Version:** 1.0  
**Status:** Frozen for Step 5 implementation  

## 1. Objective

The AI Slice answers: **What does the current evidence mean for understanding this company?**

The MVP uses **Deep Narrative First** and returns only:

1. One coherent English **Master Research Report**
2. **3–6 Key Takeaways**
3. A small set of **Thread Actions**

No large collection of parallel structured AI objects.

```text
Evidence Snapshot
        ↓
     AI / Gemini
        ↓
Master Research Report
Key Takeaways
Thread Actions
```

## 2. Relationship with the Previous Report

**Yes, the relationship is visible, but the new report does not inherit the previous report in full.**

Three mechanisms handle continuity:

### A. Report Lineage

```text
current_report.previous_report_id → previous_report
```

This answers: which report immediately preceded this review? It is for history, navigation and comparison.

### B. Evidence Delta

Before the AI call, Python compares the current EvidenceSnapshot with the previous one and creates a compact deterministic delta.

Example:

```text
Price: 108.14 → 110.02
Forward P/E: 37.8 → 39.1
Revenue growth: unchanged
New company news: +3
Analyst consensus: 115 → 118
```

The AI receives the delta, not the complete previous evidence payload.

### C. Thread Actions

Long-term continuity is carried by Research Threads:

```text
Report A → Advertising Thread
Report B → UPDATE / Importance Increased
Report C → CONTINUE / Importance Unchanged
```

Therefore:

```text
Report Lineage   = report history
Evidence Delta   = factual change
Thread Continuity = durable research continuity
```

## 3. Frozen Design Principle

**Report = current snapshot.** A report is immutable after generation.

**Thread = continuity.** A thread records what remains worth tracking over time.

**Ephemeral topic = local.** A short-lived issue does not have to become persistent.

## 4. Do Not Send the Full Previous Report to Gemini

Sending full historical reports causes token waste, narrative anchoring and repetitive output.

The AI should receive only:

```text
Current Evidence
+ Evidence Delta
+ Previous Key Takeaways
+ Active / Watching Thread summaries
+ Relevant Thread Versions
+ Analysis Mode
```

The full historical report remains stored for UI/history.

## 5. Master Research Report

The report should recover the depth and flow of the original demo. Recommended structure:

1. Business Model & Earnings Logic  
2. Investment Classification  
3. Moat & Competitive Position  
4. Financial Quality  
5. Valuation Context  
6. Key Growth Drivers  
7. Catalysts  
8. Key Risks  
9. What Matters Most Now  
10. What to Monitor

The report should read like one coherent analyst note, not a collection of independent JSON fields.

## 6. Key Takeaways

Return **3–6** concise conclusions. They must be derived from the report and introduce no new facts.

## 7. Thread Actions

Allowed actions:

```text
continue
update
create
deprioritize
close
ephemeral
```

Minimal fields:

```text
action
thread_id (nullable)
title
importance
importance_change
change_summary
```

The AI does not rewrite the full Thread.

## 8. Initial vs Follow-up Review

### Initial

```text
review_type = initial
previous_report_id = null
```

Full baseline analysis. Thread Actions may create initial persistent threads.

### Follow-up

```text
review_type = full_follow_up
```

The AI receives current evidence, evidence delta, previous takeaways, and relevant active thread context.

## 9. What Changed Since the Last Review

Every follow-up report should explicitly include a compact section:

```text
## What Changed Since the Last Review
```

Normally 2–5 high-value changes. This is the primary user-visible link between consecutive reports.

## 10. Material Change Detection

Before Gemini runs, deterministic comparison should check:

- financial metric changes
- valuation changes
- analyst consensus changes
- new company news
- missing/restored evidence sections
- material price or market-cap changes

The result is:

```text
material_change = true / false
```

## 11. Duplicate / Low-Change Rules

### Exact duplicate

If current `content_hash` equals the previous snapshot hash and model/prompt version are unchanged:

> Do not call Gemini again. Reuse the existing report.

### Low change

If evidence changed but there is no meaningful research change:

```text
review_type = low_change
```

The AI may produce a shorter update focused on what changed, what did not change, and Thread importance. User can still request a full refresh.

## 12. Full Follow-up Review

Use a full review when major financial metrics, earnings/guidance, strategic news, valuation, important Thread states, or an explicit user request justify it.

## 13. Minimal AI Output Schema

```python
class MasterResearchReport(BaseModel):
    report_markdown: str
    key_takeaways: list[str]
    what_changed: str
    thread_actions: list[ThreadAction]

class ThreadAction(BaseModel):
    action: Literal[
        "continue", "update", "create",
        "deprioritize", "close", "ephemeral"
    ]
    thread_id: str | None
    title: str
    importance: Literal["high", "medium", "low"]
    importance_change: Literal[
        "new", "increased", "unchanged", "decreased"
    ]
    change_summary: str
```

## 14. ResearchReport Relationship

The eventual ResearchReport record should contain:

```text
report_id
company_id
snapshot_id
previous_report_id
review_type
material_change
model
prompt_version
input_hash
report_markdown
key_takeaways
what_changed
created_at
```

Longitudinal continuity remains separate:

```text
ResearchReport
      ↓
ThreadAction
      ↓
ResearchThread
      ↓
ThreadVersion
```

## 15. Runtime Flow

```text
User → Slice 1
      ↓
Find previous Snapshot + Report
      ↓
Compare evidence
      ↓
Build Evidence Delta
      ↓
Load previous Takeaways + relevant Threads
      ↓
Gemini
      ↓
Report + Takeaways + Thread Actions
      ↓
ResearchReport
      ↓
Thread processing / Timeline
      ↓
UI
```

## 16. UI

The company page should show:

```text
Last Review
What Changed
Key Takeaways
Master Research Report
Active Research Threads
Timeline
```

Historical reports remain accessible but do not dominate the current view.

## 17. Critical Design Distinction

Do **not** make every report a version of the previous report.

```text
Report = immutable current view
Thread Version = longitudinal state
previous_report_id = navigation / comparison
thread_id = research continuity
```

So:

```text
Report A → Report B → Report C
```
is report history, while:

```text
Advertising Thread
   → Version 1
   → Version 2
   → Version 3
```
is research continuity.

## 18. Frozen Step 5 Decision

The MVP adopts:

> **One deep current-state Master Research Report + 3–6 Key Takeaways + a small set of Thread Actions.**

Temporal continuity is represented by **Report Lineage + Evidence Delta + Thread Continuity**.

The current report explicitly contains **What Changed Since the Last Review**.
