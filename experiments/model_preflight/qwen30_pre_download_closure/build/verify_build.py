"""Offline verify future build receipts and saved image; never executes a model."""
import hashlib,json,sys
from pathlib import Path
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def main():
    p=Path(sys.argv[1]);receipt=json.loads((p/'digest_receipt.json').read_text(encoding='utf-8'));attempt=json.loads((p/'attempt.json').read_text(encoding='utf-8'))
    selftest=json.loads((p/'evidence/self_test.json').read_text(encoding='utf-8'));sbom=json.loads((p/'evidence/sbom.json').read_text(encoding='utf-8'));image=json.loads((p/'image_inspect.json').read_text(encoding='utf-8'))[0]
    checks={'build_exit_zero':attempt['exit_code']==0,'one_attempt_no_retry':attempt['invocations']==1 and attempt['retries']==0,'no_GPU_or_model':not attempt['GPU_used'] and not attempt['models_used'],
        'self_test_PASS':selftest['status']=='PASS' and selftest['stage']=='BUILD-TIME','image_config_digest_matches':image['Id']==receipt['image_config_digest'],
        'saved_image_SHA_matches':sha(p/'image.tar')==receipt['OCI_archive_sha256'],'SBOM_generated_wheels':len(sbom['generated_wheels'])==3,'platform':image['Os']=='linux' and image['Architecture']=='amd64'}
    result={'checks':checks,'build_identity_verified':all(checks.values()),'selftest_sha256':sha(p/'evidence/self_test.json'),'SBOM_sha256':sha(p/'evidence/sbom.json'),'image_config_digest':image['Id'],'target_runtime_pass':False}
    print(json.dumps(result,indent=2));sys.exit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
