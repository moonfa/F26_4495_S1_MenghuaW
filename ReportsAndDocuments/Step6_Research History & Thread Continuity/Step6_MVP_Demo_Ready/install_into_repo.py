#!/usr/bin/env python3
"""Safely copy the repo-specific Step6 files into Implementation/MVP_Demo/slice2_new.
Usage: python3 install_into_repo.py /path/to/slice2_new
"""
from __future__ import annotations
import argparse
import hashlib
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

PATCH_ROOT=Path(__file__).resolve().parent
EXPECTED_MAIN_GIT_BLOBS={
    "app/routes.py":"618793365368bbd918701944bbf6d8b3f59b661b",
    "app/main.py":"d875b71e1fce526cb372b4ec868aa9c7e4925b1a",
    "app/static/index.html":"b5bd2bd0df662c4771095550634636e35bfacb05",
}

def git_blob_hash(content:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\x00"+content).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project",type=Path,help="Implementation/MVP_Demo/slice2_new directory")
    parser.add_argument("--allow-modified",action="store_true",help="Proceed if working files differ from reviewed GitHub main; original files are backed up")
    args=parser.parse_args()
    project=args.project.expanduser().resolve()
    if not (project/"app"/"models.py").is_file() or not (project/"app"/"routes.py").is_file():
        parser.error(f"This isn't the expected slice2_new project: {project}")
    if not (project/"requirements.txt").is_file():
        parser.error("Expected requirements.txt in slice2_new; check the folder")
    mismatches=[]
    for relative,expected in EXPECTED_MAIN_GIT_BLOBS.items():
        path=project/relative
        if not path.is_file():parser.error(f"Required working file missing: {relative}")
        current=git_blob_hash(path.read_bytes())
        if current!=expected:mismatches.append((relative,current,expected))
    if mismatches and not args.allow_modified:
        print("\nSTOP: Your local files differ from the reviewed GitHub main version.")
        for rel,current,expected in mismatches:
            print(f"  {rel}\n    local: {current}\n    reviewed: {expected}")
        print("\nCommit/backup your latest local changes first. If you intentionally want to replace them,")
        print("re-run with --allow-modified (this installer saves copies of the original files).")
        return 2
    if (project/"app"/"step6").exists() and not args.allow_modified:
        print("Step 6 is already present. No files replaced. Use --allow-modified after reviewing differences.")
        return 2
    stamp=datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup=Path.home()/"Step6_Project_Backups"/(project.name+"_"+stamp)
    targets=list(EXPECTED_MAIN_GIT_BLOBS)
    if (project/"app"/"step6").exists():targets.append("app/step6")
    backup.mkdir(parents=True,exist_ok=False)
    for rel in targets:
        src=project/rel;dest=backup/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        if src.is_dir():shutil.copytree(src,dest)
        else:shutil.copy2(src,dest)
    # Separate *consistent* SQLite backup, even though migration makes its own.
    db=project/"slice1.db"
    if db.is_file():
        with sqlite3.connect(str(db)) as source, sqlite3.connect(str(backup/"slice1.db")) as target:
            source.backup(target)
    for rel in EXPECTED_MAIN_GIT_BLOBS:
        src=PATCH_ROOT/rel;dest=project/rel
        if not src.is_file():raise SystemExit(f"Missing package file: {src}")
        shutil.copy2(src,dest)
    src=PATCH_ROOT/"app"/"step6";dest=project/"app"/"step6"
    if dest.exists():shutil.rmtree(dest)
    shutil.copytree(src,dest,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
    print("\nStep 6 code installed into:",project)
    print("Backup of original files"+(" and SQLite DB" if db.is_file() else ""),":",backup)
    print("Next, from the project folder, run: python3 -m app.step6.migrate")
    print("Then start the SAME existing server: python3 -m uvicorn app.main:app --reload")
    print("Open http://127.0.0.1:8000/ and click Load Saved Research.")
    return 0

if __name__=="__main__":sys.exit(main())
