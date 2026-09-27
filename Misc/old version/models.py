"""
Step 2 — Domain Model & Schema
Frozen per: MVP_Specification.md v1.0 (2026-09-23)

Stack: Python + FastAPI + PostgreSQL (SQLAlchemy 2.0 declarative)

Design decisions:
1. UUID string PKs generated in Python — portable between SQLite (local dev)
   and PostgreSQL (prod), no pgcrypto extension needed.
2. Semi-structured payloads (market_data, valuation, news, ...) use sa.JSON
   (JSONB on PostgreSQL, TEXT on SQLite).
3. Enums stored as plain strings (native_enum=False) for portability.
4. History is append-only: evidence snapshots, reports and thread versions
   are never overwritten — only superseded by newer rows.
5. AI is advisory (course proposal §3.5 / §3.6.4): every ThreadAction starts
   as `proposed` and only takes effect after explicit human review.
6. Token diagnostics (input_tokens / output_tokens) on each report, so token
   burn is measurable instead of "felt" (per the AI-slice redesign discussion).
7. Manual evidence entry (course proposal Appendix B.2) is preserved as a
   lightweight `evidence_items` table that can attach to a snapshot/report.

Terminology mapping (old proposal -> frozen MVP spec):
    Thesis            -> ResearchReport (snapshot of view at time T)
    ThesisNode        -> ResearchThread (cross-time research topic)
    EventImpact       -> ThreadAction   (what changed since last review)
    ThesisVersion     -> ThreadVersion  (state of a thread at time T)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enumerations (stored as strings)
# ---------------------------------------------------------------------------

class CompanyArchetype:
    RETAIL = "retail"
    CONSUMER = "consumer"
    SEMICONDUCTOR = "semiconductor"
    PLATFORM = "platform"
    MOBILITY = "mobility"
    SOFTWARE = "software"
    TELECOM = "telecom"
    BANK = "bank"
    UTILITY = "utility"
    INDUSTRIAL = "industrial"
    BIOTECH = "biotech"


class ThreadType:
    PERSISTENT = "persistent"   # long-lived, multi-year main lines
    FLEXIBLE = "flexible"       # medium-lived, importance rises/falls
    EPHEMERAL = "ephemeral"     # short-lived, attached to report(s) only


class ThreadStatus:
    CANDIDATE = "candidate"
    ACTIVE = "active"
    WATCHING = "watching"
    DORMANT = "dormant"
    ARCHIVED = "archived"


class Importance:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImportanceChange:
    INCREASED = "increased"
    UNCHANGED = "unchanged"
    DECREASED = "decreased"
    NEW = "new"


class ThreadActionType:
    CONTINUE = "continue"        # still relevant, no material change
    UPDATE = "update"            # still relevant, state/importance changed
    CREATE = "create"            # new cross-time topic emerged
    DEPRIORITIZE = "deprioritize"  # temporarily less important
    CLOSE = "close"              # no longer worth tracking
    EPHEMERAL = "ephemeral"      # worth mentioning once, no thread


class ReviewStatus:
    PROPOSED = "proposed"        # AI suggestion, awaiting human review
    APPROVED = "approved"        # human accepted
    REJECTED = "rejected"        # human rejected
    EDITED = "edited"            # human accepted with modifications


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------

class Company(Base):
    """The company under research. One row per ticker."""
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    ticker: Mapped[str] = mapped_column(sa.String(16), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    sector: Mapped[str | None] = mapped_column(sa.String(128))
    industry: Mapped[str | None] = mapped_column(sa.String(128))
    description: Mapped[str | None] = mapped_column(sa.Text)

    # Archetype determines the *candidate* thread framework (§3.4 of spec).
    # A company may carry secondary archetypes (e.g. GOOGL: platform + cloud/AI).
    primary_archetype: Mapped[str | None] = mapped_column(sa.String(64))
    secondary_archetypes: Mapped[list | None] = mapped_column(sa.JSON)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    snapshots: Mapped[list["EvidenceSnapshot"]] = relationship(back_populates="company")
    reports: Mapped[list["ResearchReport"]] = relationship(back_populates="company")
    threads: Mapped[list["ResearchThread"]] = relationship(back_populates="company")


# ---------------------------------------------------------------------------
# Candidate thread library (Step 3 seeds this table)
# ---------------------------------------------------------------------------

class CandidateThread(Base):
    """
    Per-archetype candidate thread framework (§3.4).
    These are *candidates*, not mandatory threads — the actual persistent
    threads for a company are created via ThreadActions over time.
    """
    __tablename__ = "candidate_threads"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    archetype: Mapped[str] = mapped_column(sa.String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text)
    suggested_type: Mapped[str] = mapped_column(
        sa.String(32), default=ThreadType.PERSISTENT
    )
    sort_order: Mapped[int] = mapped_column(sa.Integer, default=0)


# ---------------------------------------------------------------------------
# Slice 1 — Evidence
# ---------------------------------------------------------------------------

class EvidenceSnapshot(Base):
    """
    "What do we know right now?" — point-in-time facts only, no AI opinion.
    Never overwritten; each run appends a new row.
    """
    __tablename__ = "evidence_snapshots"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("companies.id"), nullable=False, index=True
    )
    taken_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=_utcnow, index=True
    )
    provider: Mapped[str] = mapped_column(sa.String(64), default="yfinance")

    market_data: Mapped[dict | None] = mapped_column(sa.JSON)      # price, mkt cap, 52w, beta...
    valuation: Mapped[dict | None] = mapped_column(sa.JSON)        # PE, PEG, PS, EV/EBITDA...
    financials: Mapped[dict | None] = mapped_column(sa.JSON)       # growth, margins, ROE, FCF...
    analyst: Mapped[dict | None] = mapped_column(sa.JSON)         # consensus, targets...
    news: Mapped[list | None] = mapped_column(sa.JSON)            # [{date,title,source,url,excerpt}]

    raw_payload: Mapped[dict | None] = mapped_column(sa.JSON)     # verbatim provider payload
    content_hash: Mapped[str | None] = mapped_column(sa.String(128), index=True)

    company: Mapped["Company"] = relationship(back_populates="snapshots")
    reports: Mapped[list["ResearchReport"]] = relationship(back_populates="snapshot")

    __table_args__ = (
        sa.Index("ix_snapshots_company_taken", "company_id", "taken_at"),
    )


class EvidenceItem(Base):
    """
    Manually entered evidence (course proposal Appendix B.2):
    a public event/note with its original source link.
    May attach to a snapshot/report or stand alone.
    """
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("companies.id"), nullable=False, index=True
    )
    snapshot_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("evidence_snapshots.id")
    )
    title: Mapped[str] = mapped_column(sa.String(512), nullable=False)
    source_url: Mapped[str | None] = mapped_column(sa.String(2048))
    source_name: Mapped[str | None] = mapped_column(sa.String(256))
    published_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    note: Mapped[str | None] = mapped_column(sa.Text)             # user note / excerpt
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_utcnow)


# ---------------------------------------------------------------------------
# AI Slice — Research report
# ---------------------------------------------------------------------------

class ResearchReport(Base):
    """
    "What do I think matters now?" — one coherent English research note per
    AI pass, plus 3–6 takeaways. The report is a *snapshot*, not the
    company's permanent knowledge structure.
    """
    __tablename__ = "research_reports"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("companies.id"), nullable=False, index=True
    )
    snapshot_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("evidence_snapshots.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=_utcnow, index=True
    )

    model: Mapped[str | None] = mapped_column(sa.String(128))     # e.g. gemini-2.x
    prompt_version: Mapped[str | None] = mapped_column(sa.String(64))

    report_markdown: Mapped[str] = mapped_column(sa.Text, nullable=False)
    key_takeaways: Mapped[list | None] = mapped_column(sa.JSON)   # 3–6 strings

    # Token diagnostics — measure, don't guess.
    input_tokens: Mapped[int | None] = mapped_column(sa.Integer)
    output_tokens: Mapped[int | None] = mapped_column(sa.Integer)

    company: Mapped["Company"] = relationship(back_populates="reports")
    snapshot: Mapped["EvidenceSnapshot | None"] = relationship(back_populates="reports")
    thread_actions: Mapped[list["ThreadAction"]] = relationship(back_populates="report")

    __table_args__ = (
        sa.Index("ix_reports_company_created", "company_id", "created_at"),
    )


# ---------------------------------------------------------------------------
# Thread continuity
# ---------------------------------------------------------------------------

class ResearchThread(Base):
    """
    "What is worth following across time?" — a persistent research object
    with a stable ID. Titles may evolve; continuity is by ID, not by string.
    """
    __tablename__ = "research_threads"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("companies.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(sa.String(256), nullable=False)

    thread_type: Mapped[str] = mapped_column(sa.String(32), default=ThreadType.FLEXIBLE)
    status: Mapped[str] = mapped_column(sa.String(32), default=ThreadStatus.CANDIDATE)
    importance: Mapped[str] = mapped_column(sa.String(16), default=Importance.MEDIUM)

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_utcnow)
    last_active_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_utcnow)

    company: Mapped["Company"] = relationship(back_populates="threads")
    versions: Mapped[list["ThreadVersion"]] = relationship(
        back_populates="thread", order_by="ThreadVersion.valid_from"
    )

    __table_args__ = (
        sa.Index("ix_threads_company_status", "company_id", "status"),
    )


class ThreadVersion(Base):
    """
    State of one thread at one research point. Only created when something
    material changed — no forced version per report.
    """
    __tablename__ = "thread_versions"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    thread_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("research_threads.id"), nullable=False, index=True
    )
    report_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("research_reports.id")
    )

    state_summary: Mapped[str | None] = mapped_column(sa.Text)
    importance: Mapped[str] = mapped_column(sa.String(16), default=Importance.MEDIUM)
    importance_change: Mapped[str] = mapped_column(
        sa.String(16), default=ImportanceChange.UNCHANGED
    )
    confidence: Mapped[str | None] = mapped_column(sa.String(16))  # high/medium/low

    valid_from: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_utcnow)
    valid_to: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_utcnow)

    thread: Mapped["ResearchThread"] = relationship(back_populates="versions")

    __table_args__ = (
        sa.Index("ix_thread_versions_thread_from", "thread_id", "valid_from"),
    )


class ThreadAction(Base):
    """
    The bridge between time points: what this report did to the thread map.
    AI proposes; human disposes (review_status gate).
    """
    __tablename__ = "thread_actions"

    id: Mapped[str] = mapped_column(sa.String(36), primary_key=True, default=_uuid)
    report_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("research_reports.id"), nullable=False, index=True
    )
    # NULL for `create` (thread doesn't exist yet) and `ephemeral` (no thread).
    thread_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("research_threads.id")
    )

    action: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    title: Mapped[str | None] = mapped_column(sa.String(256))  # for `create`
    importance: Mapped[str | None] = mapped_column(sa.String(16))
    importance_change: Mapped[str | None] = mapped_column(sa.String(16))
    change_summary: Mapped[str | None] = mapped_column(sa.Text)

    # Human-in-the-loop gate (course proposal §3.5).
    review_status: Mapped[str] = mapped_column(sa.String(32), default=ReviewStatus.PROPOSED)
    reviewer_note: Mapped[str | None] = mapped_column(sa.Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), default=_utcnow)

    report: Mapped["ResearchReport"] = relationship(back_populates="thread_actions")
