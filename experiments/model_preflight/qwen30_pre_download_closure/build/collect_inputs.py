"""Opt-in FUTURE runtime package collection; no model hosts, no execution, no retries."""
import argparse,hashlib,json,shutil,urllib.parse,urllib.request,zipfile
from email.parser import BytesParser
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
P=Path(__file__).resolve().parents[1]
def load(name):return json.loads((P/name).read_text(encoding='utf-8'))
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def fetch(a,path):
    if urllib.parse.urlparse(a['url']).hostname not in {'files.pythonhosted.org','download-r2.pytorch.org','snapshot.ubuntu.com','github.com'}:raise ValueError('Runtime-host allowlist only')
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        partial=path.with_name(path.name+'.partial')
        with urllib.request.urlopen(a['url'],timeout=120) as r,partial.open('xb') as f:
            shutil.copyfileobj(r,f,8388608)
        if sha(partial)!=a['sha256'] or ('bytes' in a and partial.stat().st_size!=a['bytes']):raise ValueError('Runtime package body authentication failed; retain partial, no retry')
        partial.rename(path)
    if sha(path)!=a['sha256']:raise ValueError('Existing runtime input hash mismatch')
    return {'path':path.relative_to(P).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'verified':True}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--collect-runtime-packages',action='store_true',required=True);a=ap.parse_args()
    stage=P/'build_context';stage.mkdir(exist_ok=False)
    lock=load('python_dependency_lock.json'); apt=load('apt_dependency_lock.json'); extra=load('extra_inputs_lock.json')
    versions={r['name']:r['version'] for r in lock['packages']};versions['flashinfer-jit-cache']='0.5.2+cu128';env=lock['target_marker_environment'];receipts=[]
    # Check actual wheel METADATA after full artifact SHA verification; no dependency solver at build time.
    wheels=[r['wheel'] for r in lock['packages'] if r['name'] not in {'vllm','transformers','peft'}]+[extra['flashinfer_jit_cache']]
    for w in wheels:
        dest=stage/'wheelhouse'/w['filename'];receipts.append(fetch(w,dest))
        with zipfile.ZipFile(dest) as z:
            name=next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'));m=BytesParser().parsebytes(z.read(name))
        key=canonicalize_name(m['Name'])
        if m['Version']!=versions[key]:raise ValueError('Wheel identity mismatch: '+key)
        for s in m.get_all('Requires-Dist',[]):
            r=Requirement(s)
            extras=next((p['extras'] for p in lock['packages'] if p['name']==key),[])
            if r.marker and not any(r.marker.evaluate(dict(env,extra=e)) for e in ['']+extras):continue
            dep=canonicalize_name(r.name)
            if r.url or dep not in versions or versions[dep] not in r.specifier:raise ValueError('Pinned closure does not cover authenticated metadata: '+s)
    for d in apt['packages']:
        rel=urllib.parse.urlparse(d['url']).path.split('/20261003T000000Z/',1)[1]
        receipts.append(fetch(d,stage/'ubuntu'/rel))
    for i in apt['indexes']:
        dest=stage/'ubuntu/dists'/i['suite']/i['component']/'binary-amd64/Packages.xz';dest.parent.mkdir(parents=True,exist_ok=True);src=P/i['path']
        if sha(src)!=i['sha256']:raise ValueError('Index mismatch')
        shutil.copyfile(src,dest)
    for suite in ['jammy','jammy-updates','jammy-security']:
        shutil.copyfile(P/f'sources/apt/{suite}-InRelease',stage/f'ubuntu/dists/{suite}/InRelease')
    # Allowlisted bundle only. Never include a workspace/repository/model directory in image context.
    for folder in ['build','runner','isolation','frozen','tests']:
        shutil.copytree(P/folder,stage/folder,ignore=shutil.ignore_patterns('__pycache__'))
    for name in ['Dockerfile','runtime_build_lock.json','python_dependency_lock.json','apt_dependency_lock.json','extra_inputs_lock.json','source_archive_lock.json','requirements-linux-cp311.lock','runner_manifest.json','target_attestation_validator.py','target_attestation_schema.json','target_capacity_policy.json','target_probe.py','target_probe.sh']:
        shutil.copyfile(P/name,stage/name)
    shutil.copytree(P/'sources/archives',stage/'archives')
    files=[p for p in stage.rglob('*') if p.is_file()]
    (stage/'inputs.sha256').write_text(''.join(sha(p)+'  '+p.relative_to(stage).as_posix()+'\n' for p in sorted(files)),encoding='utf-8')
    (P/'build/input_collection_receipt.json').open('x',encoding='utf-8').write(json.dumps({'verified_bodies':receipts,'model_weights':0,'source_archives_copied':7,'policy':'No retries; incomplete staging retained on failure'},indent=2)+'\n')
if __name__=='__main__':main()
