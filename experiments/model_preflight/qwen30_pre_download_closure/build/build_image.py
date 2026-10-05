"""Future CPU-only Docker build driver. No GPU flag, no model context, no automatic retry."""
import argparse,hashlib,json,platform,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--target-arch',required=True);ap.add_argument('--build',action='store_true',required=True);a=ap.parse_args()
    if platform.system()!='Linux' or platform.machine()!='x86_64':raise SystemExit('PENDING_TARGET_LINUX_CPU_BUILD')
    import re
    if not re.fullmatch(r'(8\.0|8\.6|8\.9|9\.0|10\.0|10\.1|12\.0)',a.target_arch):raise SystemExit('Architecture must be supported by pinned CUDA12.8 sources and bound to future selected-device evidence')
    context=P/'build_context'
    if not (context/'inputs.sha256').exists():raise SystemExit('Collect and authenticate exact inputs first')
    binding=hashlib.sha256((context/'inputs.sha256').read_bytes()).hexdigest()
    out=P/'build/target_build';out.mkdir(exist_ok=False)
    args=['docker','build','--platform=linux/amd64','--network=none','--pull=false','--build-arg=TORCH_CUDA_ARCH_LIST='+a.target_arch,'--build-arg=BUILD_RECIPE_BINDING='+binding,'--iidfile='+str(out/'image.id'),'-f',str(context/'Dockerfile'),str(context)]
    with (out/'build.stdout').open('xb') as stdout,(out/'build.stderr').open('xb') as stderr:
        run=subprocess.run(args,stdout=stdout,stderr=stderr)
    (out/'attempt.json').write_text(json.dumps({'argv':args,'exit_code':run.returncode,'input_binding_sha256':binding,'target_arch':a.target_arch,'invocations':1,'retries':0,'GPU_used':False,'models_used':False},indent=2)+'\n',encoding='utf-8')
    if run.returncode:raise SystemExit('Target build failure retained; no rerun or version substitution')
    iid=(out/'image.id').read_text(encoding='utf-8').strip()
    inspected=json.loads(subprocess.check_output(['docker','image','inspect',iid]))
    (out/'image_inspect.json').write_text(json.dumps(inspected,indent=2)+'\n',encoding='utf-8')
    cid=subprocess.check_output(['docker','create','--network=none',iid],text=True).strip()
    try:subprocess.run(['docker','cp',cid+':/opt/build-evidence',str(out/'evidence')],check=True)
    finally:subprocess.run(['docker','rm',cid],check=True)
    subprocess.run(['docker','image','save','--output',str(out/'image.tar'),iid],check=True)
    h=hashlib.sha256()
    with (out/'image.tar').open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    (out/'digest_receipt.json').write_text(json.dumps({'image_config_digest':iid,'registry_manifest_digest':None,'OCI_archive_sha256':h.hexdigest(),'distinction':'Local image ID is config digest; archive SHA is delivery hash. Registry manifest digest only after separate authorized export/publish; none fabricated.'},indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
