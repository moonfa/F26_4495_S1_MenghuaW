"""Offline tests against the actual Step6 router and original Step5A mock AI.
Run from the unpacked ZIP root: python -m pytest tests -q
"""
import importlib
import os
import shutil
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

SOURCE = Path(__file__).resolve().parents[1]

@pytest.fixture
def app_and_db(tmp_path, monkeypatch):
    target=tmp_path/'app';target.mkdir()
    (target/'__init__.py').write_text('')
    for f in ['routes.py','main.py']:
        shutil.copy2(SOURCE/'app'/f,target/f)
    shutil.copytree(SOURCE/'app'/'step6', target/'step6',ignore=shutil.ignore_patterns('__pycache__'))
    ai_dir=target/'ai';ai_dir.mkdir();(ai_dir/'__init__.py').write_text('')
    original=Path('/mnt/data/step6_work/source/mnt/data/step5a_vertical_slice/ai')
    if not original.exists():
        # The test bundle carries the 4 original AI modules as fixtures when run elsewhere.
        original=SOURCE/'tests'/'fixtures'/'ai'
    for f in ['analyzer.py','provider.py','report_context.py']:
        shutil.copy2(original/f, ai_dir/f)
    for f in ['prompts.py','schemas.py']:
        shutil.copy2(SOURCE/'app'/'ai'/f, ai_dir/f)
    (target/'database.py').write_text('''
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase,sessionmaker
import os
engine=create_engine(os.environ["DATABASE_URL"],connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
class Base(DeclarativeBase): pass
def get_session():
    with SessionLocal() as s: yield s
''')
    (target/'models.py').write_text('''
from datetime import datetime,timezone
from sqlalchemy import ForeignKey,String,Text,Integer,DateTime,JSON
from sqlalchemy.orm import mapped_column,Mapped
from .database import Base
now=lambda:datetime.now(timezone.utc)
class Company(Base):
 __tablename__="companies"
 id:Mapped[int]=mapped_column(primary_key=True)
 ticker:Mapped[str]=mapped_column(String(16),unique=True,index=True)
 name:Mapped[str]=mapped_column(String(200))
 company_type:Mapped[str|None]=mapped_column(String(80),nullable=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Source(Base):
 __tablename__="sources"
 id:Mapped[int]=mapped_column(primary_key=True)
 provider:Mapped[str]=mapped_column(String(50))
 source_type:Mapped[str]=mapped_column(String(50))
 name:Mapped[str]=mapped_column(String(200))
 url:Mapped[str|None]=mapped_column(Text,nullable=True)
class EvidenceSnapshot(Base):
 __tablename__="evidence_snapshots"
 id:Mapped[int]=mapped_column(primary_key=True)
 company_id:Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
 source_id:Mapped[int]=mapped_column(ForeignKey("sources.id"),index=True)
 ticker:Mapped[str]=mapped_column(String(16),index=True)
 operation:Mapped[str]=mapped_column(String(100))
 requested_at:Mapped[datetime]=mapped_column(DateTime(timezone=True))
 retrieved_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
 status:Mapped[str]=mapped_column(String(20),index=True)
 request_params:Mapped[dict|None]=mapped_column(JSON,nullable=True)
 raw_payload:Mapped[dict|None]=mapped_column(JSON,nullable=True)
 normalized_payload:Mapped[dict|None]=mapped_column(JSON,nullable=True)
 record_count:Mapped[int|None]=mapped_column(Integer,nullable=True)
 content_hash:Mapped[str|None]=mapped_column(String(64),nullable=True)
 error_code:Mapped[str|None]=mapped_column(String(80),nullable=True)
 error_message:Mapped[str|None]=mapped_column(Text,nullable=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class AnalysisDraft(Base):
 __tablename__="analysis_drafts"
 id:Mapped[int]=mapped_column(primary_key=True)
 snapshot_id:Mapped[int]=mapped_column(ForeignKey("evidence_snapshots.id"),index=True)
 analysis_type:Mapped[str]=mapped_column(String(40))
 status:Mapped[str]=mapped_column(String(20),index=True)
 provider:Mapped[str]=mapped_column(String(50))
 model:Mapped[str]=mapped_column(String(100))
 prompt_version:Mapped[str]=mapped_column(String(50))
 input_hash:Mapped[str]=mapped_column(String(64),index=True)
 output_payload:Mapped[dict|None]=mapped_column(JSON,nullable=True)
 error_code:Mapped[str|None]=mapped_column(String(80),nullable=True)
 error_message:Mapped[str|None]=mapped_column(Text,nullable=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
''')
    (target/'schemas.py').write_text('''
from datetime import datetime
from typing import Any
from pydantic import BaseModel,Field
class SyncRequest(BaseModel):
 ticker:str
class EvidenceSyncResponse(BaseModel):
 snapshot_id:int
 ticker:str
 provider:str
 operation:str|None=None
 status:str
 requested_at:datetime
 retrieved_at:datetime|None=None
 source_url:str|None=None
 data:dict[str,Any]|None=None
 warnings:list|None=None
 error_code:str|None=None
 error_message:str|None=None
class EvidenceHistoryItem(BaseModel):
 snapshot_id:int
 ticker:str
 operation:str
 status:str
 provider:str
 requested_at:datetime
 retrieved_at:datetime|None=None
 data:dict[str,Any]|None=None
 error_code:str|None=None
 error_message:str|None=None
class AnalysisRequest(BaseModel):
 analysis_type:str="company_profile"
 force_refresh:bool=False
class AnalysisDraftResponse(BaseModel):
 draft_id:int
 snapshot_id:int
 analysis_type:str
 status:str
 provider:str
 model:str
 prompt_version:str
 input_hash:str
 result:dict[str,Any]|None=None
 error_code:str|None=None
 error_message:str|None=None
''')
    (target/'adapters').mkdir();(target/'adapters'/'__init__.py').write_text('')
    (target/'adapters'/'openbb_adapter.py').write_text('''
PRICE=100.0
class OpenBBAdapterError(Exception):
 def __init__(self,code,message):self.code=code;self.message=message
class OpenBBAdapter:
 SNAPSHOT_VERSION="research-snapshot-v2.1"
 def __init__(self,provider):self.provider=provider
 def yahoo_url(self,ticker):return f"https://finance.yahoo.com/quote/{ticker}/"
 def get_equity_research_snapshot(self,ticker):
  evidence={"schema_version":self.SNAPSHOT_VERSION,
   "company":{"symbol":ticker,"name":"Walmart Inc.","currency":"USD"},
   "market":{"current_price":PRICE,"currency":"USD"},
   "valuation":{"forward_pe":20.0},"financial_health":{"profit_margin":0.03},
   "analyst_consensus":{},"recent_news":[],"data_quality":{}}
  return evidence,{"raw":{"test":PRICE},"raw_sections":{"profile":1},"warnings":[]}
''')
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.setenv('DATABASE_URL',f'sqlite:///{tmp_path}/test.db')
    monkeypatch.setenv('AI_PROVIDER','mock')
    # Import once for this fixture; test isolated per pytest process via distinct modules.
    for name in list(sys.modules):
        if name=='app' or name.startswith('app.'):
            del sys.modules[name]
    from app.routes import build_router
    from app.step6.routes import router as history_router
    from app.step6.migrate import main as migrate
    migrate()
    app=FastAPI();app.include_router(build_router('yfinance'));app.include_router(history_router)
    return TestClient(app),importlib.import_module('app'), tmp_path

def test_full_history_continuity_and_cache(app_and_db,monkeypatch):
    client,app,tmp=app_and_db
    from app.models import Company,AnalysisDraft
    from app.database import SessionLocal
    from app.step6.models import ResearchReport,ResearchThread,ThreadAction,ThreadVersion
    from app.ai.provider import MockAIProvider,AIProviderError
    from app import routes as old_routes
    from app.adapters import openbb_adapter as adapter
    spy={'calls':0,'contexts':[],'fail':False}
    class CountedMock(MockAIProvider):
        def analyze(self,**kw):
            spy['calls']+=1
            spy['contexts'].append(kw['user_prompt'])
            if spy['fail']:raise AIProviderError('quota','Mock quota exceeded')
            return super().analyze(**kw)
    monkeypatch.setattr(old_routes,'build_ai_provider',lambda:CountedMock())
    first=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json();assert first['status']=='success'
    s1=first['snapshot_id']
    a1=client.post(f'/api/v1/analysis/evidence/{s1}',json={'analysis_type':'company_profile'}).json()
    assert a1['status']=='success' and a1['result']['review_type']=='initial' and spy['calls']==1
    again=client.post(f'/api/v1/analysis/evidence/{s1}',json={'analysis_type':'company_profile'}).json()
    assert again['draft_id']==a1['draft_id'] and spy['calls']==1
    second=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json();s2=second['snapshot_id']
    duplicate=client.post(f'/api/v1/analysis/evidence/{s2}',json={'analysis_type':'company_profile'}).json()
    assert duplicate['draft_id']==a1['draft_id'] and spy['calls']==1
    rows=client.get('/api/v1/companies/WMT/reports').json();assert len(rows)==1
    # Force full creates a SECOND archived report despite unchanged evidence.
    forced=client.post(f'/api/v1/analysis/evidence/{s2}',json={'analysis_type':'company_profile','force_refresh':True}).json()
    assert forced['status']=='success' and forced['result']['review_type']=='full_follow_up' and spy['calls']==2
    rows=client.get('/api/v1/companies/WMT/reports').json()
    assert len(rows)==2 and rows[0]['previous_report_id']==rows[1]['id']
    # Add a proposed AI action, then approve it using actual Step 6 review API.
    with SessionLocal() as db:
        db.add(ThreadAction(report_id=rows[1]['id'],action='create',title='E-commerce profitability',
                            importance='high',importance_change='new',change_summary='Track margins'))
        db.commit();action=db.scalars(select(ThreadAction).order_by(ThreadAction.id.desc())).first()
        action_id=action.id
    approved=client.post(f'/api/v1/thread-actions/{action_id}/review',json={'decision':'approve'});assert approved.status_code==200
    assert client.post(f'/api/v1/thread-actions/{action_id}/review',json={'decision':'approve'}).status_code==409
    tid=approved.json()['thread_id']
    timeline=client.get(f'/api/v1/threads/{tid}/timeline').json();assert len(timeline['versions'])==1
    # New identical evidence AFTER thread approval now requires a fresh AI review (thread context changed).
    s3=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json()['snapshot_id']
    third=client.post(f'/api/v1/analysis/evidence/{s3}',json={'analysis_type':'company_profile'}).json()
    assert third['status']=='success' and spy['calls']==3
    assert 'E-commerce profitability' in spy['contexts'][-1]
    rows=client.get('/api/v1/companies/WMT/reports').json()
    assert len(rows)==3 and rows[0]['previous_report_id']==rows[1]['id']
    # Changed evidence, followed by a failed force request: prior reports stay intact.
    adapter.PRICE=105.0
    s4=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json()['snapshot_id']
    a4=client.post(f'/api/v1/analysis/evidence/{s4}',json={'analysis_type':'company_profile'}).json()
    assert a4['status']=='success' and spy['calls']==4
    assert a4['result']['previous_report_id'] is not None
    spy['fail']=True
    error=client.post(f'/api/v1/analysis/evidence/{s4}',json={'analysis_type':'company_profile','force_refresh':True}).json()
    assert error['status']=='failed'
    assert len(client.get('/api/v1/companies/WMT/reports').json())==4
    with SessionLocal() as db:
        assert db.query(ResearchThread).count()==1 and db.query(ThreadVersion).count()==1
        assert db.query(ResearchReport).count()==4
        assert db.query(AnalysisDraft).filter_by(status='failed').count()==1
    # Personal note is saved independently.
    note=client.post('/api/v1/companies/WMT/notes',json={'body':'Compare actual results next quarter','note_type':'hypothesis','thread_id':tid})
    assert note.status_code==201 and len(client.get('/api/v1/companies/WMT/notes').json())==1
    print('PASS: initial, same-snapshot cache, cross-snapshot cache, force full, lineage, approval, one version, active thread prompt, failure preservation, personal journal')

def test_existing_legacy_drafts_backfill_is_idempotent(app_and_db):
    client,app,tmp=app_and_db
    from datetime import datetime,timedelta,timezone
    from app.database import SessionLocal
    from app.models import Company,Source,EvidenceSnapshot,AnalysisDraft
    from app.step6.models import ResearchReport,ThreadAction
    from app.step6.service import import_successful_drafts
    now=datetime.now(timezone.utc)
    with SessionLocal() as db:
        c=Company(ticker='MRVL',name='Marvell');src=Source(provider='openbb',source_type='yfinance',name='test')
        db.add_all([c,src]);db.flush()
        previous=None
        for n in range(3):
            snap=EvidenceSnapshot(company_id=c.id,source_id=src.id,ticker='MRVL',operation='equity.profile',
                requested_at=now+timedelta(minutes=n),status='success',
                normalized_payload={'company':{'symbol':'MRVL'},'market':{'current_price':100+n}},
                created_at=now+timedelta(minutes=n))
            db.add(snap);db.flush()
            report={'report_markdown':f'# Review {n}','key_takeaways':[f'Point {n}'],
                    'thread_actions':[{'action':'create','title':f'Thread {n}','importance':'high','importance_change':'new','change_summary':'Research this'}],
                    'previous_report_id':previous}
            draft=AnalysisDraft(snapshot_id=snap.id,analysis_type='company_profile',status='success',
               provider='mock',model='mock-model',prompt_version='legacy-v1',input_hash=str(n),
               output_payload=report,created_at=now+timedelta(minutes=n))
            db.add(draft);db.flush();previous=draft.id
        # An old structured (non-Markdown) analysis must be ignored, not overwritten.
        db.add(AnalysisDraft(snapshot_id=snap.id,analysis_type='company_profile',status='success',
            provider='mock',model='mock-model',prompt_version='old',input_hash='old',
            output_payload={'summary':'old-style'},created_at=now+timedelta(minutes=4)))
        db.commit()
        assert import_successful_drafts(db,c.id)==3
        assert import_successful_drafts(db,c.id)==0
        reports=db.scalars(select(ResearchReport).where(ResearchReport.company_id==c.id)
            .order_by(ResearchReport.id)).all()
        assert len(reports)==3
        assert [r.previous_report_id for r in reports]==[None,reports[0].id,reports[1].id]
        assert db.query(ThreadAction).filter(ThreadAction.report_id.in_([r.id for r in reports])).count()==3
        assert db.query(AnalysisDraft).filter_by(status='success').count()==4
    print('PASS: legacy backfill, exact formal lineage, no old-row edits, idempotent re-run')

def test_same_snapshot_after_human_approval_is_followup_then_cached(app_and_db,monkeypatch):
    client,app,tmp=app_and_db
    from app.database import SessionLocal
    from app.step6.models import ThreadAction
    from app.ai.provider import MockAIProvider
    from app import routes as old_routes
    calls=[]
    class CountingProvider(MockAIProvider):
        def analyze(self,**kwargs):
            calls.append(kwargs['user_prompt'])
            return super().analyze(**kwargs)
    monkeypatch.setattr(old_routes,'build_ai_provider',lambda:CountingProvider())
    sn=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json()['snapshot_id']
    draft=client.post(f'/api/v1/analysis/evidence/{sn}',json={'analysis_type':'company_profile'}).json()
    detail=client.get(f'/api/v1/reports/by-draft/{draft["draft_id"]}').json()
    with SessionLocal() as db:
        action=ThreadAction(report_id=detail['id'],action='create',title='Membership Economics',
                            importance='high',importance_change='new',change_summary='Compare membership growth')
        db.add(action);db.commit();aid=action.id
    approved=client.post(f'/api/v1/thread-actions/{aid}/review',json={'decision':'approve'})
    assert approved.status_code==200
    review=client.post(f'/api/v1/analysis/evidence/{sn}',json={'analysis_type':'company_profile'}).json()
    assert review['status']=='success' and review['result']['review_type']=='low_change'
    assert review['result']['previous_report_id']==detail['id']
    assert len(calls)==2 and 'Membership Economics' in calls[-1]
    rerun=client.post(f'/api/v1/analysis/evidence/{sn}',json={'analysis_type':'company_profile'}).json()
    assert rerun['draft_id']==review['draft_id'] and len(calls)==2
    same=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json()['snapshot_id']
    reuse=client.post(f'/api/v1/analysis/evidence/{same}',json={'analysis_type':'company_profile'}).json()
    assert reuse['draft_id']==review['draft_id'] and len(calls)==2
    history=client.get('/api/v1/companies/WMT/reports').json()
    assert len(history)==2 and history[0]['previous_report_id']==history[1]['id']
    print('PASS: human approval updates prompt; same-Snapshot follow-up links previous formal report and is then cached on repeat/new identical Snapshot')

def test_two_distinct_reports_one_thread_two_versions_and_edited_approval(app_and_db):
    client, _, _ = app_and_db
    from app.database import SessionLocal
    from app.step6.models import ThreadAction, ThreadVersion, ResearchThread
    s1=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json()['snapshot_id']
    d1=client.post(f'/api/v1/analysis/evidence/{s1}',json={'analysis_type':'company_profile'}).json()
    r1=client.get(f'/api/v1/reports/by-draft/{d1["draft_id"]}').json()['id']
    with SessionLocal() as db:
        a=ThreadAction(report_id=r1,action='create',title='Retail Media',importance='high',importance_change='new',change_summary='Track margins')
        db.add(a);db.commit();aid=a.id
    first=client.post(f'/api/v1/thread-actions/{aid}/review',json={'decision':'approve'})
    assert first.status_code==200
    tid=first.json()['thread_id']
    s2=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json()['snapshot_id']
    d2=client.post(f'/api/v1/analysis/evidence/{s2}',json={'analysis_type':'company_profile'}).json()
    r2=client.get(f'/api/v1/reports/by-draft/{d2["draft_id"]}').json()['id']
    assert r1 != r2
    with SessionLocal() as db:
        a=ThreadAction(report_id=r2,thread_id=tid,action='update',title='Retail Media',importance='medium',importance_change='decreased',change_summary='Old summary',original_proposal={'title':'Retail Media','change_summary':'Old summary'})
        db.add(a);db.commit();aid2=a.id
    edited=client.post(f'/api/v1/thread-actions/{aid2}/review',json={'decision':'approve','edited_title':'Retail Media & Ads','edited_summary':'Revised after evidence','edited_importance':'high','reviewer_note':'My decision'})
    assert edited.status_code==200 and edited.json()['thread_id']==tid
    assert client.post(f'/api/v1/thread-actions/{aid2}/review',json={'decision':'approve'}).status_code==409
    timeline=client.get(f'/api/v1/threads/{tid}/timeline').json()
    assert len(timeline['versions'])==2
    assert {v['report_id'] for v in timeline['versions']}=={r1,r2}
    with SessionLocal() as db:
        assert db.query(ResearchThread).count()==1
        assert db.query(ThreadVersion).count()==2
        assert db.get(ThreadAction,aid2).original_proposal['change_summary']=='Old summary'
        assert db.get(ResearchThread,tid).title=='Retail Media & Ads'
    print('PASS: two real archived reports -> one thread -> two versions; edited human approval; immutable AI proposal; duplicate approval blocked')

def test_valuation_implication_persists_without_modifying_user_assumptions(app_and_db):
    client,_,_=app_and_db
    from app.database import SessionLocal
    from app.step6.models import ResearchReport
    from app.ai.schemas import MasterResearchReport
    payload={'impacts':[{'target':'base_metric','direction':'up','magnitude':'medium','confidence':'high','reason':'Guidance raises EPS sensitivity'}, {'target':'multiple','direction':'unchanged','magnitude':'low','confidence':'medium','reason':'No evidence for rerating'}],'action':'review_recommended'}
    parsed=MasterResearchReport(report_markdown='# Test',valuation_implications=payload)
    assert parsed.valuation_implications.impacts[0].target=='base_metric'
    sn=client.post('/api/v1/evidence/sync',json={'ticker':'WMT'}).json()['snapshot_id']
    draft=client.post(f'/api/v1/analysis/evidence/{sn}',json={'analysis_type':'company_profile'}).json()
    with SessionLocal() as db:
        report=db.query(ResearchReport).one()
        report.valuation_implications=payload
        db.commit();rid=report.id
    detail=client.get(f'/api/v1/reports/{rid}').json()
    assert detail['valuation_implications']==payload
    history=client.get('/api/v1/companies/WMT/reports').json()
    assert history[0]['valuation_implications']==payload
    assert history[0]['summary']
    print('PASS: valuation implication schema, archived JSON, report detail and history summary')
