"""Create proposal/metadata receipts and an artifact inventory; never freeze."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
WORKSPACE=ROOT.parents[2]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(name,value):
    (ROOT/name).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")

def main():
    metadata=json.loads((ROOT/"upstream/hub_metadata.json").read_text())
    shards=[{"file":s["rfilename"],"bytes":s["size"],"upstream_declared_sha256":s["lfs"]["sha256"],
        "local_weight_body_verified":False} for s in metadata["siblings"] if s["rfilename"].endswith(".safetensors")]
    write("weight_manifest.json",{"repository":metadata["id"],"revision":metadata["sha"],
        "shards":shards,"storage_bytes":sum(s["bytes"] for s in shards),"source":"pinned Hub API LFS metadata"})
    write("proposed_runtime.json",{
        "status":"PROPOSED_ONLY_NOT_FROZEN_NOT_CERTIFIED_NOT_EXECUTED",
        "runtime":"offline vLLM V1","version":"0.11.2","torch":"2.9.0","cuda_build":"12.8",
        "transformers":"4.57.6","tokenizers":"0.22.2","jinja2":"3.1.6",
        "model":metadata["id"],"revision":metadata["sha"],"tokenizer_revision":metadata["sha"],
        "engine":{"dtype":"bfloat16","quantization":None,"trust_remote_code":False,
            "generation_config":"vllm","max_model_len":32768,"tensor_parallel_size":1,
            "max_num_seqs":1,"seed":0,"enforce_eager":True,"enable_prefix_caching":False},
        "environment":{"VLLM_ENABLE_V1_MULTIPROCESSING":"0"},
        "sampling":{"temperature":0.0,"top_p":1.0,"top_k":0,"min_p":0.0,
            "repetition_penalty":1.0,"frequency_penalty":0.0,"presence_penalty":0.0,
            "seed":0,"stop":[],"stop_token_ids":[151643],"ignore_eos":False,"max_tokens":2048,
            "min_tokens":0,"n":1,"best_of":None,"truncate_prompt_tokens":None,
            "detokenize":False,"logits_processors":None,"allowed_token_ids":None,
            "bad_words":None,"structured_outputs":None,"logit_bias":None},
        "primary_eos_token_id":151645,"native_terminal_ids":[151645,151643],
        "wrapper_requirements":["prepared exact prompt_token_ids only","fresh sequence per request",
            "one call, no retries or fallback","no product mounts/tools or reads during generation",
            "pre-admit all five forms with full 2048 reserve","retain raw token IDs and completion facts",
            "decode without special-token stripping; account only final observed native terminal",
            "no clipping, shifting, truncation, reserve reduction or server auto defaults"],
        "pending":["complete binary/image/driver lock","exact checkpoint load","effective controls audit",
            "generation/termination smoke test","raw terminal token retention","repeatability measurement",
            "certified wrapper","adapter roundtrip and refresh cost"]})
    head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=WORKSPACE,text=True).strip()
    assert head=="7fcdecbe26f4fd01138edf8f58c02ce4b947db0b"
    assert subprocess.run(["git","diff","--exit-code"],cwd=WORKSPACE,capture_output=True).returncode==0
    assert subprocess.run(["git","diff","--cached","--exit-code"],cwd=WORKSPACE,capture_output=True).returncode==0
    policy=WORKSPACE/"benchmark_design/context_policy/current-repo-v1-draft3.json"
    assert sha(policy.read_bytes())=="d93f5136339153e65e35ef720333e21260292bc680f2cd3cfe608dfa46939a3b"
    rows=json.loads((ROOT/"capacity_checks.json").read_text())
    assert len(rows)==45
    for r in rows:
        assert r["total_reserved_tokens"] <=32768
    manifest=json.loads((ROOT/"upstream_manifest.json").read_text())
    for item in manifest["files"]:
        assert sha((ROOT/"upstream"/item["file"]).read_bytes())==item["sha256"]
    write("workspace_audit.json",{"head":head,"tracked_worktree_diff_empty":True,
        "staged_diff_empty":True,"policy_hash_unchanged":True,"all_new_artifacts_under":str(ROOT),
        "policy_exclusion":"experiments", "candidate_artifacts_inspected":False,
        "benchmark_tasks_inspected":False,"benchmark_execution":False,"generation_performed":False,
        "training_performed":False,"commit_created":False,"model_frozen":False})
    files=[]
    for p in sorted(ROOT.rglob("*")):
        relative=p.relative_to(ROOT)
        if "dependencies" in relative.parts or "__pycache__" in relative.parts or p.name=="artifact_manifest.json":
            continue
        if p.is_file():
            data=p.read_bytes()
            files.append({"path":relative.as_posix(),"bytes":len(data),"sha256":sha(data)})
    write("artifact_manifest.json",{"note":"Self and local dependencies excluded. Dependencies identified by tokenizer-requirements.lock.txt.","files":files})
    print(json.dumps({"artifacts":len(files),"artifact_bytes":sum(x["bytes"] for x in files),
        "max_input_tokens":max(r["input_tokens"] for r in rows),
        "max_reserved_tokens":max(r["total_reserved_tokens"] for r in rows),"head":head,"tracked_diff_empty":True},indent=2))

if __name__=="__main__":
    main()
