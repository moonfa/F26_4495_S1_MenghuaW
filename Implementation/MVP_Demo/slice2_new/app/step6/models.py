"""Additive Step 6 tables; imports the SAME Base used by the existing app."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, UniqueConstraint, Index
from ..database import Base
from ..models import Company, EvidenceSnapshot, AnalysisDraft

def utcnow():
    return datetime.now(timezone.utc)

class ResearchReport(Base):
    __tablename__ = "research_reports"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey(f"{Company.__tablename__}.id"), nullable=False, index=True)
    snapshot_id = Column(Integer, ForeignKey(f"{EvidenceSnapshot.__tablename__}.id"), nullable=False)
    source_analysis_draft_id = Column(Integer, ForeignKey(f"{AnalysisDraft.__tablename__}.id"), unique=True)
    previous_report_id = Column(Integer, ForeignKey("research_reports.id"))
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    status = Column(String(20), default="success", nullable=False)
    review_type = Column(String(40))
    material_change = Column(Boolean)
    provider = Column(String(50))
    model = Column(String(120))
    prompt_version = Column(String(120))
    evidence_content_hash = Column(String(64))
    thread_state_hash = Column(String(64))
    input_hash = Column(String(64))
    report_markdown = Column(Text, nullable=False)
    key_takeaways = Column(JSON, default=list)
    what_changed = Column(Text)
    evidence_delta = Column(JSON)
    valuation_implications = Column(JSON)
    language = Column(String(10), default="en")
    __table_args__ = (Index("ix_report_company_date", "company_id", "created_at", "id"),)

class ResearchThread(Base):
    __tablename__ = "research_threads"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey(f"{Company.__tablename__}.id"), nullable=False, index=True)
    title = Column(String(240), nullable=False)
    thread_type = Column(String(80))
    status = Column(String(30), default="active", nullable=False)
    importance = Column(String(20), default="medium", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    last_active_at = Column(DateTime(timezone=True), default=utcnow)

class ThreadVersion(Base):
    __tablename__ = "thread_versions"
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("research_threads.id"), nullable=False)
    report_id = Column(Integer, ForeignKey("research_reports.id"), nullable=False)
    state_summary = Column(Text, nullable=False)
    importance = Column(String(20))
    importance_change = Column(String(20))
    created_at = Column(DateTime(timezone=True), default=utcnow)

class ThreadAction(Base):
    __tablename__ = "thread_actions"
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("research_reports.id"), nullable=False)
    thread_id = Column(Integer, ForeignKey("research_threads.id"))
    action = Column(String(30), nullable=False)
    title = Column(String(240), nullable=False)
    importance = Column(String(20), default="medium")
    importance_change = Column(String(20), default="unchanged")
    change_summary = Column(Text, default="")
    original_proposal = Column(JSON)
    review_status = Column(String(20), default="proposed", nullable=False)
    reviewer_note = Column(Text)
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    __table_args__ = (UniqueConstraint("report_id","action","title", name="uq_report_action_title"),)

class PersonalResearchNote(Base):
    __tablename__ = "personal_research_notes"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey(f"{Company.__tablename__}.id"), nullable=False, index=True)
    report_id = Column(Integer, ForeignKey("research_reports.id"))
    thread_id = Column(Integer, ForeignKey("research_threads.id"))
    note_type = Column(String(40), default="general", nullable=False)
    body = Column(Text, nullable=False)
    valuation_assumptions = Column(JSON)
    review_due_at = Column(DateTime(timezone=True))
    supersedes_note_id = Column(Integer, ForeignKey("personal_research_notes.id"))
    created_at = Column(DateTime(timezone=True), default=utcnow)
