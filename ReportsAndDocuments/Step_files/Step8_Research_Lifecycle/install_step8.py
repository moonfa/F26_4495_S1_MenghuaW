#!/usr/bin/env python3
from pathlib import Path
import argparse, shutil, sqlite3
from datetime import datetime

def main():
    ap=argparse.ArgumentParser(description='Install Step 8 Research Lifecycle patch')
    ap.add_argument('project',nargs='?',default='.')
    args=ap.parse_args();root=Path(args.project).resolve();pkg=Path(__file__).resolve().parent
    required=[root/'app/main.py',root/'app/routes.py',root/'app/static/index.html',root/'app/step6/models.py']
    missing=[str(x) for x in required if not x.exists()]
    if missing: raise SystemExit('This patch requires the installed Step 6/7 baseline. Missing: '+', '.join(missing))
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S');backup=root.parent/f'{root.name}_before_step8_{stamp}';backup.mkdir(parents=True)
    for rel in ['app/main.py','app/routes.py','app/static/index.html','app/step6/models.py','app/step6/routes.py','app/step6/service.py','app/ai/analyzer.py','app/ai/prompts.py','app/ai/schemas.py','app/schemas.py']:
        src=root/rel
        if src.exists():
            dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    db=root/'slice1.db'
    if db.exists():
        b=backup/'slice1.db';
        with sqlite3.connect(str(db)) as src,sqlite3.connect(str(b)) as dst:src.backup(dst)
    # Full reviewed files
    for rel in ['app/main.py','app/routes.py','app/static/index.html','app/step6/models.py','app/step6/routes.py','app/step6/service.py','app/ai/analyzer.py','app/ai/prompts.py']:
        src=pkg/rel;dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    # New Step 8 module
    dst=root/'app/step8';
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(pkg/'app/step8',dst)
    # AI structured schema extension from Step 6.1
    shutil.copy2(pkg/'app/ai/schemas.py',root/'app/ai/schemas.py')
    # Add report_language to existing HTTP request schema without replacing unrelated coursework schemas.
    schema=root/'app/schemas.py';text=schema.read_text()
    if 'class AnalysisRequest' not in text: raise SystemExit('Could not find AnalysisRequest in app/schemas.py; backup is at '+str(backup))
    if 'report_language:' not in text:
        marker='class AnalysisRequest(BaseModel):\n    analysis_type: str\n    force_refresh: bool = False'
        if marker not in text: raise SystemExit('AnalysisRequest shape differs from reviewed baseline; stopped safely. Backup: '+str(backup))
        text=text.replace(marker,marker+'\n    report_language: Literal["en", "zh-CN"] = "en"')
        schema.write_text(text)
    print('Step 8 files installed.')
    print('Backup:',backup)
    print('NEXT: python3 -m app.step8.migrate')
    print('THEN: python3 -m uvicorn app.main:app --reload')
if __name__=='__main__':main()
