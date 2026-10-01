"""Backfill is idempotent; never edits legacy AnalysisDraft or EvidenceSnapshot."""
import hashlib
import json
from sqlalchemy import select
from .models import ResearchReport, ResearchThread, ThreadVersion, ThreadAction
from ..models import AnalysisDraft, EvidenceSnapshot
from .models import utcnow
from sqlalchemy import or_, and_

def canonical_hash(data):
    return hashlib.sha256(json.dumps(data or {}, sort_keys=True, separators=(",",":"), ensure_ascii=False, default=str).encode()).hexdigest()

def import_successful_drafts(session, company_id=None):
    query = (select(AnalysisDraft, EvidenceSnapshot)
             .join(EvidenceSnapshot, AnalysisDraft.snapshot_id == EvidenceSnapshot.id)
             .where(AnalysisDraft.status == "success"))
    if company_id is not None:
        query = query.where(EvidenceSnapshot.company_id == company_id)
    rows = session.execute(query.order_by(AnalysisDraft.created_at, AnalysisDraft.id)).all()
    imported = 0
    for draft, snapshot in rows:
        result = draft.output_payload or {}
        if not isinstance(result, dict) or not result.get("report_markdown"):
            continue  # legacy structured analysis isn't a Step5A master report
        if session.scalar(select(ResearchReport.id).where(ResearchReport.source_analysis_draft_id == draft.id)):
            continue
        previous = session.scalar(
            select(ResearchReport).join(AnalysisDraft, ResearchReport.source_analysis_draft_id == AnalysisDraft.id).where(
                ResearchReport.company_id == snapshot.company_id,
                or_(ResearchReport.created_at < draft.created_at,
                    and_(ResearchReport.created_at == draft.created_at, AnalysisDraft.id < draft.id)),
            ).order_by(ResearchReport.created_at.desc(), ResearchReport.id.desc())
        )
        # Existing Step5A previous_report_id references an AnalysisDraft, not ResearchReport.
        historical_draft_id = (result.get("previous_report_id")
                               if result.get("previous_report_ref_type") != "research_report"
                               else None)
        if historical_draft_id:
            mapped = session.scalar(select(ResearchReport).where(
                ResearchReport.source_analysis_draft_id == historical_draft_id,
                ResearchReport.company_id == snapshot.company_id,
            ))
            if mapped and mapped.id != (previous.id if previous else None):
                previous = mapped
        report = ResearchReport(
            company_id=snapshot.company_id, snapshot_id=snapshot.id,
            source_analysis_draft_id=draft.id,
            previous_report_id=previous.id if previous else None,
            created_at=draft.created_at, status="success",
            review_type=result.get("review_type"),
            material_change=result.get("material_change"),
            model=draft.model, prompt_version=draft.prompt_version,
            evidence_content_hash=canonical_hash(snapshot.normalized_payload),
            provider=draft.provider,
            thread_state_hash=result.get("thread_state_hash") or canonical_hash([]),
            input_hash=draft.input_hash,
            report_markdown=result["report_markdown"],
            key_takeaways=result.get("key_takeaways") or [],
            what_changed=result.get("what_changed"),
            evidence_delta=result.get("evidence_delta"),
            valuation_implications=result.get("valuation_implications"),
            language=result.get("language") or "en",
        )
        session.add(report)
        session.flush()
        seen_actions = set()
        for item in result.get("thread_actions") or []:
            if not isinstance(item, dict) or item.get("action") not in {"continue","update","create","deprioritize","close","ephemeral"}:
                continue
            action_key = (item.get("action"),str(item.get("title") or "Untitled").strip().casefold())
            if action_key in seen_actions:
                continue
            seen_actions.add(action_key)
            proposed_thread_id = item.get("thread_id")
            linked = None
            if proposed_thread_id and str(proposed_thread_id).isdigit():
                linked = session.get(ResearchThread, int(proposed_thread_id))
                if linked is not None and linked.company_id != report.company_id:
                    linked = None
            if linked is None and item["action"] in {"continue","update","deprioritize","close"}:
                # Use an exact, case-insensitive title match when AI did not provide a valid thread ID.
                matches = session.scalars(select(ResearchThread).where(
                    ResearchThread.company_id == report.company_id,
                    ResearchThread.title.ilike(str(item.get("title") or "").strip())
                )).all()
                linked = matches[0] if len(matches) == 1 else None
            session.add(ThreadAction(
                thread_id=linked.id if linked else None,
                original_proposal=item,
                report_id=report.id, action=item["action"],
                title=str(item.get("title") or "Untitled")[:240],
                importance=item.get("importance") or "medium",
                importance_change=item.get("importance_change") or "unchanged",
                change_summary=item.get("change_summary") or "",
            ))
        imported += 1
    session.commit()
    return imported


def active_thread_context(session, company_id, limit=8):
    """Compact, human-approved longitudinal context for ONE Gemini call."""
    rows = session.scalars(select(ResearchThread).where(
        ResearchThread.company_id == company_id,
        ResearchThread.status.in_(["active", "watching"]),
    ).order_by(ResearchThread.last_active_at.desc(), ResearchThread.id.desc()).limit(limit)).all()
    context = []
    for thread in rows:
        last = session.scalar(select(ThreadVersion).where(
            ThreadVersion.thread_id == thread.id,
        ).order_by(ThreadVersion.created_at.desc(), ThreadVersion.id.desc()))
        context.append({"thread_id": str(thread.id), "title": thread.title,
                        "status": thread.status, "importance": thread.importance,
                        "last_approved_summary": last.state_summary if last else ""})
    return context
