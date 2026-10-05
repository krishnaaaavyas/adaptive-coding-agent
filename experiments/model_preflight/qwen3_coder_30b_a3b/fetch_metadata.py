"""Candidate-blind metadata acquisition; explicit allowlist, never weight bodies."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
REPO = "Qwen/Qwen3-Coder-30B-A3B-Instruct"
REV = "b2cff646eb4bb1d68355c01b18ae02e7cf42d120"

def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()

def main():
    upstream = ROOT / "upstream"
    upstream.mkdir(exist_ok=True)
    metadata = fetch(f"https://huggingface.co/api/models/{REPO}/revision/{REV}?blobs=true")
    info = json.loads(metadata)
    assert info["sha"] == REV
    (upstream / "hub_metadata.json").write_bytes(metadata)
    names = ["config.json", "generation_config.json", "tokenizer_config.json", "tokenizer.json",
             "vocab.json", "merges.txt", "chat_template.jinja", "LICENSE", "README.md",
             "model.safetensors.index.json"]
    manifest = []
    for name in names:
        data = fetch(f"https://huggingface.co/{REPO}/resolve/{REV}/{name}")
        (upstream / name).write_bytes(data)
        manifest.append({"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                         "url": f"https://huggingface.co/{REPO}/resolve/{REV}/{name}"})
    (ROOT / "upstream_manifest.json").write_text(json.dumps({"repository": REPO, "revision": REV,
        "files": manifest}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"revision": REV, "download_bytes": sum(x["bytes"] for x in manifest),
                      "files": len(manifest), "weight_bodies_downloaded": False}))

if __name__ == "__main__":
    main()
