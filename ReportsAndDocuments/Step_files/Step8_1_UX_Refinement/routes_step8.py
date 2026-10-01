from datetime import datetime, timezone
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_session
from ..models import Company, EvidenceSnapshot
from ..ai.provider import build_ai_provider, AIProviderError
from ..step6.models import ResearchReport, PersonalResearchNote
from .models import CompanyResearchState, ResearchUpdate
from .schemas import TargetedResearchUpdate

router=APIRouter(prefix='/api/v1',tags=['Step 8 research lifecycle'])
def now(): return datetime.now(timezone.utc)
def company_for(session,ticker):
    c=session.scalar(select(Company).where(Company.ticker==ticker.strip().upper()))
    if not c: raise HTTPException(404,'Company not found. Refresh Evidence once to create it.')
    return c
def state_for(session,c):
    s=session.scalar(select(CompanyResearchState).where(CompanyResearchState.company_id==c.id))
    if not s:
        s=CompanyResearchState(company_id=c.id,status='watching',report_language='en');session.add(s);session.flush()
    return s
def scalar_metrics(e):
    out={}
    for sec in ('market','valuation','financial_health','analyst_consensus'):
        for k,v in (e.get(sec) or {}).items():
            if isinstance(v,(int,float)) and not isinstance(v,bool): out[f'{sec}.{k}']=float(v)
    return out
def evidence_delta(current,previous):
    if not previous:return {'status':'initial','metric_changes':[],'new_news_count':len(current.get('recent_news') or []),'new_news_titles':[x.get('title') for x in (current.get('recent_news') or [])[:8]]}
    a,b=scalar_metrics(previous),scalar_metrics(current);changes=[]
    for key,new in b.items():
        old=a.get(key)
        if old is None:continue
        pct=(new-old)/max(abs(old),1e-9)
        if abs(pct)>=.005:changes.append({'metric':key,'old':old,'new':new,'pct_change':round(pct,4)})
    old_titles={str(x.get('title','')).strip() for x in (previous.get('recent_news') or [])}
    new_news=[x for x in (current.get('recent_news') or []) if str(x.get('title','')).strip() not in old_titles]
    return {'status':'changed' if changes or new_news else 'unchanged','metric_changes':changes[:40],'new_news_count':len(new_news),'new_news_titles':[x.get('title') for x in new_news[:8]]}
def classify(delta):
    changes=delta.get('metric_changes') or [];news=delta.get('new_news_titles') or []
    maxmove=max([abs(x.get('pct_change',0)) for x in changes] or [0]);text=' '.join(str(x).lower() for x in news)
    hard=('earnings','guidance','acquisition','merger','bankruptcy','ceo resign','ceo steps down','chief executive resign','restatement','sec investigation','antitrust lawsuit')
    material=maxmove>=.20 or any(w in text for w in hard)
    research=material or maxmove>=.05 or len(news)>=2 or any(x['metric'].startswith(('financial_health.','analyst_consensus.')) for x in changes)
    return 'material' if material else 'research' if research else 'evidence'
def guardrail(level,result):
    if level!='material':return level,False
    impacts=result.get('driver_impacts') or [];vals=result.get('valuation_implications') or []
    low=bool(impacts) and all(x.get('magnitude')=='low' for x in impacts)
    unchanged=bool(vals) and all(x.get('direction') in ('unchanged','uncertain') and x.get('magnitude')=='low' for x in vals)
    return ('research',False) if low and unchanged else ('material',bool(result.get('full_review_recommended',True)))
class CompanyStateRequest(BaseModel):
    status:Literal['watching','following','archived']|None=None
    report_language:Literal['en','zh-CN']|None=None
@router.get('/research-companies')
def research_companies(session:Session=Depends(get_session)):
    result=[]
    for c in session.scalars(select(Company).order_by(Company.ticker)).all():
        s=state_for(session,c);result.append({'ticker':c.ticker,'name':c.name,'status':s.status,'report_language':s.report_language})
    session.commit();return result
@router.put('/companies/{ticker}/research-state')
def set_state(ticker:str,payload:CompanyStateRequest,session:Session=Depends(get_session)):
    c=company_for(session,ticker);s=state_for(session,c)
    if payload.status is not None:s.status=payload.status
    if payload.report_language is not None:s.report_language=payload.report_language
    s.updated_at=now();session.commit();return {'ticker':c.ticker,'status':s.status,'report_language':s.report_language}
@router.post('/companies/{ticker}/classify-update')
def classify_update(ticker:str,session:Session=Depends(get_session)):
    c=company_for(session,ticker);snaps=session.scalars(select(EvidenceSnapshot).where(EvidenceSnapshot.company_id==c.id,EvidenceSnapshot.status=='success').order_by(EvidenceSnapshot.created_at.desc(),EvidenceSnapshot.id.desc()).limit(2)).all()
    if not snaps:raise HTTPException(409,'No successful Evidence Snapshot.')
    cur=snaps[0];prev=snaps[1] if len(snaps)>1 else None;delta=evidence_delta(cur.normalized_payload or {},prev.normalized_payload or {});level=classify(delta)
    return {'ticker':c.ticker,'snapshot_id':cur.id,'previous_snapshot_id':prev.id if prev else None,'level':level,'full_review_recommended':level=='material','evidence_delta':delta}
class AnalyzeUpdateRequest(BaseModel):
    report_language:Literal['en','zh-CN']|None=None
@router.post('/companies/{ticker}/research-updates',status_code=201)
def analyze_update(ticker:str,payload:AnalyzeUpdateRequest,session:Session=Depends(get_session)):
    c=company_for(session,ticker);s=state_for(session,c);language=payload.report_language or s.report_language
    if payload.report_language:s.report_language=payload.report_language;s.updated_at=now()
    snaps=session.scalars(select(EvidenceSnapshot).where(EvidenceSnapshot.company_id==c.id,EvidenceSnapshot.status=='success').order_by(EvidenceSnapshot.created_at.desc(),EvidenceSnapshot.id.desc()).limit(2)).all()
    if not snaps:raise HTTPException(409,'No successful Evidence Snapshot.')
    cur=snaps[0];prev=snaps[1] if len(snaps)>1 else None
    existing=session.scalar(select(ResearchUpdate).where(ResearchUpdate.snapshot_id==cur.id,ResearchUpdate.language==language))
    if existing:session.commit();return update_view(existing)
    delta=evidence_delta(cur.normalized_payload or {},prev.normalized_payload or {});level=classify(delta)
    if level=='evidence':
        summary='跟踪证据中未发现足以改变投资论点、核心驱动因素或主要风险的变化。' if language=='zh-CN' else 'No thesis-relevant change was detected in the tracked evidence.'
        u=ResearchUpdate(company_id=c.id,snapshot_id=cur.id,previous_snapshot_id=prev.id if prev else None,update_level='evidence',summary=summary,evidence_delta=delta,full_review_recommended=False,language=language,provider='deterministic',model='rules-v1.1')
    else:
        try:ai=build_ai_provider()
        except AIProviderError as e:raise HTTPException(502,e.message)
        lang='Simplified Chinese' if language=='zh-CN' else 'English'
        prompt='Analyze ONLY the NEW evidence delta for a long-term fundamental research workflow. Output ALL natural-language fields in '+lang+'. Keep enum values in English. Do not write a full report or give buy/sell advice. Recommend a full review ONLY for a genuinely material change to earnings/guidance, business model, management, regulation, capital allocation, or the core thesis. A generic headline, price move, or low-magnitude clarification is NOT sufficient.\n\nANALYSIS_CONTEXT:\n'+__import__('json').dumps({'ticker':c.ticker,'classification':level,'evidence_delta':delta,'current_evidence':cur.normalized_payload or {}},ensure_ascii=False,default=str)
        if ai.config.provider=='mock':result={'summary':'Mock mode: targeted research review.','driver_impacts':[],'valuation_implications':[],'full_review_recommended':level=='material'}
        else:
            try:result=ai.analyze(system_prompt='You are a concise fundamental research update analyst.',user_prompt=prompt,response_schema=TargetedResearchUpdate)
            except AIProviderError as e:raise HTTPException(502,e.message)
        effective,recommend=guardrail(level,result)
        u=ResearchUpdate(company_id=c.id,snapshot_id=cur.id,previous_snapshot_id=prev.id if prev else None,update_level=effective,summary=result['summary'],evidence_delta=delta,driver_impacts=result.get('driver_impacts') or [],valuation_implications=result.get('valuation_implications') or [],full_review_recommended=recommend,language=language,provider=ai.config.provider,model=ai.config.model)
    session.add(u);session.commit();session.refresh(u);return update_view(u)
def update_view(u):
    return {'id':u.id,'snapshot_id':u.snapshot_id,'previous_snapshot_id':u.previous_snapshot_id,'update_level':u.update_level,'summary':u.summary,'evidence_delta':u.evidence_delta,'driver_impacts':u.driver_impacts,'valuation_implications':u.valuation_implications,'full_review_recommended':u.full_review_recommended,'language':u.language,'provider':u.provider,'model':u.model,'created_at':u.created_at}
@router.get('/companies/{ticker}/research-updates')
def updates(ticker:str,limit:int=50,session:Session=Depends(get_session)):
    c=company_for(session,ticker);rows=session.scalars(select(ResearchUpdate).where(ResearchUpdate.company_id==c.id).order_by(ResearchUpdate.created_at.desc(),ResearchUpdate.id.desc()).limit(max(1,min(limit,100)))).all();return [update_view(x) for x in rows]
@router.get('/companies/{ticker}/research-timeline')
def research_timeline(ticker:str,limit:int=100,session:Session=Depends(get_session)):
    c=company_for(session,ticker);events=[]
    for r in session.scalars(select(ResearchReport).where(ResearchReport.company_id==c.id,ResearchReport.status=='success')).all():events.append({'type':'full_review','id':r.id,'created_at':r.created_at,'title':'Full Research Review','summary':r.what_changed or ((r.key_takeaways or [''])[0]),'language':getattr(r,'language',None) or 'en','snapshot_id':r.snapshot_id})
    for u in session.scalars(select(ResearchUpdate).where(ResearchUpdate.company_id==c.id)).all():events.append({'type':'research_update' if u.update_level!='evidence' else 'evidence_update','id':u.id,'created_at':u.created_at,'title':u.update_level.replace('_',' ').title(),'summary':u.summary,'update_level':u.update_level,'snapshot_id':u.snapshot_id,'previous_snapshot_id':u.previous_snapshot_id,'evidence_delta':u.evidence_delta,'full_review_recommended':u.full_review_recommended,'language':u.language})
    for n in session.scalars(select(PersonalResearchNote).where(PersonalResearchNote.company_id==c.id)).all():events.append({'type':'personal_note','id':n.id,'created_at':n.created_at,'title':n.note_type.replace('_',' ').title(),'summary':n.body[:240]})
    events.sort(key=lambda x:(x['created_at'] or datetime.min.replace(tzinfo=timezone.utc),x['id']),reverse=True);return events[:max(1,min(limit,200))]
