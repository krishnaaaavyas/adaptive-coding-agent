import json, sys, tarfile, io
from pathlib import Path
from fetch_evidence import fetch, dump, sha, ROOT
def main():
    pins=json.loads((ROOT/'implementation_pins.json').read_text())
    manifest=json.loads((ROOT/'source_manifest.json').read_text())
    paths={'harmony':['src/tiktoken_ext.rs','src/load.rs','src/chat.rs','Cargo.lock'], 'gpt_oss':['gpt_oss/generate.py'], 'cookbook':[]}
    tree=json.loads(fetch(f'https://api.github.com/repos/openai/openai-cookbook/git/trees/{pins["cookbook"]["revision"]}?recursive=1'))
    paths['cookbook']=[x['path'] for x in tree['tree'] if 'gpt-oss' in x['path'] and ('fine' in x['path'] or 'train' in x['path']) and x['path'].endswith(('.md','.ipynb'))]
    for key,items in paths.items():
        for path in items:
            p=pins[key]; url=f'https://raw.githubusercontent.com/{p["repository"]}/{p["revision"]}/{path}'; name='sources/'+key+'_'+path.replace('/','_')
            try:
                b=fetch(url); (ROOT/name).write_bytes(b); manifest.append(dict(file=name,url=url,bytes=len(b),sha256=sha(b)))
            except Exception as e: manifest.append(dict(file=name,url=url,error=str(e)))
    # Published sdist includes a cargo source identity when provided; archive without executing it.
    meta=json.loads((ROOT/'harmony_pypi.json').read_text())
    for item in meta['urls']:
        if item['filename'].endswith('.tar.gz') or item['filename'].endswith('win_amd64.whl'):
            b=fetch(item['url']); assert sha(b)==item['digests']['sha256']
            (ROOT/'sources'/item['filename']).write_bytes(b)
            manifest.append(dict(file='sources/'+item['filename'],url=item['url'],bytes=len(b),sha256=sha(b)))
            if item['filename'].endswith('.tar.gz'):
                with tarfile.open(fileobj=io.BytesIO(b)) as tar:
                    for member in tar.getmembers():
                        if member.name.endswith('.cargo_vcs_info.json'):
                            dump('harmony_distribution_source_identity.json',json.loads(tar.extractfile(member).read()))
    dump('source_manifest.json',manifest)
    cache=ROOT/'encoding_cache';cache.mkdir(exist_ok=True)
    url='https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken'
    b=fetch(url);assert sha(b)=='446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d'
    import hashlib
    name=hashlib.sha1(url.encode()).hexdigest();(cache/name).write_bytes(b)
    dump('encoding_data_manifest.json',dict(file='encoding_cache/'+name,url=url,bytes=len(b),sha256=sha(b),pinned_by='official Harmony 0.0.8 encoding source expected_hash'))
    print(json.dumps(dict(training_sources=paths['cookbook'],errors=[x for x in manifest if 'error' in x]),indent=2))
if __name__=='__main__':main()
