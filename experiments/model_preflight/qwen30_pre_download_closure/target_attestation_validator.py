"""Fail-closed target contract validation; invented fixtures never attest actual hardware."""
import json,re,sys
from pathlib import Path
import jsonschema
P=Path(__file__).resolve().parent
def validate(d):
    problems=[]
    schema=json.loads((P/'target_attestation_schema.json').read_text(encoding='utf-8'))
    problems.extend(str(e.message) for e in jsonschema.Draft202012Validator(schema).iter_errors(d))
    if problems:return {'status':'PENDING','class':'C','reasons':problems,'actual_host_attested':False}
    if d['kind']!='ACTUAL_TARGET_INVENTORY':problems.append('Synthetic fixture cannot establish actual target')
    if d['os']!='Linux' or d['architecture'] not in ['x86_64','amd64']:problems.append('Linux amd64 required')
    if d['physical_GPU_count']!=len(d['devices']) or d['physical_GPU_count']<1:problems.append('Physical GPU inventory inconsistent')
    selected=[x for x in d['devices'] if x['uuid']==d['selected_GPU_UUID']]
    if len(selected)!=1:problems.append('Exactly one selected physical device required')
    else:
        x=selected[0]
        if not re.fullmatch(r'GPU-[0-9a-fA-F-]+',x['uuid']) or x['MIG'] not in ['Disabled','N/A','[N/A]']:problems.append('Selected full device / disabled MIG evidence required')
        if float(x['compute_capability'])<8:problems.append('BF16-capable CC >=8 required')
        if tuple(map(int,x['driver_version'].split('.')))<(570,124,6):problems.append('Driver below frozen conservative floor')
        if x['free_VRAM_bytes']>x['total_VRAM_bytes']:problems.append('Impossible free VRAM')
        if x['free_VRAM_bytes']<70*2**30:problems.append('Below plausible planning point; capacity review/evidence pending, not model failure')
    if d['tensor_parallel_size']!=1:problems.append('Frozen TP1 required')
    if d['host_RAM_total_bytes']<64*2**30 or d['host_RAM_available_bytes']>d['host_RAM_total_bytes']:problems.append('RAM provision/inventory insufficient')
    if d['storage_free_bytes']<250000000000 or d['storage_free_bytes']>d['storage_total_bytes']:problems.append('Storage >=250GB free required')
    if not d['scratch_writable']:problems.append('Writable scoped scratch proof absent')
    for k in ['filesystem','container_runtime','driver_CUDA_report','topology']:
        if d[k].get('error') or not d[k].get('stdout'):problems.append(k+' evidence absent')
    for k in ['cgroup_v2','cgroup_memory_peak_support','proc_smaps_rollup_support']:
        if not d[k]:problems.append(k+' observer support absent')
    iso=d['OS_isolation_receipt']
    import hashlib
    raw=d['OS_isolation_receipt_raw_utf8'].encode('utf-8')
    try:matches=json.loads(raw)==iso
    except ValueError:matches=False
    if not matches or hashlib.sha256(raw).hexdigest()!=d['OS_isolation_receipt_sha256']:problems.append('OS receipt body/hash binding mismatch')
    if iso.get('kind')!='ACTUAL_LINUX_CPU_ONLY_ISOLATION_PROBE' or iso.get('all_pass') is not True:problems.append('Actual CPU-only Linux OS probe absent/failed')
    required=['non_root_uid','capabilities_zero','no_new_privileges','seccomp_filter','only_loopback','network_attempt_denied','outside_canary_read_denied','model_mount_write_denied','input_mount_write_denied','no_credentials','no_Docker_socket','no_SSH_socket','scoped_write','allowed_mounts_verified']
    if any(iso.get('probes',{}).get(k) is not True for k in required):problems.append('Required actual isolation evidence incomplete')
    return {'status':'PENDING' if problems else 'PASS','class':'C' if problems else None,'reasons':problems,'actual_host_attested':not problems,'capacity_measured_fit_guaranteed':False,'authorization_to_acquire':False}
if __name__=='__main__':
    r=validate(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')));print(json.dumps(r,indent=2));sys.exit(0 if r['status']=='PASS' else 2)
