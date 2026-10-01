#!/usr/bin/env python3
# Diagnostic only: reports repeated thread-action titles/statuses; does not modify DB.
from app.database import SessionLocal
from app.step6.models import ResearchReport,ThreadAction
from app.models import Company
from sqlalchemy import select
with SessionLocal() as s:
    for ticker in ("WMT","MCD","MRVL"):
        c=s.scalar(select(Company).where(Company.ticker==ticker))
        print("\n",ticker)
        if not c: continue
        rows=s.execute(select(ThreadAction,ResearchReport).join(ResearchReport,ThreadAction.report_id==ResearchReport.id).where(ResearchReport.company_id==c.id).order_by(ThreadAction.created_at)).all()
        for a,r in rows: print(f"report={r.id} action={a.id} status={a.review_status:8} type={a.action:12} title={a.title}")
