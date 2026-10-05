"""Public code tree metadata only; never a model-host endpoint."""
import hashlib, json, tarfile, urllib.request
from pathlib import Path
P = Path(__file__).resolve().parent
def get(url, name):
    p = P / 'sources' / name
    if not p.exists():
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Qwen30-runtime-preparation'}), timeout=90) as r:
            data = r.read(100000001)
        assert len(data) <= 100000000
        p.write_bytes(data)
    return p.read_bytes()
def main():
    url='https://api.github.com/repos/vllm-project/flash-attention/git/trees/58e0626a692f09241182582659e3bf8f16472659?recursive=1'
    tree=json.loads(get(url,'flash-attention-tree.json'))
    links=[r for r in tree['tree'] if r['type']=='commit']
    rows=[]
    for r in links:
        if r['path']!='csrc/cutlass':
            rows.append(dict(r, selected=False, reason='ROCm composable_kernel not used by frozen CUDA build'))
            continue
        commit=r['sha']; u=f'https://codeload.github.com/NVIDIA/cutlass/tar.gz/{commit}'
        data=get(u,'archives/flash-attention-cutlass.tar.gz')
        rows.append(dict(r,selected=True,url=u,path='sources/archives/flash-attention-cutlass.tar.gz',bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    release=json.loads(get('https://api.github.com/repos/flashinfer-ai/flashinfer/releases/tags/v0.5.2','flashinfer-release-v0.5.2.json'))
    assets=[a for a in release['assets'] if a['name']=='flashinfer_jit_cache-0.5.2+cu128-cp39-abi3-manylinux_2_28_x86_64.whl']
    assert len(assets)==1
    a=assets[0]
    # No wheel body acquired here. Metadata inside cache is still a target collector obligation.
    artifact={'name':'flashinfer-jit-cache','version':'0.5.2+cu128','filename':a['name'],'url':a['browser_download_url'],'bytes':a['size'],'sha256':'8e8afa03ca179581ff13cd0d59db1048fc3610103962d9bf13f628acfe026c35','body_downloaded':False,'body_hash_verified':False,'metadata_requires_dist':'PENDING_WHEEL_METADATA_VERIFICATION'}
    (P/'extra_inputs_lock.json').write_text(json.dumps({'flash_attention_gitlinks':rows,'flashinfer_jit_cache':artifact,'tree_source_url':url},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'gitlinks':rows,'flashinfer_jit_cache':artifact}))
if __name__=='__main__': main()
