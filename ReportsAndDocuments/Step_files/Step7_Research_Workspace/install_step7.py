from pathlib import Path
import shutil, sys, datetime

def main():
    target=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
    source=Path(__file__).resolve().parent
    dst=target/'app'/'static'/'index.html'
    if not dst.exists():
        raise SystemExit('Run this from Implementation/MVP_Demo/slice2_new (app/static/index.html not found).')
    stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup=target/'local_backups'/f'step7_{stamp}'
    backup.mkdir(parents=True,exist_ok=True)
    shutil.copy2(dst,backup/'index.html')
    shutil.copy2(source/'app'/'static'/'index.html',dst)
    print(f'Step 7 UI installed. Backup: {backup}')
    print('No database migration is required for Step 7.')

if __name__=='__main__': main()
