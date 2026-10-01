from pathlib import Path
from datetime import datetime
import shutil,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve();app=p/'app'
files=[app/'static/index.html',app/'step8/routes.py',app/'routes.py']
if any(not x.exists() for x in files):raise SystemExit('Run from the current slice2_new Step 8 project.')
stamp=datetime.now().strftime('%Y%m%d_%H%M%S');bak=p/'local_backups'/('step8_1_'+stamp)
for f in files:
 d=bak/f.relative_to(p);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
here=Path(__file__).resolve().parent;shutil.copy2(here/'routes_step8.py',app/'step8/routes.py')
r=app/'routes.py';s=r.read_text()
needle='ResearchReport.status == "success",\n                ).order_by(ResearchReport.created_at.desc(), ResearchReport.id.desc())'
repl='ResearchReport.status == "success",\n                    ResearchReport.language == getattr(payload, "report_language", "en"),\n                ).order_by(ResearchReport.created_at.desc(), ResearchReport.id.desc())'
if needle in s:s=s.replace(needle,repl,1)
elif 'ResearchReport.language == getattr(payload, "report_language", "en")' not in s:raise SystemExit('app/routes.py differs from expected GitHub Step 8 baseline; restore from '+str(bak))
r.write_text(s)
i=app/'static/index.html';h=i.read_text()
if 'STEP 8.1 UX REFINEMENT' not in h:
 h=h.replace('</style>','/* STEP 8.1 UX REFINEMENT */\n'+(here/'ux.css').read_text()+'\n</style>',1)
 h=h.replace('</body>','<script>/* STEP 8.1 UX REFINEMENT */\n'+(here/'ux.js').read_text()+'\n</script>\n</body>',1)
i.write_text(h)
print('Backup:',bak);print('Step 8.1 installed. No DB migration required. Restart Uvicorn and hard-refresh.')
