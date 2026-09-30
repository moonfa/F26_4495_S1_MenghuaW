from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index, UniqueConstraint
from ..database import Base
from ..models import Company, EvidenceSnapshot

def utcnow(): return datetime.now(timezone.utc)

class CompanyResearchState(Base):
    __tablename__='company_research_state'
    id=Column(Integer,primary_key=True)
    company_id=Column(Integer,ForeignKey(f'{Company.__tablename__}.id'),nullable=False,unique=True,index=True)
    status=Column(String(20),nullable=False,default='watching') # watching/following/archived
    report_language=Column(String(10),nullable=False,default='en')
    created_at=Column(DateTime(timezone=True),default=utcnow,nullable=False)
    updated_at=Column(DateTime(timezone=True),default=utcnow,nullable=False)

class ResearchUpdate(Base):
    __tablename__='research_updates'
    id=Column(Integer,primary_key=True)
    company_id=Column(Integer,ForeignKey(f'{Company.__tablename__}.id'),nullable=False,index=True)
    snapshot_id=Column(Integer,ForeignKey(f'{EvidenceSnapshot.__tablename__}.id'),nullable=False,index=True)
    previous_snapshot_id=Column(Integer,ForeignKey(f'{EvidenceSnapshot.__tablename__}.id'))
    update_level=Column(String(20),nullable=False) # evidence/research/material
    summary=Column(Text,nullable=False)
    evidence_delta=Column(JSON)
    driver_impacts=Column(JSON,default=list)
    valuation_implications=Column(JSON)
    full_review_recommended=Column(Boolean,default=False,nullable=False)
    language=Column(String(10),default='en',nullable=False)
    provider=Column(String(50))
    model=Column(String(120))
    created_at=Column(DateTime(timezone=True),default=utcnow,nullable=False)
    __table_args__=(UniqueConstraint('snapshot_id','language',name='uq_update_snapshot_language'),Index('ix_update_company_date','company_id','created_at','id'))
