"""Static artifact and preservation verification; no model or adapter execution."""
import sys
sys.dont_write_bytecode=True
import ast
import csv
import hashlib
import json
import pathlib
import re
import subprocess
from urllib.parse import urlparse
from datetime import datetime, timezone

ROOT=pathlib.Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]
REPO='mistralai/Devstral-Small-2-24B-Instruct-2512'
SHA='55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128'
REQUIRED=['REPORT.md','source_manifest.json','identity.json','serialization.json','capacity_checks.json',
          'runtime_profile.json','adaptation_targets.json','original_base_lifecycle.json','resource_estimates.json',
          'infrastructure_test_matrix.csv','reconstruction_analysis.json','tokenizer_environment.json']

def digest(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def dump(path,data):(ROOT/path).write_text(json.dumps(data,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=WORKSPACE,text=True,encoding='utf-8').strip()

def main():
    for name in REQUIRED:assert (ROOT/name).is_file(),name
    # Enumerate the dedicated output tree only, not candidate or product repositories.
    files=sorted((p for p in ROOT.rglob('*') if p.is_file()),key=lambda p:p.relative_to(ROOT).as_posix())
    parsed=[]
    for p in files:
        if p.suffix=='.json':
            json.loads(p.read_text(encoding='utf-8'));parsed.append(p.relative_to(ROOT).as_posix())
    source=read('source_manifest.json');retrieved=[r for r in source['files'] if r['status']=='retrieved']
    for r in retrieved:
        p=(ROOT/r['path']).resolve();assert p.is_relative_to(ROOT)
        assert p.stat().st_size==r['bytes'] and digest(p.read_bytes())==r['sha256'],r['path']
        assert r['url'].startswith('https://') and r['retrieved_at_utc']
        assert p.suffix not in ('.safetensors','.gguf','.pt','.pth','.bin'),r['path']
        assert pathlib.PurePosixPath(urlparse(r['url']).path).suffix not in ('.safetensors','.gguf','.pt','.pth','.bin')
    for r in source['local_project_inputs']:
        p=WORKSPACE/r['path'];assert p.stat().st_size==r['bytes'] and digest(p.read_bytes())==r['sha256']
    with (ROOT/'infrastructure_test_matrix.csv').open(encoding='utf-8',newline='') as stream:
        reader=csv.DictReader(stream);assert reader.fieldnames==['id','test','procedure','acceptance','status']
        rows=list(reader)
    assert len(rows)==24 and [r['id'] for r in rows]==list('ABCDEFGHIJKLMNOPQRSTUVWX')
    assert all(r['status']=='NOT_RUN' and all(r.values()) for r in rows)
    report=(ROOT/'REPORT.md').read_text(encoding='utf-8')
    assert [int(n) for n in re.findall(r'^## (\d+)\.',report,re.M)]==list(range(1,24))
    # Check local markdown targets inside the dedicated output and allowed project paths.
    for link in re.findall(r'\]\(([^)]+)\)',report):
        if '://' not in link and not link.startswith('#') and link not in ('validation.json','artifact_manifest.json'):
            assert (ROOT/link).resolve().is_file(),link
    identity=read('identity.json');assert identity['repository']==REPO and identity['revision']==SHA
    assert not identity['landscape_discrepancies']
    capacity=read('capacity_checks.json');assert capacity['maximum_synthetic_input_tokens']==20454
    assert capacity['maximum_input_plus_2048']==22502 and capacity['reserve']==2048 and capacity['deployed_target']==32768
    assert capacity['capacity_violations']==0 and capacity['all_256_byte_alphabet_symbols_in_vocab']
    targets=read('adaptation_targets.json');assert len(targets['catalog'])==585 and len(targets['modules'])==280
    for name,count,parameters in [('attention_only',160,19660800),('attention_plus_mlp',280,92405760)]:
        scope=targets['scopes'][name];assert scope['base_weight_tensors']==count and scope['trainable_parameters_rank16']==parameters
        assert all(re.fullmatch(scope['target_regex'],m) and 'vision' not in m for m in scope['target_modules'])
    runtime=read('runtime_profile.json');assert len(runtime['frozen_control_map'])==15
    assert runtime['sampling_params']['max_tokens']==2048 and runtime['engine_args']['max_model_len']==32768
    assert all(r['infrastructure_status']=='INFRASTRUCTURE-UNVERIFIED' for r in runtime['frozen_control_map'].values())
    reconstruction=read('reconstruction_analysis.json');assert reconstruction['static_path_established'] and not reconstruction['verified_lifecycle']
    assert reconstruction['dense_export_required']['save_original_format'] is False
    env=read('tokenizer_environment.json');assert not env['torch_imported'] and not env['model_libraries_imported']
    # Audit imports in authored scripts only, never execute downloaded upstream code.
    imports=[]
    for p in ROOT.glob('*.py'):
        for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))):
            if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
            elif isinstance(n,ast.ImportFrom):imports.append(n.module or '')
    assert not any(m.split('.')[0] in ('torch','transformers','peft','vllm') for m in imports)
    body_files=[p.relative_to(ROOT).as_posix() for p in files if p.suffix.lower() in ('.safetensors','.gguf','.pt','.pth','.bin')]
    assert not body_files
    baseline=read('baseline_integrity.json');preserved=baseline['preserved_files']
    for r in preserved:
        p=WORKSPACE/r['path'];assert p.stat().st_size==r['bytes'] and digest(p.read_bytes())==r['sha256'],r['path']
    head=git('rev-parse','HEAD');status=git('status','--short')
    assert head==baseline['head'] and status==baseline['status']
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    validation={'status':'PASS_STATIC_ARTIFACT_VALIDATION','validated_at_utc':datetime.now(timezone.utc).isoformat(),
                'subject_repository':REPO,'subject_revision':SHA,'required_artifacts_present':True,
                'all_generated_and_source_JSON_parsed':True,'json_files_parsed_before_finalization':len(parsed),
                'source_reference_hashes_verified':len(retrieved),'local_project_input_hashes_verified':len(source['local_project_inputs']),
                'csv_schema_valid':True,'infrastructure_items':len(rows),'all_infrastructure_NOT_RUN':True,
                'report_sections':23,'local_markdown_links_valid':True,'exact_identity_and_landscape_match':True,
                'synthetic_capacity_checks_passed':True,'no_weight_body_files_or_weight_URL_requests':True,
                'no_inference':True,'no_model_instantiation':True,'no_adapter_instantiation':True,
                'no_upstream_training_serving_recipe_execution':True,'protected_candidate_inventory_accessed':False,
                'protected_outcomes_accessed':False,'candidate_blindness_evidence':'Scope/process attestation: acquisition allowlist, authored imports and explicit permitted project inputs; not an OS-level trace certificate',
                'native_tensor_layouts_verified':False,'deterministic_model_inference_verified':False,
                'fresh_base_lifecycle_empirically_verified':False,'isolation_empirically_certified':False,
                'product_repositories_unchanged':True,'protocol_modified':False,'preserved_existing_files_verified':len(preserved),
                'historical_and_landscape_hashes_unchanged':True,'git_tracked_and_staged_diff_empty':True,
                'HEAD_unchanged':True,'final_HEAD':head,'initial_git_status':baseline['status'],'final_git_status':status,
                'commit_made':False,'fallback_triggered':False,'GPU_use_or_spending_authorized':False,
                'artifact_hash_check':'All manifest-listed file hashes recomputed and asserted after artifact_manifest.json is written; manifest excludes itself to avoid recursion',
                'model_parameter_count_inference':24011361280,'rank16_attention_parameters':19660800,'rank16_combined_parameters':92405760}
    dump('validation.json',validation)
    files=sorted((p for p in ROOT.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'),key=lambda p:p.relative_to(ROOT).as_posix())
    manifest={'subject_repository':REPO,'subject_revision':SHA,'scope':'entire dedicated preflight tree; no historical files mutated',
              'excluded_self':'artifact_manifest.json (no circular self-hash)','files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in files]}
    dump('artifact_manifest.json',manifest)
    assert (ROOT/'validation.json').is_file() and (ROOT/'artifact_manifest.json').is_file()
    for r in read('artifact_manifest.json')['files']:
        p=ROOT/r['path'];assert p.stat().st_size==r['bytes'] and digest(p.read_bytes())==r['sha256']
    json.loads((ROOT/'validation.json').read_text(encoding='utf-8'))
    print(json.dumps({'status':validation['status'],'source_hashes':len(retrieved),'artifact_hashes':len(files),
                      'preserved_files':len(preserved),'HEAD':head,'git_status':status,'all_infrastructure_items':'NOT_RUN'},indent=2))

if __name__=='__main__':main()
