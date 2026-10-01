#!/usr/bin/env python3
"""Install Step 6.1 over an existing Step 6 app. Never overwrites the DB."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, shutil, sqlite3, sys
PATCH=Path(__file__).resolve().parent
FILES=[
"app/static/index.html", "app/ai/schemas.py", "app/ai/prompts.py",
"app/step6/models.py", "app/step6/routes.py", "app/step6/service.py", "app/step6/migrate.py"]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project",type=Path,help="Path to Implementation/MVP_Demo/slice2_new")
    args=parser.parse_args();root=args.project.expanduser().resolve()
    for name in ["app/models.py","app/routes.py","app/step6/models.py","requirements.txt"]:
        if not (root/name).is_file():parser.error(f"Not an installed Step6 project: missing {name}")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup=Path.home()/"Step6_Project_Backups"/("step61_"+stamp)
    backup.mkdir(parents=True,exist_ok=False)
    for name in FILES:
        src=root/name;dst=backup/name
        if src.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    db=root/"slice1.db"
    if db.is_file():
        with sqlite3.connect(str(db)) as src, sqlite3.connect(str(backup/"slice1.db")) as dst:src.backup(dst)
    for name in FILES:
        dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PATCH/name,dest)
    print("Installed Step 6.1 code into:",root)
    print("Backed up existing files and local DB (if found) at:",backup)
    print("Next: cd",root,"&& python3 -m app.step6.migrate")
    return 0
if __name__=="__main__":sys.exit(main())
