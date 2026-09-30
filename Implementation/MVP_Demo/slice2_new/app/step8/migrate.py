"""Run from slice2_new: python -m app.step8.migrate. Stop Uvicorn first."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import text
from ..database import Base, engine
from . import models as m

def main():
    if engine.url.get_backend_name()!='sqlite': raise SystemExit('Step 8 MVP migration currently supports SQLite only.')
    db=engine.url.database
    if db and db!=':memory:' and Path(db).exists():
        original=Path(db);backup=original.with_name(original.name+'.before_step8_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')+'.bak')
        with sqlite3.connect(str(original)) as src,sqlite3.connect(str(backup)) as dst:src.backup(dst)
        print('SQLite backup:',backup.resolve())
    Base.metadata.create_all(engine,tables=[m.CompanyResearchState.__table__,m.ResearchUpdate.__table__])
    # Additive language metadata for existing report history. Safe/idempotent on SQLite.
    with engine.begin() as conn:
        cols={r[1] for r in conn.execute(text('PRAGMA table_info(research_reports)')).fetchall()}
        if 'language' not in cols: conn.execute(text("ALTER TABLE research_reports ADD COLUMN language VARCHAR(10) DEFAULT 'en'"))
    print('Step 8 migration complete. Existing evidence, reports, threads and notes were preserved.')
if __name__=='__main__':main()
