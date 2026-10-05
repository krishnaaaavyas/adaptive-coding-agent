"""Future Linux inventory only. No allocation, models, project traversal or provisioning."""
import argparse,csv,json,os,platform,shutil,subprocess,time
from pathlib import Path
def command(args):
    try: return {'argv':args,'stdout':subprocess.check_output(args,stderr=subprocess.STDOUT,text=True,timeout=15).strip(),'error':None}
    except (OSError,subprocess.SubprocessError) as e: return {'argv':args,'stdout':None,'error':type(e).__name__}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--selected-gpu-uuid',required=True);ap.add_argument('--staging',required=True);ap.add_argument('--scratch',required=True);ap.add_argument('--isolation-receipt',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    if platform.system()!='Linux' or platform.machine() not in ['x86_64','amd64']:raise SystemExit('PENDING_TARGET_LINUX_AMD64; no inventory performed')
    staging=Path(a.staging).resolve(strict=True); scratch=Path(a.scratch).resolve(strict=True)
    disk=shutil.disk_usage(staging); mem={}
    for s in Path('/proc/meminfo').read_text(encoding='utf-8').splitlines():
        k,v=s.split(':',1);mem[k]=int(v.strip().split()[0])*1024
    gpu=command(['nvidia-smi','--query-gpu=uuid,name,compute_cap,memory.total,memory.free,ecc.mode.current,mig.mode.current,driver_version','--format=csv,noheader,nounits'])
    devices=[]
    if gpu['stdout']:
        for r in csv.reader(gpu['stdout'].splitlines(),skipinitialspace=True):
            if len(r)==8:
                devices.append(dict(zip(['uuid','model','compute_capability','total_VRAM_MiB','free_VRAM_MiB','ECC','MIG','driver_version'],r)))
    for d in devices:
        d['total_VRAM_bytes']=int(d.pop('total_VRAM_MiB'))*1048576;d['free_VRAM_bytes']=int(d.pop('free_VRAM_MiB'))*1048576
    # Exclusive creation on explicitly supplied scratch only, removes only that single invented file.
    canary=scratch/('qwen30-preacquisition-probe-'+str(os.getpid()))
    writable=False
    try:
        with canary.open('xb') as f:f.write(b'invented scratch capacity probe')
        writable=True
    finally:
        if writable:canary.unlink()
    iso_path=Path(a.isolation_receipt)
    isolation=json.loads(iso_path.read_text(encoding='utf-8'))
    import hashlib
    result={'schema_version':'qwen30-target-attestation-v1','kind':'ACTUAL_TARGET_INVENTORY','observed_utc_ns':time.time_ns(),'os':platform.system(),'architecture':platform.machine(),'kernel':platform.release(),
        'physical_GPU_count':len(devices),'devices':devices,'selected_GPU_UUID':a.selected_gpu_uuid,'tensor_parallel_size':1,'topology':command(['nvidia-smi','topo','-m']),
        'host_RAM_total_bytes':mem['MemTotal'],'host_RAM_available_bytes':mem['MemAvailable'],'storage_total_bytes':disk.total,'storage_free_bytes':disk.free,
        'filesystem':command(['findmnt','-J','-T',str(staging)]),'staging_path':str(staging),'scratch_path':str(scratch),'scratch_writable':writable,
        'driver_CUDA_report':command(['nvidia-smi']),'container_runtime':command(['docker','version','--format','{{json .}}']),
        'cgroup_v2':Path('/sys/fs/cgroup/cgroup.controllers').exists(),'cgroup_memory_peak_support':Path('/sys/fs/cgroup/memory.peak').exists(),'proc_smaps_rollup_support':Path('/proc/self/smaps_rollup').exists(),
        'clock':{'source':'time.monotonic_ns/CLOCK_MONOTONIC','resolution_seconds':time.get_clock_info('monotonic').resolution,'monotonic':time.get_clock_info('monotonic').monotonic},
        'OS_isolation_receipt':isolation,'OS_isolation_receipt_raw_utf8':iso_path.read_text(encoding='utf-8'),'OS_isolation_receipt_sha256':hashlib.sha256(iso_path.read_bytes()).hexdigest(),'raw_GPU_query':gpu,
        'provider_selected':False,'model_acquired':False,'model_allocated':False,'GPU_workload_executed':False}
    Path(a.output).open('x',encoding='utf-8').write(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
