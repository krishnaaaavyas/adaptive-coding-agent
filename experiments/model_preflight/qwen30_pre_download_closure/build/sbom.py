"""SBOM records installed distributions, OS packages and actual runtime binary hashes."""
import argparse,hashlib,importlib.metadata as md,json,subprocess,sys
from pathlib import Path
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
    packages=sorted([{'name':d.metadata['Name'],'version':d.version,'installed_files':[str(f) for f in d.files or []]} for d in md.distributions()],key=lambda r:r['name'].lower())
    os_inventory=subprocess.check_output(['dpkg-query','-W','-f=${Package}\t${Version}\t${Architecture}\n'],text=True)
    files=set([Path(sys.executable).resolve()])
    for name in ['/usr/bin/gcc-10','/usr/bin/g++-10','/usr/bin/ld','/usr/local/cuda/bin/nvcc']:
        p=Path(name)
        if p.is_file():files.add(p.resolve())
    for root in [Path('/opt/python3.11.9'),Path('/usr/local/cuda'),Path('/usr/lib/x86_64-linux-gnu'),Path('/lib/x86_64-linux-gnu')]:
        for p in root.rglob('*'):
            if p.is_file() and ('.so' in p.name or p.name in ['nvcc','gcc-10','g++-10','libdevice.10.bc']):files.add(p.resolve())
    hashes=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]
    built=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(Path('/opt/built-wheels').glob('*.whl'))]
    result={'format':'qwen30-build-sbom-v1','python_distributions':packages,'OS_dpkg_inventory':os_inventory,'binaries':hashes,'generated_wheels':built,'complete_layer_content_identity':'Bound by final image config/layers/archive digests; this SBOM details runtime binaries','loaded_driver_library_hashes':'PENDING TARGET RUNTIME; no libcuda supplied or GPU initialized','model_weights':0}
    Path(a.output).open('x',encoding='utf-8').write(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
