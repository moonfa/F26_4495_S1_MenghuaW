from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_session
from ..models import Company
from .models import ResearchReport, ResearchThread, ThreadVersion, ThreadAction, PersonalResearchNote


router = APIRouter(prefix="/api/v1", tags=["Research history"])

def report_view(r):
    return {"id":r.id,"company_id":r.company_id,"snapshot_id":r.snapshot_id,
        "previous_report_id":r.previous_report_id,"created_at":r.created_at,
        "review_type":r.review_type,"material_change":r.material_change,
        "provider":r.provider,"model":r.model,"prompt_version":r.prompt_version,
        "report_markdown":r.report_markdown,"key_takeaways":r.key_takeaways,
        "what_changed":r.what_changed,"evidence_delta":r.evidence_delta}

def company_for(session,ticker):
    company=session.scalar(select(Company).where(Company.ticker==ticker.strip().upper()))
    if not company: raise HTTPException(404,"Company not found")
    return company

@router.get("/companies/{ticker}/reports")
def history(ticker:str, limit:int=20, session:Session=Depends(get_session)):
    company=company_for(session,ticker)
    limit=max(1,min(limit,100))
    rows=session.scalars(select(ResearchReport).where(
        ResearchReport.company_id==company.id, ResearchReport.status=="success"
    ).order_by(ResearchReport.created_at.desc(),ResearchReport.id.desc()).limit(limit)).all()
    return [{"id":r.id,"snapshot_id":r.snapshot_id,"previous_report_id":r.previous_report_id,
             "created_at":r.created_at,"review_type":r.review_type,
             "key_takeaways":r.key_takeaways,"what_changed":r.what_changed} for r in rows]

@router.get("/reports/{report_id}")
def report_detail(report_id:int,session:Session=Depends(get_session)):
    r=session.get(ResearchReport,report_id)
    if not r: raise HTTPException(404,"Report not found")
    actions=session.scalars(select(ThreadAction).where(ThreadAction.report_id==report_id)).all()
    return {**report_view(r),"thread_actions":[
        {"id":a.id,"thread_id":a.thread_id,"action":a.action,"title":a.title,
         "importance":a.importance,"change_summary":a.change_summary,
         "importance_change":a.importance_change,
         "review_status":a.review_status,"original_proposal":a.original_proposal} for a in actions]}

@router.get("/reports/by-draft/{draft_id}")
def detail_from_legacy_draft(draft_id:int, session:Session=Depends(get_session)):
    report=session.scalar(select(ResearchReport).where(
        ResearchReport.source_analysis_draft_id==draft_id
    ))
    if not report: raise HTTPException(404,"No archived Master Research Report for that AI draft")
    return report_detail(report.id,session)

@router.get("/companies/{ticker}/threads")
def threads(ticker:str,session:Session=Depends(get_session)):
    company=company_for(session,ticker)
    rows=session.scalars(select(ResearchThread).where(ResearchThread.company_id==company.id)
                         .order_by(ResearchThread.last_active_at.desc())).all()
    return [{"id":t.id,"title":t.title,"status":t.status,"importance":t.importance} for t in rows]

@router.get("/threads/{thread_id}/timeline")
def timeline(thread_id:int,session:Session=Depends(get_session)):
    thread=session.get(ResearchThread,thread_id)
    if not thread: raise HTTPException(404,"Thread not found")
    versions=session.scalars(select(ThreadVersion).where(ThreadVersion.thread_id==thread_id)
                             .order_by(ThreadVersion.created_at,ThreadVersion.id)).all()
    return {"thread_id":thread.id,"title":thread.title,"versions":[
        {"id":v.id,"report_id":v.report_id,"created_at":v.created_at,
         "state_summary":v.state_summary,"importance":v.importance} for v in versions]}

class ReviewRequest(BaseModel):
    decision:Literal["approve","reject"]
    reviewer_note:str|None=None
    target_thread_id:int|None=None
    edited_title:str|None=None
    edited_summary:str|None=None
    edited_importance:Literal["high","medium","low"]|None=None

@router.post("/thread-actions/{action_id}/review")
def review_action(action_id:int,payload:ReviewRequest,session:Session=Depends(get_session)):
    action=session.get(ThreadAction,action_id)
    if not action: raise HTTPException(404,"Action not found")
    if action.review_status!="proposed":
        raise HTTPException(409,"Action already reviewed; retry does not apply it twice.")
    report=session.get(ResearchReport,action.report_id)
    if not report: raise HTTPException(409,"Report missing")
    if payload.decision=="approve":
        if payload.edited_title:
            action.title=payload.edited_title.strip()[:240]
        if payload.edited_summary:
            action.change_summary=payload.edited_summary.strip()
        if payload.edited_importance:
            action.importance=payload.edited_importance
        if payload.target_thread_id is not None:
            target=session.get(ResearchThread,payload.target_thread_id)
            if not target or target.company_id != report.company_id:
                raise HTTPException(400,"Target thread does not belong to report company")
            action.thread_id=target.id
    if payload.decision=="approve" and action.action!="ephemeral":
        if action.action=="create":
            thread=ResearchThread(company_id=report.company_id,title=action.title,
                                  importance=action.importance,status="active")
            prior=session.scalars(select(ResearchThread).where(
                ResearchThread.company_id==report.company_id,
                ResearchThread.title.ilike(action.title),
                ResearchThread.status!="archived")).all()
            if prior: raise HTTPException(409,"A thread with this title already exists; review it as an update")
            session.add(thread);session.flush();action.thread_id=thread.id
        else:
            thread=session.get(ResearchThread,action.thread_id) if action.thread_id else None
            if not thread or thread.company_id!=report.company_id:
                raise HTTPException(409,"Existing thread must be linked before approving this action.")
            if action.action=="deprioritize": thread.status="watching"
            elif action.action=="close": thread.status="archived"
            elif action.action in ("continue","update"): thread.status="active"
            thread.importance=action.importance
            thread.last_active_at=datetime.now(timezone.utc)
        session.add(ThreadVersion(thread_id=thread.id,report_id=report.id,
                                  state_summary=action.change_summary or action.title,
                                  importance=action.importance,
                                  importance_change=action.importance_change))
    edited=bool(payload.edited_title or payload.edited_summary or payload.edited_importance)
    action.review_status=("edited" if edited else "approved") if payload.decision=="approve" else "rejected"
    action.reviewer_note=payload.reviewer_note
    action.reviewed_at=datetime.now(timezone.utc)
    session.commit()
    return {"action_id":action.id,"review_status":action.review_status,"thread_id":action.thread_id}

class NoteRequest(BaseModel):
    body:str=Field(min_length=1,max_length=20000)
    note_type:Literal["hypothesis","valuation_assumption","planned_action","review_outcome","general"]="general"
    report_id:int|None=None
    thread_id:int|None=None
    valuation_assumptions:dict|None=None

@router.get("/companies/{ticker}/notes")
def notes(ticker:str,session:Session=Depends(get_session)):
    company=company_for(session,ticker)
    rows=session.scalars(select(PersonalResearchNote).where(
        PersonalResearchNote.company_id==company.id).order_by(PersonalResearchNote.created_at.desc())).all()
    return [{"id":n.id,"body":n.body,"note_type":n.note_type,"report_id":n.report_id,
             "thread_id":n.thread_id,"created_at":n.created_at} for n in rows]

@router.post("/companies/{ticker}/notes",status_code=201)
def add_note(ticker:str,payload:NoteRequest,session:Session=Depends(get_session)):
    company=company_for(session,ticker)
    if payload.report_id:
        report=session.get(ResearchReport,payload.report_id)
        if not report or report.company_id!=company.id: raise HTTPException(400,"Report belongs to another company")
    if payload.thread_id:
        thread=session.get(ResearchThread,payload.thread_id)
        if not thread or thread.company_id!=company.id: raise HTTPException(400,"Thread belongs to another company")
    note=PersonalResearchNote(company_id=company.id,**payload.model_dump())
    session.add(note);session.commit();session.refresh(note)
    return {"id":note.id,"created_at":note.created_at}

# Explicit one-time import; do not expose a public backfill endpoint.
