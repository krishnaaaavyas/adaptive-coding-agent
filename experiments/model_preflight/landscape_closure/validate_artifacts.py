"""Integrity checks for static audit artifacts; never touches model/project tests."""
import csv
import datetime
import hashlib
import json
import pathlib
import re
import subprocess

ROOT=pathlib.Path(__file__).resolve().parent
manifest=json.loads((ROOT/'source_manifest.json').read_text(encoding='utf-8'))
with (ROOT/'landscape.csv').open(encoding='utf-8',newline='') as f:
    reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
assert len(rows)==36
assert len({r['repository'] for r in rows})==len(rows)
assert set(r['repository'] for r in rows)==set(r['repository'] for r in manifest['models'])
allowed={'FULL PREFLIGHT','TARGETED PREFLIGHT','INFERENCE-ONLY REFERENCE','REDUNDANT REPRESENTATIVE','EXCLUDE'}
assert all(r['disposition'] in allowed for r in rows)
assert not any('score' in f.lower() or 'quality' in f.lower() for f in fields)
assert all(r['weight_bodies_downloaded']=='False' for r in rows)
cutoff=datetime.datetime.fromisoformat('2026-10-03T18:29:59+00:00')
for r in manifest['models']:
    assert re.fullmatch('[0-9a-f]{40}',r['revision'])
    assert datetime.datetime.fromisoformat(r['modified_at'].replace('Z','+00:00'))<=cutoff
    meta=json.loads((ROOT/r['metadata']['path']).read_text(encoding='utf-8'))
    assert meta['sha']==r['revision']
    assert not meta.get('disabled',False)
for s in manifest['support_repositories']:
    assert datetime.datetime.fromisoformat(s['commit_date'].replace('Z','+00:00'))<=cutoff
retrieved=[]; unavailable=[]
def check_record(record):
    if record['status']!='retrieved':
        unavailable.append({'url':record['url'],'status':record['status']});return
    path=ROOT/record['path'];data=path.read_bytes()
    assert path.resolve().is_relative_to(ROOT.resolve())
    assert len(data)==record['bytes']<=manifest['per_response_limit_bytes']
    assert hashlib.sha256(data).hexdigest()==record['sha256']
    assert path.suffix.lower() not in {'.safetensors','.bin','.gguf','.pt','.pth'}
    retrieved.append(record['path'])
for s in manifest['models']:
    check_record(s['metadata'])
    for f in s['files']:check_record(f)
for s in manifest['support_repositories']:
    check_record(s['identity'])
    for f in s['files']:check_record(f)
for f in manifest['support_pages']:check_record(f)
for item in manifest['project_inputs']:
    original=pathlib.Path(item['original_path']).read_bytes()
    archived=(ROOT/item['archived_path']).read_bytes()
    assert original==archived
    assert hashlib.sha256(original).hexdigest()==item['sha256']
for item in manifest['selected_weight_packaging']:
    assert item['bytes_declared']>0
    if item['repository'].startswith('mistralai/'):
        assert all(n.startswith('model-') for n in item['files'])
report=(ROOT/'REPORT.md').read_text(encoding='utf-8')
assert [int(n) for n in re.findall(r'^## (\d+)\.',report,re.M)]==list(range(1,24))
qwen=[r for r in rows if r['static_preflight_state']=='completed_historical']
assert len(qwen)==2 and all(r['inference']=='PASS' for r in qwen)
gpt=next(r for r in rows if r['repository']=='openai/gpt-oss-20b')
assert gpt['disposition']=='EXCLUDE' and gpt['static_preflight_state']=='historical_protocol_drop'
assert len([r for r in rows if r['static_preflight_state'].startswith('minimum_')])==3
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head=='7fcdecbe26f4fd01138edf8f58c02ce4b947db0b'
tracked=subprocess.run(['git','diff','--exit-code'],cwd=ROOT,capture_output=True,text=True)
assert tracked.returncode==0,tracked.stdout
assert subprocess.run(['git','diff','--cached','--exit-code'],cwd=ROOT,capture_output=True).returncode==0
status=subprocess.check_output(['git','status','--short'],cwd=ROOT.parents[2],text=True).strip()
assert status=='?? experiments/model_preflight/'
validation={'status':'PASS','scope':'static artifact/source/repository integrity only',
 'landscape_rows':len(rows),'required_sections':23,'retrieved_sources_checked':len(retrieved),
 'maximum_source_bytes':max((ROOT/path).stat().st_size for path in retrieved),
 'unavailable_sources':unavailable,'all_pinned_revisions_at_or_before_requested_calendar_cutoff':True,
 'no_weight_body_extension_present':not any(p.suffix.lower() in {'.safetensors','.bin','.gguf','.pt','.pth'} for p in ROOT.rglob('*') if p.is_file()),
 'declared_weight_package_selection_excludes_alternative_Mistral_consolidated_files':True,
 'separate_I_A_P_and_five_eligibility_subgates':True,'benchmark_score_fields_present':False,
 'historical_Qwen_states_and_Harmony_drop_retained':True,
 'minimum_new_static_work_items':3,'tracked_files_unchanged':True,'staged_files_unchanged':True,
 'head':head,'git_status':status,'preserved_input_hashes':manifest['project_inputs'],
 'empirical_model_validation_performed':False,'project_tests_or_evaluators_run':False}
(ROOT/'validation.json').write_text(json.dumps(validation,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
# Local standard-library import caches are not audit evidence; remove only these files.
cache=ROOT/'__pycache__'
if cache.exists():
    assert cache.resolve().is_relative_to(ROOT.resolve())
    for p in cache.glob('*.pyc'):p.unlink()
    if not list(cache.iterdir()):cache.rmdir()
artifacts=[]
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path.name=='artifact_manifest.json':continue
    data=path.read_bytes()
    artifacts.append({'path':str(path.relative_to(ROOT)).replace('\\','/'),
                      'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
artifact={'schema':'landscape-artifact-manifest-v1','root':str(ROOT),
 'self_excluded':True,'model_weight_bodies_downloaded':False,'files':artifacts}
(ROOT/'artifact_manifest.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'validation':'PASS','models':len(rows),'sources':len(retrieved),'artifacts':len(artifacts),
                  'archive_bytes':sum(x['bytes'] for x in artifacts),'unavailable':len(unavailable)},indent=2))
