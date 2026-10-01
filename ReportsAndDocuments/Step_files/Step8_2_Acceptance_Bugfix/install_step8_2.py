#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import shutil, sys
p=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
paths=[p/"app/routes.py",p/"app/step8/routes.py",p/"app/static/index.html"]
if any(not x.exists() for x in paths): raise SystemExit("Run from slice2_new.")
bak=p/"local_backups"/("step8_2_"+datetime.now().strftime("%Y%m%d_%H%M%S"))
for x in paths:
    d=bak/x.relative_to(p); d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(x,d)

# Language-aware full-report cache
f=p/"app/routes.py"; s=f.read_text()
marker='                    ResearchReport.status == "success",'
lang='                    ResearchReport.language == getattr(payload, "report_language", "en"),'
if lang not in s:
    if marker not in s: raise SystemExit("Unexpected app/routes.py; backup="+str(bak))
    s=s.replace(marker,marker+"\n"+lang,1)
f.write_text(s)

# Narrower materiality and non-duplicative Timeline full-review marker
f=p/"app/step8/routes.py"; s=f.read_text()
a=s.index("def classify(delta):"); b=s.index("\nclass CompanyStateRequest",a)
repl="def classify(delta):\n    changes=delta.get('metric_changes') or []; news=delta.get('new_news_titles') or []\n    thesis=[x for x in changes if not x['metric'].startswith('market.')]\n    maxmove=max([abs(x.get('pct_change',0)) for x in thesis] or [0])\n    text=' '.join(str(x).lower() for x in news)\n    hard=('raises guidance','cuts guidance','withdraws guidance','earnings miss','earnings beat','acquisition','merger','bankruptcy','ceo resign','ceo steps down','chief executive resign','restatement','sec investigation','antitrust lawsuit')\n    material=maxmove>=0.20 or any(w in text for w in hard)\n    research=material or maxmove>=0.05 or len(news)>=2 or any(x['metric'].startswith(('financial_health.','analyst_consensus.')) for x in thesis)\n    return ('material' if material else 'research' if research else 'evidence')\n"
s=s[:a]+repl+s[b:]
s=s.replace("summary='No material thesis-level change detected in the tracked evidence.'","summary=('跟踪证据中未发现足以改变投资论点、核心驱动因素或主要风险的变化。' if language=='zh-CN' else 'No thesis-relevant change was detected in the tracked evidence.')")
s=s.replace("'summary':r.what_changed or ((r.key_takeaways or [''])[0])","'summary':'Saved Master Research Report'")
s=s.replace("events.sort(key=lambda x:(x['created_at'] or datetime.min.replace(tzinfo=timezone.utc),x['id']),reverse=True)","events.sort(key=lambda x:((x['created_at'].isoformat() if hasattr(x.get('created_at'),'isoformat') else str(x.get('created_at') or '')),x['id']),reverse=True)")
f.write_text(s)

# UI semantics: hide the old duplicate thread-history box and clarify Timeline full reviews.
f=p/"app/static/index.html"; h=f.read_text()
if "STEP 8.2 ACCEPTANCE UX" not in h:
    css="\n/* STEP 8.2 ACCEPTANCE UX */\n#timelineItems{display:none!important}\n"
    h=h.replace("</style>",css+"</style>",1)
    js="\n<script>/* STEP 8.2 ACCEPTANCE UX */\nconst step82OldTimeline=loadStep8Timeline;loadStep8Timeline=async function(){await step82OldTimeline();document.querySelectorAll(\'#researchTimeline .news-item\').forEach(row=>{const type=row.querySelector(\'.timeline-type\')?.textContent.toLowerCase()||\'\';if(type.includes(\'full review\')){const summary=row.querySelector(\'.meta\');if(summary)summary.textContent=\'Full report saved — open Historical Master Research Reports for details.\';}});};\n</script>\n"
    h=h.replace("</body>",js+"</body>",1)
f.write_text(h)
print("Backup:",bak)
print("Step 8.2 core bug-fix installed. No DB migration required.")
