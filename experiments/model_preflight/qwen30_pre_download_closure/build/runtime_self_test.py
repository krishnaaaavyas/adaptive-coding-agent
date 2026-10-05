"""Model-free Linux BUILD-TIME identities. Does not import torch/vLLM or initialize CUDA."""
import argparse,base64,hashlib,importlib.metadata as md,json,platform,subprocess,sys,unicodedata
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output');a=ap.parse_args();checks=[]
    def check(name,condition,observed):checks.append({'name':name,'status':'PASS' if condition else 'FAIL','observed':observed})
    check('CPython',(platform.python_implementation(),platform.python_version())==('CPython','3.11.9'),platform.python_version())
    check('Unicode',unicodedata.unidata_version=='14.0.0',unicodedata.unidata_version)
    check('Linux amd64',platform.system()=='Linux' and platform.machine()=='x86_64',[platform.system(),platform.machine()])
    apt=json.loads((P/'apt_dependency_lock.json').read_text(encoding='utf-8'));wrong=[]
    for p in apt['packages']:
        installed=subprocess.check_output(['dpkg-query','-W','-f=${Version}',p['name']],text=True)
        if installed!=p['version']:wrong.append({'name':p['name'],'expected':p['version'],'actual':installed})
    check('Exact apt/compiler package versions',not wrong,wrong)
    gcc=subprocess.check_output(['gcc-10','--version'],text=True);check('gcc-10 toolchain',gcc.startswith('gcc-10 '),gcc)
    lock=json.loads((P/'python_dependency_lock.json').read_text(encoding='utf-8'))
    expected={r['name']:r['version'] for r in lock['packages']};expected['flashinfer-jit-cache']='0.5.2+cu128'
    for name,version in expected.items():
        try: dist=md.distribution(name);actual=dist.version
        except md.PackageNotFoundError:check(name,False,None);continue
        check(name+' version',actual==version,actual)
        failures=[];count=0
        for file in dist.files or []:
            if file.hash:
                if file.hash.mode!='sha256':failures.append(str(file));continue
                p=dist.locate_file(file)
                got=base64.urlsafe_b64encode(bytes.fromhex(sha(p))).rstrip(b'=').decode('ascii')
                if got!=file.hash.value:failures.append(str(file))
                count+=1
        check(name+' installed RECORD hashes',not failures and count>0,{'checked':count,'mismatches':failures})
    nvcc=subprocess.check_output(['/usr/local/cuda/bin/nvcc','--version'],text=True)
    check('NVCC 12.8.90','V12.8.90' in nvcc,nvcc)
    root=Path(md.distribution('torch').locate_file('torch/version.py'))
    text=root.read_text(encoding='utf-8');check('Torch CUDA userspace declaration',"'12.8'" in text or '"12.8"' in text,sha(root))
    vllm=Path(md.distribution('vllm').locate_file('vllm'));extensions=list(vllm.rglob('*.so'))
    check('vLLM compiled CUDA extensions',any(p.name.startswith('_C.') for p in extensions) and any('_vllm_fa2_C' in p.name for p in extensions),[{'path':str(p),'sha256':sha(p)} for p in extensions])
    manifest=json.loads((P/'runner_manifest.json').read_text(encoding='utf-8'));bad=[]
    for r in manifest['files']:
        p=P/r['path']
        if not p.is_file() or sha(p)!=r['sha256']:bad.append(r['path'])
    check('Bound runner/observer/build/oracle hashes',not bad,{'root_sha256':manifest['content_root_sha256'],'mismatches':bad})
    source=json.loads((P/'source_archive_lock.json').read_text(encoding='utf-8'))
    check('Runtime source input identities',all(sha(P/'archives'/Path(r['path']).name)==r['sha256'] for r in source['sources']),[{'name':r['name'],'commit':r['commit'],'sha256':r['sha256']} for r in source['sources']])
    result={'stage':'BUILD-TIME','status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','checks':checks,'python_executable_sha256':sha(Path(sys.executable)),
        'GPU_dependent_checks':'PENDING TARGET RUNTIME','target_runtime_pass':False,'model_or_adapter_instantiated':False,'framework_imported':False,'GPU_used':False,'actual_kernel_dispatch':'PENDING','phase_observer_test':'PENDING'}
    text=json.dumps(result,indent=2)+'\n'
    if a.output:Path(a.output).open('x',encoding='utf-8').write(text)
    else:print(text)
    sys.exit(0 if result['status']=='PASS' else 2)
if __name__=='__main__':main()
