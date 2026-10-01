#!/usr/bin/env python3
import json,sys,urllib.request
BASE=(sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8000").rstrip("/")
def get(p):
    with urllib.request.urlopen(BASE+p,timeout=20) as r:return json.load(r)
fail=[]
print("Step 8.2 read-only acceptance:",BASE)
print("health:",get("/api/v1/health"))
for t in ("WMT","MCD","MRVL"):
    print("\n==",t,"=="); saved={}
    endpoints={"evidence":f"/api/v1/evidence/{t}","reports":f"/api/v1/companies/{t}/reports?limit=100","threads":f"/api/v1/companies/{t}/threads","updates":f"/api/v1/companies/{t}/research-updates?limit=100","timeline":f"/api/v1/companies/{t}/research-timeline?limit=100"}
    for name,path in endpoints.items():
        try:
            d=get(path);saved[name]=d;print(f"{name:10} PASS count={len(d)}")
        except Exception as e:
            fail.append(f"{t}:{name}:{e}");print(f"{name:10} FAIL {e}")
    proposed=reviewed=0
    for r in saved.get("reports",[])[:20]:
        try:
            detail=get(f"/api/v1/reports/{r['id']}")
            for a in detail.get("thread_actions",[]):
                proposed+=a.get("review_status")=="proposed"
                reviewed+=a.get("review_status")!="proposed"
        except Exception as e:fail.append(f"{t}:report:{r['id']}:{e}")
    for th in saved.get("threads",[]):
        try:get(f"/api/v1/threads/{th['id']}/timeline")
        except Exception as e:fail.append(f"{t}:thread:{th['id']}:{e}")
    print("thread actions: proposed=",proposed,"reviewed=",reviewed)
print("\nRESULT:","PASS" if not fail else "FAIL")
if fail:print("\n".join(fail))
sys.exit(1 if fail else 0)
