"""Read-only integrity/metadata/receipt verification; never imports frameworks or probes hardware."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
import jsonschema
P=Path(__file__).resolve().parent;WORK=P.parents[2];G=P.parent/'qwen30_infrastructure_governance'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def canonical(d):return json.dumps(d,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode('utf-8')
def main():
    checks=[]
    def check(name,ok,detail=None):checks.append({'check':name,'result':'PASS' if ok else 'FAIL','detail':detail})
    baseline=load(P/'baseline_integrity.json');bad=[]
    for r in baseline['preserved_files']:
        p=WORK/r['path']
        if not p.is_file() or p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:bad.append(r['path'])
    check('Prior governance/roster/Draft2/Draft3/current-r2 explicit integrity allowlist',not bad,{'files':len(baseline['preserved_files']),'mismatches':bad,'method':'Hash-only explicit previous paths, no protected candidate/task/scorer/outcome enumeration or content inspection'})
    for p in (P/'frozen').glob('*.json'):check('Frozen exact copy '+p.name,sha(p)==sha(G/p.name))
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WORK,text=True).strip();status=subprocess.check_output(['git','status','--short'],cwd=WORK,text=True).strip();tracked=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=WORK,text=True).strip()
    check('HEAD unchanged',head==baseline['head'],head);check('No tracked/product edits or commit',not tracked,{'tracked_diff':tracked,'status':status})
    package=load(P/'python_dependency_lock.json');versions={r['name']:r['version'] for r in package['packages']};env=package['target_marker_environment'];edges=0;errors=[]
    for p in package['packages']:
        for text in p['active_requires_dist']:
            r=Requirement(text);name=canonicalize_name(r.name)
            if r.marker and not any(r.marker.evaluate(dict(env,extra=x)) for x in ['']+p['extras']):continue
            edges+=1
            if name not in versions or versions[name] not in r.specifier:errors.append({'package':p['name'],'requirement':text,'selected':versions.get(name)})
    check('Independent Python metadata edge/specifier verification after cu128 override',not errors,{'packages':len(versions),'active_edges':edges,'errors':errors,'ABI_proof':False})
    pins={'torch':'2.9.0+cu128','vllm':'0.11.2','transformers':'4.57.6','peft':'0.18.0','tokenizers':'0.22.2','jinja2':'3.1.6','triton':'3.5.0','flashinfer-python':'0.5.2','nvidia-nccl-cu12':'2.27.5','nvidia-cuda-nvrtc-cu12':'12.8.93','nvidia-cuda-runtime-cu12':'12.8.90'}
    check('Frozen package/CUDA/Triton/NCCL identities retained',all(versions.get(k)==v for k,v in pins.items()),pins)
    lock=load(P/'runtime_build_lock.json');check('Frozen base/platform/runtime retained',lock['platform']['base_image']==load(G/'runtime_lock.json')['platform']['container_base'] and lock['subject']==load(G/'runtime_lock.json')['subject'])
    sources=load(P/'source_archive_lock.json')['sources'];extra=load(P/'extra_inputs_lock.json');sources +=[r for r in extra['flash_attention_gitlinks'] if r['selected']]
    check('Retrieved exact code archive content hashes',all((P/r['path']).stat().st_size==r['bytes'] and sha(P/r['path'])==r['sha256'] for r in sources),{'archives':len(sources),'Qwen_bodies':0})
    check('FlashInfer cache metadata dependencies resolved',extra['flashinfer_jit_cache']['metadata_requires_dist']==[] and sha(P/extra['flashinfer_jit_cache']['metadata_path'])==extra['flashinfer_jit_cache']['metadata_sha256'],'Range metadata only; complete wheel hash verification remains PENDING')
    apt=load(P/'apt_dependency_lock.json');check('Apt exact metadata closure recorded',apt['failure'] is None and len(apt['packages'])==114 and len({r['name'] for r in apt['packages']})==114)
    check('Apt signed-header index SHA declarations match cached indexes',all(sha(P/r['path'])==r['sha256'] for r in apt['indexes']),{'index_count':len(apt['indexes']),'actual_GPGV':'PENDING_TARGET_BUILD','Deb_body_authentication':'PENDING_INPUT_COLLECTION'})
    runner=load(P/'runner_manifest.json');bad=[r['path'] for r in runner['files'] if not (P/r['path']).is_file() or sha(P/r['path'])!=r['sha256']]
    root=hashlib.sha256(canonical([{'path':r['path'],'sha256':r['sha256']} for r in runner['files']])).hexdigest()
    check('Runner/build/observer/isolation/oracle content root',not bad and root==runner['content_root_sha256'],{'files':len(runner['files']),'root_sha256':root,'bad':bad})
    syntax=[]
    for p in P.rglob('*.py'):
        try:ast.parse(p.read_text(encoding='utf-8'))
        except SyntaxError as e:syntax.append([p.relative_to(P).as_posix(),str(e)])
    check('Owned Python syntax without execution/import',not syntax,syntax)
    jsonschema.Draft202012Validator.check_schema(load(P/'target_attestation_schema.json'));check('Target contract JSON schema well-formed',True)
    oracle=ast.parse((P/'tests/oracle.py').read_text(encoding='utf-8'));check('Literal oracle independent of production imports',not any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(oracle)))
    for prefix,count in [('model_free',25),('preparation',11)]:
        batches=sorted((P/'test_results').glob(prefix+'_batch_*.json'));latest=load(batches[-1]);check('Latest '+prefix+' tests PASS',latest['result']=='PASS' and latest['tests_run']==count,{'batch':batches[-1].name,'tests':count,'all_previous_batches_retained':len(batches)})
    rows=[json.loads(line) for line in (P/'test_results/model_free_runs/provenance.jsonl').read_bytes().splitlines()];previous='0'*64;valid=True
    for r in rows:
        valid=valid and r['previous_sha256']==previous and r['entry_sha256']==hashlib.sha256(canonical({k:v for k,v in r.items() if k!='entry_sha256'})).hexdigest();previous=r['entry_sha256']
    check('All model-free attempts retained append-only hash chain',valid,{'entries':len(rows),'head_sha256':previous})
    schema=load(G/'run_manifest_schema.json');errors=[];receipts=list((P/'test_results/model_free_runs').glob('batch*/synthetic_receipt.json'))
    for p in receipts:
        d=load(p)
        errors.extend([str(e.message) for e in jsonschema.Draft202012Validator(schema).iter_errors(d['schema_payload'])])
        if d['schema_payload']['gate_result']=='PASS' or not d['model_free']:errors.append('Synthetic actual gate claim')
        for a in d['transport_artifact_hashes']:
            if sha(p.parent/a['path'])!=a['sha256']:errors.append(str(p)+' artifact mismatch')
    check('Retained synthetic schema/sidecar evidence and no actual Qwen PASS',not errors,{'receipts':len(receipts),'errors':errors})
    old=load(G/'pre_download_checklist.json');new=load(P/'pre_download_recheck.json');check('Recheck preserves every frozen mandatory requirement',len(old['items'])==len(new['items']) and all(a['id']==b['id'] and a['requirement']==b['frozen_requirement'] and a['mandatory']==b['mandatory'] and a['status']==b['previous_state'] for a,b in zip(old['items'],new['items'])))
    check('All previous PENDING correctly remain PENDING despite partial evidence',all(r['current_state']=='PENDING' for r in new['items'] if r['previous_state']=='PENDING') and new['verdict']=='NOT READY — RUNTIME_BUILD, TARGET_CAPACITY, RUNNER_ATTESTATION')
    check('No fabricated image/target/OS evidence',load(P/'runtime_build_manifest.json')['actual_image_config_digest'] is None and load(P/'target_capacity_policy.json')['actual_target_attested'] is False and load(P/'runner_attestation.json')['OS_config_is_PASS'] is False)
    if (P/'artifact_manifest.json').exists():
        artifact=load(P/'artifact_manifest.json');bad=[r['path'] for r in artifact['files'] if not (P/r['path']).is_file() or sha(P/r['path'])!=r['sha256']];check('Sealed new artifact manifest content hashes',not bad,{'files':len(artifact['files']),'bad':bad})
    result={'status':'PASS' if all(c['result']=='PASS' for c in checks) else 'FAIL','checks':checks,'pre_download_verdict':new['verdict'],'current_target_image_runtime_tests':'NOT_RUN/PENDING','current_model_free_tests':36,'prohibitions':{'weights_downloaded':False,'model_instantiated':False,'adapter_instantiated':False,'inference':False,'model_forward':False,'training':False,'GPU_used_or_rented':False,'A_S_started':False,'A_B_M_C_BC_experiments':False,'Study1_2_3':False,'protected_candidates_tasks_scorers_outcomes_accessed':False,'protocol_changed':False,'product_tracked_files_modified':False,'commit_made':False},'scope_attestation_basis':'All executed commands restricted to preparation metadata/source retrieval, model-free stdlib/jsonschema/packaging tests and explicit frozen artifact hashes; no native worker, target probe, Docker build or framework self-test executed. Runtime/target proof remains pending.','head':head,'git_status':status,'validation_role':'Implementer verification, not an assigned independent reviewer'}
    if '--write' in sys.argv:(P/'validation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'checks':len(checks),'prior_files':len(baseline['preserved_files']),'failures':[c for c in checks if c['result']=='FAIL'],'head':head,'git_status':status},ensure_ascii=True));sys.exit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
