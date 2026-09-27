"""Run from slice2_new: python -m app.step6.migrate. Stop Uvicorn first."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()  # before importing database engine
from ..database import Base, engine, SessionLocal
from .. import models as legacy_models
from . import models as step6_models
from .service import import_successful_drafts

def main():
    db_url = engine.url
    if db_url.get_backend_name() == "sqlite":
        db = db_url.database
        if db and db != ":memory:" and Path(db).exists():
            original = Path(db)
            backup = original.with_name(original.name + ".before_step6_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + ".bak")
            with sqlite3.connect(str(original)) as src, sqlite3.connect(str(backup)) as dst:
                src.backup(dst)
            print("SQLite backup:", backup.resolve())
    else:
        raise SystemExit("Non-SQLite DB: take a manual database backup and use a versioned migration before continuing.")
    Base.metadata.create_all(engine, tables=[
        step6_models.ResearchReport.__table__,
        step6_models.ResearchThread.__table__,
        step6_models.ThreadVersion.__table__,
        step6_models.ThreadAction.__table__,
        step6_models.PersonalResearchNote.__table__,
    ])
    with SessionLocal() as session:
        imported=import_successful_drafts(session)
    print("Successfully imported Master Research Reports:", imported)
    print("Done. Existing AnalysisDraft/EvidenceSnapshot rows were not deleted or overwritten.")

if __name__ == "__main__": main()
