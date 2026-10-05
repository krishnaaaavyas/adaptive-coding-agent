"""Archive versioned first-party implementation evidence only."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "vllm_sampling_params.py": "vllm-project/vllm/v0.11.2/vllm/sampling_params.py",
    "vllm_processor.py": "vllm-project/vllm/v0.11.2/vllm/v1/engine/processor.py",
    "vllm_output.py": "vllm-project/vllm/v0.11.2/vllm/v1/engine/output_processor.py",
    "vllm_stop.py": "vllm-project/vllm/v0.11.2/vllm/v1/core/sched/utils.py",
    "vllm_requirements_cuda.txt": "vllm-project/vllm/v0.11.2/requirements/cuda.txt",
    "vllm_requirements_common.txt": "vllm-project/vllm/v0.11.2/requirements/common.txt",
    "vllm_qwen3_moe.py": "vllm-project/vllm/v0.11.2/vllm/model_executor/models/qwen3_moe.py",
    "vllm_arg_utils.py": "vllm-project/vllm/v0.11.2/vllm/engine/arg_utils.py",
    "transformers_qwen3_moe.py": "huggingface/transformers/v4.57.6/src/transformers/models/qwen3_moe/modeling_qwen3_moe.py",
    "peft_lora.md": "huggingface/peft/v0.18.0/docs/source/developer_guides/lora.md",
    "peft_quantization.md": "huggingface/peft/v0.18.0/docs/source/developer_guides/quantization.md",
    "peft_checkpoint.md": "huggingface/peft/v0.18.0/docs/source/developer_guides/checkpoint.md",
    "peft_mapping.py": "huggingface/peft/v0.18.0/src/peft/utils/constants.py",
}

def main():
    folder = ROOT / "sources"
    folder.mkdir(exist_ok=True)
    manifest = []
    for name, suffix in SOURCES.items():
        url = "https://raw.githubusercontent.com/" + suffix
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
            (folder / name).write_bytes(data)
            manifest.append({"file": name, "url": url, "bytes": len(data),
                             "sha256": hashlib.sha256(data).hexdigest()})
        except Exception as error:
            manifest.append({"file": name, "url": url, "error": str(error)})
    (ROOT / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
