import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .ai.analyzer import AIAnalyzer
from .ai.prompts import PROMPT_VERSION
from .ai.provider import AIProviderError, build_ai_provider
from .ai.report_context import build_review_context
from .adapters.openbb_adapter import OpenBBAdapter, OpenBBAdapterError
from .database import Base, engine, get_session
from .models import AnalysisDraft, Company, EvidenceSnapshot, Source
from .step6.models import ResearchReport
from .step6.service import canonical_hash, import_successful_drafts, active_thread_context
from .schemas import (
    AnalysisDraftResponse,
    AnalysisRequest,
    EvidenceHistoryItem,
    EvidenceSyncResponse,
    SyncRequest,
)

# Keep legacy tables auto-created for Slice 1/2, but Step6 tables must be
# created by the explicit backed-up migration, not implicitly on app import.
Base.metadata.create_all(engine, tables=[
    Company.__table__, Source.__table__, EvidenceSnapshot.__table__, AnalysisDraft.__table__
])


def build_router(provider: str) -> APIRouter:
    router = APIRouter(prefix="/api/v1")
    adapter = OpenBBAdapter(provider=provider)

    @router.get("/health")
    def health() -> dict[str, Any]:
        ai_provider = os.getenv("AI_PROVIDER", "mock").strip().lower()
        return {
            "status": "ok",
            "provider": provider,
            "ai_provider": ai_provider,
        }

    @router.post("/evidence/sync", response_model=EvidenceSyncResponse)
    def sync_evidence(payload: SyncRequest, session: Session = Depends(get_session)) -> EvidenceSyncResponse:
        ticker = payload.ticker.strip().upper()
        requested_at = datetime.now(timezone.utc)

        company = session.scalar(select(Company).where(Company.ticker == ticker))
        if company is None:
            company = Company(ticker=ticker, name=ticker)
            session.add(company)
            session.flush()

        source = session.scalar(
            select(Source).where(
                Source.provider == "openbb",
                Source.source_type == provider,
                Source.name == "OpenBB Equity Profile",
            )
        )
        if source is None:
            source = Source(
                provider="openbb",
                source_type=provider,
                name="OpenBB Equity Profile",
                url=adapter.yahoo_url(ticker) if provider == "yfinance" else None,
            )
            session.add(source)
            session.flush()

        snapshot = EvidenceSnapshot(
            company_id=company.id,
            source_id=source.id,
            ticker=ticker,
            operation="equity.profile",
            requested_at=requested_at,
            status="pending",
            request_params={
                "symbol": ticker,
                "provider": provider,
                "snapshot_version": getattr(adapter, "SNAPSHOT_VERSION", "research-snapshot-v2.1"),
                "chart": False,
                "sections": ["profile", "quote", "metrics", "consensus", "income", "cash", "news"],
            },
        )
        session.add(snapshot)
        session.flush()

        try:
            normalized, meta = adapter.get_equity_research_snapshot(ticker)
            raw = meta.get("raw", {})
            raw_bytes = json.dumps(raw, sort_keys=True, default=str, ensure_ascii=False).encode("utf-8")
            retrieved_at = datetime.now(timezone.utc)

            snapshot.status = "success"
            snapshot.retrieved_at = retrieved_at
            snapshot.raw_payload = raw
            snapshot.normalized_payload = normalized
            snapshot.record_count = sum(meta.get("raw_sections", {}).values())
            snapshot.content_hash = hashlib.sha256(raw_bytes).hexdigest()

            company_name = normalized.get("company", {}).get("name")
            if company_name and company.name == ticker:
                company.name = str(company_name)

            session.commit()
            session.refresh(snapshot)

            return EvidenceSyncResponse(
                snapshot_id=snapshot.id,
                ticker=ticker,
                provider=provider,
                operation=snapshot.operation,
                status=snapshot.status,
                requested_at=snapshot.requested_at,
                retrieved_at=snapshot.retrieved_at,
                source_url=source.url,
                data=normalized,
                warnings=meta.get("warnings"),
            )
        except OpenBBAdapterError as exc:
            retrieved_at = datetime.now(timezone.utc)
            snapshot.status = "failed"
            snapshot.retrieved_at = retrieved_at
            snapshot.error_code = exc.code
            snapshot.error_message = exc.message[:500]
            session.commit()
            raise HTTPException(
                status_code=502,
                detail=EvidenceSyncResponse(
                    snapshot_id=snapshot.id,
                    ticker=ticker,
                    provider=provider,
                    operation=snapshot.operation,
                    status="failed",
                    requested_at=snapshot.requested_at,
                    retrieved_at=retrieved_at,
                    source_url=source.url,
                    error_code=exc.code,
                    error_message=exc.message[:500],
                ).model_dump(mode="json"),
            ) from exc

    @router.get("/evidence/{ticker}", response_model=list[EvidenceHistoryItem])
    def list_evidence(ticker: str, session: Session = Depends(get_session)) -> list[EvidenceHistoryItem]:
        symbol = ticker.strip().upper()
        rows = session.scalars(
            select(EvidenceSnapshot)
            .where(EvidenceSnapshot.ticker == symbol)
            .order_by(EvidenceSnapshot.created_at.desc())
        ).all()
        return [
            EvidenceHistoryItem(
                snapshot_id=row.id,
                ticker=row.ticker,
                operation=row.operation,
                status=row.status,
                provider=provider,
                requested_at=row.requested_at,
                retrieved_at=row.retrieved_at,
                data=row.normalized_payload,
                error_code=row.error_code,
                error_message=row.error_message,
            )
            for row in rows
        ]

    @router.post("/analysis/evidence/{snapshot_id}", response_model=AnalysisDraftResponse)
    def analyze_evidence(
        snapshot_id: int,
        payload: AnalysisRequest,
        session: Session = Depends(get_session),
    ) -> AnalysisDraftResponse:
        snapshot = session.get(EvidenceSnapshot, snapshot_id)
        if snapshot is None:
            raise HTTPException(status_code=404, detail="Evidence snapshot not found.")
        if snapshot.status != "success" or not snapshot.normalized_payload:
            raise HTTPException(status_code=409, detail="Only a successful evidence snapshot can be analyzed.")
        if payload.analysis_type != "company_profile":
            raise HTTPException(
                status_code=400,
                detail="Step 5A supports company_profile / Master Research Report only.",
            )

        # Early reusable-report lookup MUST happen before previous-report context is
        # assembled; otherwise an identical second click changes previous_report_id
        # and incorrectly causes a new Gemini call.
        import_successful_drafts(session, company_id=snapshot.company_id)
        thread_context = active_thread_context(session, snapshot.company_id)
        thread_state_hash = canonical_hash(thread_context)
        if not payload.force_refresh:
            old_report = session.scalar(
                select(ResearchReport).where(
                    ResearchReport.company_id == snapshot.company_id,
                    ResearchReport.evidence_content_hash == canonical_hash(snapshot.normalized_payload),
                    ResearchReport.thread_state_hash == thread_state_hash,
                    ResearchReport.prompt_version == PROMPT_VERSION,
                    ResearchReport.provider == ("gemini" if os.getenv("AI_PROVIDER", "mock").strip().lower() in ("google", "gemini") else os.getenv("AI_PROVIDER", "mock").strip().lower()),
                    ResearchReport.model == ("mock-model" if os.getenv("AI_PROVIDER", "mock").strip().lower() == "mock" else os.getenv("AI_MODEL", "gemini-3.8-flash")),
                    ResearchReport.status == "success",
                ).order_by(ResearchReport.created_at.desc(), ResearchReport.id.desc())
            )
            if old_report:
                old_draft=session.get(AnalysisDraft,old_report.source_analysis_draft_id)
                if old_draft:
                    return _analysis_response(old_draft)

        previous_snapshot = session.scalar(
            select(EvidenceSnapshot)
            .where(
                EvidenceSnapshot.company_id == snapshot.company_id,
                EvidenceSnapshot.status == "success",
                EvidenceSnapshot.id < snapshot_id,
            )
            .order_by(EvidenceSnapshot.created_at.desc())
        )

        previous_report = session.scalar(
            select(AnalysisDraft)
            .join(EvidenceSnapshot, AnalysisDraft.snapshot_id == EvidenceSnapshot.id)
            .where(
                EvidenceSnapshot.company_id == snapshot.company_id,
                AnalysisDraft.analysis_type == "company_profile",
                AnalysisDraft.status == "success",
                AnalysisDraft.snapshot_id <= snapshot_id,
            )
            .order_by(AnalysisDraft.created_at.desc(), AnalysisDraft.id.desc())
        )

        previous_report_snapshot = session.get(EvidenceSnapshot, previous_report.snapshot_id) if previous_report else None
        reference_snapshot = previous_report_snapshot or previous_snapshot

        previous_archived = session.scalar(select(ResearchReport).where(
            ResearchReport.source_analysis_draft_id == previous_report.id
        )) if previous_report else None
        previous_result = previous_report.output_payload if previous_report else {}
        previous_key_takeaways = list(previous_result.get("key_takeaways") or []) if isinstance(previous_result, dict) else []

        review_context = build_review_context(
            current_snapshot_id=snapshot.id,
            current_evidence=snapshot.normalized_payload,
            previous_snapshot_id=reference_snapshot.id if reference_snapshot else None,
            previous_report_id=previous_archived.id if previous_archived else None,
            previous_evidence=reference_snapshot.normalized_payload if reference_snapshot else None,
            previous_key_takeaways=previous_key_takeaways,
        )

        # A force request asks for a NEW full narrative even when the evidence barely moved.
        actual_review_type = ("full_follow_up" if payload.force_refresh and previous_report
                              else review_context.review_type)
        review_context_dict = {
            "review_type": actual_review_type,
            "material_change": review_context.material_change,
            "current_snapshot_id": review_context.current_snapshot_id,
            "previous_snapshot_id": review_context.previous_snapshot_id,
            "previous_report_id": review_context.previous_report_id,
            "evidence_delta": review_context.evidence_delta,
        }

        input_hash_base = AIAnalyzer.input_hash(
            evidence=snapshot.normalized_payload,
            review_context=review_context_dict,
            previous_key_takeaways=previous_key_takeaways,
            prompt_version=PROMPT_VERSION,
        )

        # Any approved Thread updates change the prompt, and therefore the cache key.
        input_hash = hashlib.sha256((input_hash_base + thread_state_hash + getattr(payload, "report_language", "en")).encode()).hexdigest()

        provider_name = os.getenv("AI_PROVIDER", "mock").strip().lower()
        model_name = os.getenv("AI_MODEL", "not-configured")

        try:
            ai = build_ai_provider()
            analyzer = AIAnalyzer(ai)
            provider_name = ai.config.provider
            model_name = ai.config.model
        except AIProviderError as exc:
            draft = AnalysisDraft(
                snapshot_id=snapshot_id,
                analysis_type="company_profile",
                status="failed",
                provider=provider_name,
                model=model_name,
                prompt_version=PROMPT_VERSION,
                input_hash=input_hash,
                error_code=exc.code,
                error_message=exc.message[:500],
            )
            session.add(draft)
            session.commit()
            session.refresh(draft)
            return _analysis_response(draft)

        draft = AnalysisDraft(
            snapshot_id=snapshot_id,
            analysis_type="company_profile",
            status="pending",
            provider=provider_name,
            model=model_name,
            prompt_version=PROMPT_VERSION,
            input_hash=input_hash,
        )
        session.add(draft)
        session.commit()
        session.refresh(draft)

        try:
            result = analyzer.analyze_company(
                evidence=snapshot.normalized_payload,
                review_context=review_context_dict,
                previous_key_takeaways=previous_key_takeaways,
                thread_context=thread_context,
                report_language=getattr(payload, "report_language", "en"),
            )

            persisted_result = {
                "report_type": "master_research_report",
                "review_type": actual_review_type,
                "material_change": review_context.material_change,
                "previous_snapshot_id": review_context.previous_snapshot_id,
                "previous_report_id": review_context.previous_report_id,
                "previous_report_ref_type": "research_report",
                "evidence_delta": review_context.evidence_delta,
                "thread_state_hash": thread_state_hash,
                "language": getattr(payload, "report_language", "en"),
                **result,
            }

            draft.status = "success"
            draft.output_payload = persisted_result
            session.commit()
            session.refresh(draft)
            # Archive the successful report and the PROPOSED Thread Actions.
            # A recoverable archive error must not turn a successful AI response
            # into a false "AI failed" record; rerun migration to reconcile.
            try:
                import_successful_drafts(session, company_id=snapshot.company_id)
            except Exception:
                session.rollback()
                import logging
                logging.exception("Step6 archive failed; recover using python -m app.step6.migrate")
            return _analysis_response(draft)

        except AIProviderError as exc:
            draft.status = "failed"
            draft.error_code = exc.code
            draft.error_message = exc.message[:500]
            session.commit()
            session.refresh(draft)
            return _analysis_response(draft)
        except Exception as exc:
            draft.status = "failed"
            draft.error_code = "analysis_validation_error"
            draft.error_message = str(exc)[:500]
            session.commit()
            session.refresh(draft)
            return _analysis_response(draft)

    @router.get("/analysis/evidence/{snapshot_id}", response_model=list[AnalysisDraftResponse])
    def list_analysis_drafts(
        snapshot_id: int,
        session: Session = Depends(get_session),
    ) -> list[AnalysisDraftResponse]:
        rows = session.scalars(
            select(AnalysisDraft)
            .where(AnalysisDraft.snapshot_id == snapshot_id)
            .order_by(AnalysisDraft.created_at.desc())
        ).all()
        return [_analysis_response(row) for row in rows]

    return router


def _analysis_response(row: AnalysisDraft) -> AnalysisDraftResponse:
    return AnalysisDraftResponse(
        draft_id=row.id,
        snapshot_id=row.snapshot_id,
        analysis_type=row.analysis_type,
        status=row.status,
        provider=row.provider,
        model=row.model,
        prompt_version=row.prompt_version,
        input_hash=row.input_hash,
        result=row.output_payload,
        error_code=row.error_code,
        error_message=row.error_message,
    )
