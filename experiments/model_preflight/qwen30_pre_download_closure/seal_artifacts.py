"""Seal new preparation files only; no earlier artifacts modified."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def main():
    files=sorted([{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in P.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'],key=lambda r:r['path'].encode('utf-8'))
    root=hashlib.sha256(json.dumps([{'path':r['path'],'sha256':r['sha256']} for r in files],sort_keys=True,ensure_ascii=True,separators=(',',':')).encode('utf-8')).hexdigest()
    d={'scope':'qwen30_pre_download_closure only','excluded_self':'artifact_manifest.json','files':files,'content_root_sha256':root,'validation':'validate_closure.py is read-only by default; do not run --write after sealing without a deliberate new seal','no_checkpoint_weights':True}
    p=P/'artifact_manifest.json';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(files),'content_root_sha256':root,'artifact_manifest_sha256':sha(p)}))
if __name__=='__main__':main()
