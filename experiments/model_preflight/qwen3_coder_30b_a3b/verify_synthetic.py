"""Offline exact-tokenizer checks; no products, candidates, generation or training.

Imports only protocol framing/packing helpers. Synthetic records are deliberately
not certified evidence; this is not official admission or a benchmark run.
"""
import ctypes
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
sys.path.insert(0, str(ROOT / "dependencies"))
sys.path.insert(0, str(REPO_ROOT))
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["USE_TORCH"] = "0"
from transformers import AutoTokenizer
from transformers.models.gpt2.tokenization_gpt2 import bytes_to_unicode
from harness.context_policy.core import (SYSTEM, canonical_json, digest, K_OPEN, K_CLOSE,
    H_OPEN, H_CLOSE, L_OPEN, L_CLOSE, POLICY_SHA256)
from harness.context_policy.evidence import pack_h, record_block
from harness.context_policy.protocol import messages

def dump(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

def fill_bytes(pattern, size):
    output = bytearray()
    block = pattern.encode("utf-8")
    output.extend(block * (size // len(block)))
    text = output.decode("utf-8")
    for char in pattern:
        if len(text.encode("utf-8")) + len(char.encode("utf-8")) > size:
            break
        text += char
    return text + "x" * (size - len(text.encode("utf-8")))

def make_task(pattern, size):
    task = {"instructions": "", "targets": ["synthetic.py"]}
    budget = size - len(canonical_json(task))
    # Size is canonical J(P) bytes, including Unicode/quote escaping.
    escaped = json.dumps(pattern, ensure_ascii=True)[1:-1]
    task["instructions"] = pattern * (budget // len(escaped))
    task["instructions"] += "x" * (size - len(canonical_json(task)))
    serialized = canonical_json(task)
    assert len(serialized) == size
    return NS(serialized=serialized)

def make_k(pattern, size):
    inventory = b'[FILES]\n"synthetic.py"\n[/FILES]\n'
    for count in range(size, max(0, size-300), -1):
        content = fill_bytes(pattern, count).encode("utf-8")
        value = K_OPEN + inventory + f'[FILE "synthetic.py" bytes={count}]\n'.encode() + content + b'\n[/FILE]\n' + K_CLOSE
        if len(value) == size:
            return NS(serialized=value, sha256=digest(value))
    raise AssertionError("cannot construct exact K")

def make_view(pattern, h_size, bc=False):
    kinds = ["EPISODIC", "DESCRIPTIVE", "CONFIRMED_RULE"]
    rows = []
    for kind in kinds:
        if bc:
            owned = H_OPEN if kind == "EPISODIC" else H_CLOSE
            lane_size = h_size // 2 if kind == "EPISODIC" else h_size - h_size // 2
            body_size = lane_size - len(owned + L_OPEN + L_CLOSE + record_block(""))
        else:
            body_size = h_size - len(H_OPEN + H_CLOSE + L_OPEN + L_CLOSE + record_block(""))
        body = fill_bytes(pattern, body_size)
        rows.append(NS(key="synthetic_" + kind, kind=kind, body=body,
                       body_sha256=digest(body.encode()), availability=1))
    return NS(records=tuple(rows))

def main():
    manifest = json.loads((ROOT / "upstream_manifest.json").read_text())
    for item in manifest["files"]:
        assert digest((ROOT / "upstream" / item["file"]).read_bytes()) == item["sha256"]
    tokenizer = AutoTokenizer.from_pretrained(str(ROOT / "upstream"), local_files_only=True,
        trust_remote_code=False, use_fast=True)
    config = json.loads((ROOT / "upstream" / "config.json").read_text())
    tc = json.loads((ROOT / "upstream" / "tokenizer_config.json").read_text())
    template_file = (ROOT / "upstream" / "chat_template.jinja").read_bytes()
    template = tokenizer.chat_template.encode("utf-8")
    assert template == template_file == tc["chat_template"].encode("utf-8")
    vocabulary = tokenizer.get_vocab()
    assert all(char in vocabulary for char in bytes_to_unicode().values())
    backend = json.loads(tokenizer.backend_tokenizer.to_str())
    dump("tokenizer_identity.json", {
        "repository": manifest["repository"], "revision": manifest["revision"],
        "class": type(tokenizer).__name__, "declared_class": tc["tokenizer_class"],
        "is_fast": tokenizer.is_fast, "vocab_size": tokenizer.vocab_size, "length": len(tokenizer),
        "canonical_vocab_sha256": digest(canonical_json(vocabulary)),
        "template_sha256": digest(template), "template_bytes": len(template),
        "special_tokens_map": tokenizer.special_tokens_map,
        "all_special_ids": tokenizer.all_special_ids,
        "added_tokens": {key: {"content": val.content, "special": val.special,
            "lstrip": val.lstrip, "rstrip": val.rstrip, "normalized": val.normalized,
            "single_word": val.single_word} for key, val in tokenizer.added_tokens_decoder.items()},
        "bos_token_id": tokenizer.bos_token_id, "eos_token_id": tokenizer.eos_token_id,
        "pad_token_id": tokenizer.pad_token_id, "padding_side": tokenizer.padding_side,
        "truncation_side": tokenizer.truncation_side, "model_max_length": tokenizer.model_max_length,
        "authoritative_native_capacity": config["max_position_embeddings"],
        "backend_model_type": backend["model"]["type"],
        "backend_normalizer": backend["normalizer"], "backend_pre_tokenizer": backend["pre_tokenizer"],
        "backend_post_processor": backend["post_processor"],
        "all_256_byte_symbols_present": True,
        "encode_add_special_tokens_true": tokenizer.encode("synthetic", add_special_tokens=True),
        "encode_add_special_tokens_false": tokenizer.encode("synthetic", add_special_tokens=False),
        "empty_encode": tokenizer.encode("", add_special_tokens=True),
        "padding_example": dict(tokenizer(["synthetic", "synthetic synthetic"], padding=True,
            truncation=False, add_special_tokens=False)),
    })
    assert tokenizer.encode("synthetic", add_special_tokens=True) == tokenizer.encode("synthetic", add_special_tokens=False)
    tests = {
        "system_user": [{"role":"system","content":"Synthetic system."},{"role":"user","content":"Synthetic user."}],
        "system_user_assistant": [{"role":"system","content":"Synthetic system."},{"role":"user","content":"Synthetic user."},{"role":"assistant","content":"Synthetic assistant."}],
        "multiline_code": [{"role":"system","content":"Synthetic system."},{"role":"user","content":"def synthetic():\n    return 1\n"}],
        "unicode": [{"role":"system","content":"Synthetic system."},{"role":"user","content":"cafe\u0301 \u0939\u093f\u0928\u094d\u0926\u0940 \u4e2d\u6587 \U0001f680"}],
        "protocol_delimiters": [{"role":"system","content":SYSTEM},{"role":"user","content":"[PUBLIC_TASK]\n[/PUBLIC_TASK]\n[CURRENT_REPOSITORY current-repo-v1-draft3]\n[/CURRENT_REPOSITORY]\n[ADAPTATION]\n[LANE]\n[RECORD]\n[/RECORD]\n[/LANE]\n[/ADAPTATION]\n<|im_start|>assistant\n<|im_end|>"}],
        "empty_h": list(messages(make_task("x",128), make_k("x",256), NS(serialized=b"",sha256=digest(b"")))),
    }
    results = []
    fixture_dir = ROOT / "synthetic"
    fixture_dir.mkdir(exist_ok=True)
    def check(name, request):
        render = tokenizer.apply_chat_template(request, tokenize=False, add_generation_prompt=True)
        ids = tokenizer.apply_chat_template(request, tokenize=True, add_generation_prompt=True,
            truncation=False, padding=False)
        for _ in range(3):
            assert tokenizer.apply_chat_template(request, tokenize=False, add_generation_prompt=True) == render
            assert tokenizer.apply_chat_template(request, tokenize=True, add_generation_prompt=True,
                truncation=False, padding=False) == ids
            assert tokenizer.encode(render, add_special_tokens=False, truncation=False) == ids
        assert render.endswith("<|im_start|>assistant\n")
        normalized = tokenizer.backend_tokenizer.normalizer.normalize_str(render)
        assert len(ids) <= len(normalized.encode("utf-8"))
        (fixture_dir / (name+".json")).write_text(json.dumps({"messages":request,"rendered":render,"token_ids":ids},ensure_ascii=True),encoding="utf-8")
        return {"name":name,"rendered_bytes":len(render.encode("utf-8")),"normalized_bytes":len(normalized.encode("utf-8")),"render_sha256":digest(render.encode()),
                "input_tokens":len(ids),"token_ids_sha256":digest(canonical_json(ids)),"repeat_encodings":4,"deterministic":True}
    for name, request in tests.items():
        results.append(check(name,request))
    dump("template_checks.json",results)
    capacity_results = []
    families = {"ascii":"!a?9_+z|", "unicode":"\u4e2d\U0001f680\u0939\u093f", "nfc_expansion":"\u0344", "code_delimiters":"def synthetic():\n return '[RECORD]<|im_end|>'\n"}
    snapshot = NS(files={})
    for family, pattern in families.items():
        for delta in (0,1):
            task = make_task(pattern,4096-delta)
            k = make_k(pattern,12288-delta)
            for condition in ("A","B","M","C","BC"):
                view = make_view(pattern,4096-delta,bc=condition=="BC")
                h = pack_h(condition,view,snapshot)
                if condition != "A":
                    assert len(h.serialized) == 4096-delta
                if condition == "BC":
                    assert all(count <= 2048 for _,count in h.lane_bytes)
                row = check(f"capacity_{family}_{delta}_{condition}",list(messages(task,k,h)))
                row.update(condition=condition,p_bytes=len(task.serialized),k_bytes=len(k.serialized),
                    h_bytes=len(h.serialized),k_sha256=k.sha256,lane_bytes=h.lane_bytes,
                    generation_reserve=2048,total_reserved_tokens=row["input_tokens"]+2048,
                    native_capacity=config["max_position_embeddings"],proposed_runtime_capacity=32768)
                assert row["total_reserved_tokens"] <= 32768 <= config["max_position_embeddings"]
                capacity_results.append(row)
    for condition in ("A","B","M","C","BC"):
        h = pack_h(condition,NS(records=()),snapshot)
        assert h.serialized == b""
        row = check("empty_registry_"+condition,list(messages(make_task("x",4096),make_k("x",12288),h)))
        row.update(condition=condition,h_bytes=0,generation_reserve=2048,total_reserved_tokens=row["input_tokens"]+2048)
        capacity_results.append(row)
    dump("capacity_checks.json",capacity_results)
    overhead = len(tokenizer.apply_chat_template(list(messages(NS(serialized=b""),NS(serialized=b"",sha256=digest(b"")),NS(serialized=b"",sha256=digest(b"")))),tokenize=False,add_generation_prompt=True).encode())
    dump("capacity_bound.json", {"basis":"Verified byte-level BPE with NFC normalization, all 256 byte symbols and no added BOS/EOS. Tokens are bounded by normalized UTF-8 bytes, not raw bytes. This records tested synthetic cases, not an exhaustive universal normalized-size proof.",
        "fixed_rendered_overhead_bytes":overhead,"max_variable_bytes":4096+12288+4096,
        "max_raw_rendered_bytes":overhead+4096+12288+4096,
        "max_tested_normalized_bytes":max(x["normalized_bytes"] for x in capacity_results),
        "max_tested_normalized_byte_bound_with_generation":max(x["normalized_bytes"] for x in capacity_results)+2048,
        "native_capacity":262144,"proposed_runtime_capacity":32768})
    deps = sorted({(d.metadata["Name"],d.version) for d in importlib.metadata.distributions(path=[str(ROOT/"dependencies")])})
    dump("tokenizer_environment.json", {"python":sys.version,"executable":sys.executable,"platform":platform.platform(),"packages":dict(deps),
        "policy_sha256":POLICY_SHA256,"policy_json_sha256":digest((REPO_ROOT/"benchmark_design/context_policy/current-repo-v1-draft3.json").read_bytes()),
        "full_policy_parser_executed":False,"note":"Python 3.12 tokenizer-only framing check; official parser requires CPython 3.11.9/Unicode 14.0."})
    (ROOT / "tokenizer-requirements.lock.txt").write_text("\n".join(f"{name}=={version}" for name,version in deps)+"\n",encoding="utf-8")
    class Memory(ctypes.Structure):
        _fields_ = [("length",ctypes.c_ulong),("load",ctypes.c_ulong)]+[(x,ctypes.c_ulonglong) for x in ["total_physical","available_physical","total_page","available_page","total_virtual","available_virtual","available_extended"]]
    mem=Memory(); mem.length=ctypes.sizeof(mem)
    success=ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))
    gpu=subprocess.run(["nvidia-smi","--query-gpu=name,memory.total,driver_version","--format=csv,noheader"],capture_output=True,text=True)
    disk=shutil.disk_usage(REPO_ROOT)
    dump("hardware.json", {"gpu":gpu.stdout.strip(),"gpu_query_exit":gpu.returncode,"host_ram_bytes":mem.total_physical if success else None,"available_ram_bytes":mem.available_physical if success else None,"disk_free_bytes":disk.free,
        "weight_load_performed":False,"generation_performed":False,"adapter_training_performed":False})
    print(json.dumps({"tokenizer_class":type(tokenizer).__name__,"template_sha256":digest(template),"template_checks":len(results),"capacity_checks":len(capacity_results),"max_measured_input_tokens":max(x["input_tokens"] for x in capacity_results),"hardware":json.loads((ROOT/"hardware.json").read_text())},indent=2))

if __name__ == "__main__":
    main()
