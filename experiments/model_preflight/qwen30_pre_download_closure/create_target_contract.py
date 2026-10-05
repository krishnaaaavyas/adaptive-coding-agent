import json
from pathlib import Path
P=Path(__file__).resolve().parent
def write(name,d):(P/name).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
integer={'type':'integer','minimum':0}; text={'type':'string','minLength':1}; boolean={'type':'boolean'}
command={'type':'object','required':['argv','stdout','error'],'properties':{'argv':{'type':'array','items':{'type':'string'}},'stdout':{'type':['string','null']},'error':{'type':['string','null']}},'additionalProperties':False}
device={'type':'object','required':['uuid','model','compute_capability','total_VRAM_bytes','free_VRAM_bytes','ECC','MIG','driver_version'],'properties':{k:text for k in ['uuid','model','compute_capability','ECC','MIG','driver_version']},'additionalProperties':False}
device['properties'].update({k:integer for k in ['total_VRAM_bytes','free_VRAM_bytes']})
device['properties']['compute_capability']={'type':'string','pattern':'^[0-9]+\\.[0-9]+$'}
device['properties']['driver_version']={'type':'string','pattern':'^[0-9]+\\.[0-9]+\\.[0-9]+$'}
props={k:text for k in ['schema_version','kind','os','architecture','kernel','selected_GPU_UUID','staging_path','scratch_path','OS_isolation_receipt_sha256']}
props.update({k:integer for k in ['observed_utc_ns','physical_GPU_count','tensor_parallel_size','host_RAM_total_bytes','host_RAM_available_bytes','storage_total_bytes','storage_free_bytes']})
props.update({k:boolean for k in ['scratch_writable','cgroup_v2','cgroup_memory_peak_support','proc_smaps_rollup_support','provider_selected','model_acquired','model_allocated','GPU_workload_executed']})
props.update({k:command for k in ['topology','filesystem','driver_CUDA_report','container_runtime','raw_GPU_query']})
props.update(devices={'type':'array','items':device},clock={'type':'object','required':['source','resolution_seconds','monotonic'],'properties':{'source':text,'resolution_seconds':{'type':'number','exclusiveMinimum':0},'monotonic':{'const':True}},'additionalProperties':False},OS_isolation_receipt={'type':'object','required':['kind','probes','all_pass','mountinfo']})
props['OS_isolation_receipt_raw_utf8']=text
props['schema_version']={'const':'qwen30-target-attestation-v1'};props['kind']={'enum':['ACTUAL_TARGET_INVENTORY','INVENTED_CONTRACT_TEST']};props['OS_isolation_receipt_sha256']={'type':'string','pattern':'^[a-f0-9]{64}$'}
write('target_attestation_schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:qwen30:target-attestation:v1','type':'object','required':list(props),'properties':props,'additionalProperties':False})
write('target_capacity_policy.json',{'status':'TARGET CONTRACT COMPLETE — ACTUAL HOST ATTESTATION PENDING','frozen_authority':'../qwen30_infrastructure_governance/hardware_requirements.json','actual_target_attested':False,'provider':None,'tensor_parallel_size':1,'selected_devices':1,'driver_minimum':'570.124.06','compute_capability_minimum':8.0,'planning':{'BF16_payload_GiB':56.872,'KV_GiB_before_workspace':3,'free_device_GiB_plausible':70,'free_device_GiB_preferred':80,'RAM_total_GiB_plausible':64,'RAM_total_GiB_preferred':128,'storage_free_bytes':250000000000},'planning_is_fit_guarantee':False,'below_planning_point':'C/PENDING capacity evidence, never fundamental model failure','required_actual_evidence':['target_probe inventory','hash-bound actual Linux CPU-only isolation probe','selected TP1 full device UUID','driver / CUDA compatibility','fresh available capacities','cgroup v2 memory.peak and /proc/smaps_rollup','image/source/runner binding before model acquisition'],'probe_does_not_read_project_material':True,'provisioning_authorized':False,'acquisition_authorized':False})
