"""Invented target receipts and source-code checks only; no target probe or GPU queries."""
import ast,copy,hashlib,json,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P))
from target_attestation_validator import validate
import jsonschema
class PreparationTests(unittest.TestCase):
    def fixture(self):
        command={'argv':['invented-inventory-command'],'stdout':'invented static receipt','error':None}
        # Independent literal oracle for exact required isolation proofs.
        iso={'kind':'ACTUAL_LINUX_CPU_ONLY_ISOLATION_PROBE','all_pass':True,'mountinfo':'invented readonly mounts','probes':dict.fromkeys(['non_root_uid','capabilities_zero','no_new_privileges','seccomp_filter','only_loopback','network_attempt_denied','outside_canary_read_denied','model_mount_write_denied','input_mount_write_denied','no_credentials','no_Docker_socket','no_SSH_socket','scoped_write','allowed_mounts_verified'],True)}
        raw=json.dumps(iso,sort_keys=True)
        d={'schema_version':'qwen30-target-attestation-v1','kind':'INVENTED_CONTRACT_TEST','observed_utc_ns':1,'os':'Linux','architecture':'x86_64','kernel':'invented kernel',
        'physical_GPU_count':1,'devices':[{'uuid':'GPU-11111111-1111-1111-1111-111111111111','model':'INVENTED GPU','compute_capability':'9.0','total_VRAM_bytes':85899345920,'free_VRAM_bytes':85899345920,'ECC':'Enabled','MIG':'Disabled','driver_version':'570.124.06'}],
        'selected_GPU_UUID':'GPU-11111111-1111-1111-1111-111111111111','tensor_parallel_size':1,'host_RAM_total_bytes':137438953472,'host_RAM_available_bytes':137438953472,'storage_total_bytes':500000000000,'storage_free_bytes':250000000000,
        'staging_path':'/invented/staging','scratch_path':'/invented/scratch','scratch_writable':True,'cgroup_v2':True,'cgroup_memory_peak_support':True,'proc_smaps_rollup_support':True,'clock':{'source':'time.monotonic_ns/CLOCK_MONOTONIC','resolution_seconds':1e-9,'monotonic':True},
        'OS_isolation_receipt':iso,'OS_isolation_receipt_raw_utf8':raw,'OS_isolation_receipt_sha256':hashlib.sha256(raw.encode()).hexdigest(),'provider_selected':False,'model_acquired':False,'model_allocated':False,'GPU_workload_executed':False}
        for k in ['topology','filesystem','driver_CUDA_report','container_runtime','raw_GPU_query']:d[k]=copy.deepcopy(command)
        return d
    def test_schema_valid_invented_fixture(self):jsonschema.Draft202012Validator(json.loads((P/'target_attestation_schema.json').read_text(encoding='utf-8'))).validate(self.fixture())
    def test_invented_never_actual_attestation(self):self.assertFalse(validate(self.fixture())['actual_host_attested'])
    def test_missing_capacity_pending(self):
        d=self.fixture();d.pop('storage_free_bytes');self.assertEqual(validate(d)['status'],'PENDING')
    def test_TP2_rejected(self):
        d=self.fixture();d['tensor_parallel_size']=2;self.assertIn('Frozen TP1 required',validate(d)['reasons'])
    def test_capacity_literal_floor(self):
        d=self.fixture();d['storage_free_bytes']=249999999999;self.assertIn('Storage >=250GB free required',validate(d)['reasons'])
    def test_MIG_rejected(self):
        d=self.fixture();d['devices'][0]['MIG']='Enabled';self.assertTrue(any('MIG' in r for r in validate(d)['reasons']))
    def test_OS_config_alone_not_proof(self):
        d=self.fixture();d['OS_isolation_receipt']['probes'].pop('network_attempt_denied');self.assertTrue(any('isolation evidence incomplete' in r for r in validate(d)['reasons']))
    def test_OS_hash_mutation(self):
        d=self.fixture();d['OS_isolation_receipt_sha256']='0'*64;self.assertTrue(any('binding mismatch' in r for r in validate(d)['reasons']))
    def test_driver_and_bad_numeric_fail_closed(self):
        d=self.fixture();d['devices'][0]['driver_version']='unknown';self.assertEqual(validate(d)['status'],'PENDING')
    def test_seccomp_default_deny(self):
        d=json.loads((P/'isolation/seccomp.json').read_text(encoding='utf-8'));self.assertEqual(d['defaultAction'],'SCMP_ACT_ERRNO');self.assertEqual(d['architectures'],['SCMP_ARCH_X86_64'])
        unconditional=set(n for r in d['syscalls'] if not r.get('args') for n in r['names']);self.assertTrue({'mount','unshare','setns','ptrace','socket','clone3'}.isdisjoint(unconditional))
        clone=next(r for r in d['syscalls'] if r['names']==['clone']);self.assertEqual(clone['args'],[{'index':0,'value':0x7e020080,'valueTwo':0,'op':'SCMP_CMP_MASKED_EQ'}])
    def test_safe_local_imports(self):
        for name in ['supervisor','interface','isolation','observer','semantic_validator','schema_validator','synthetic_worker']:
            tree=ast.parse((P/'runner'/f'{name}.py').read_text(encoding='utf-8'))
            imports=[n for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
            modules=[a.name for n in imports if isinstance(n,ast.Import) for a in n.names]+[n.module or '' for n in imports if isinstance(n,ast.ImportFrom)]
            self.assertFalse(any(m.split('.')[0] in {'torch','vllm','transformers','peft'} for m in modules))
if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PreparationTests));batch=len(list((P/'test_results').glob('preparation_batch_*.json')))+1
    (P/f'test_results/preparation_batch_{batch}.json').write_text(json.dumps({'result':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'failures':[(str(t),s) for t,s in result.failures],'errors':[(str(t),s) for t,s in result.errors],'all_inputs_invented':True,'actual_target_attested':False,'model_instantiated':False,'GPU_queries':0},indent=2)+'\n',encoding='utf-8');sys.exit(0 if result.wasSuccessful() else 1)
