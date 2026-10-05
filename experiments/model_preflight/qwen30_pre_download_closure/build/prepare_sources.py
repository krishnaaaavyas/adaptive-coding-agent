"""Offline safe extraction and separate gitlink placement; no git/tag/network fetch."""
import hashlib,json,tarfile
from pathlib import Path
P=Path('/opt/qwen-bundle');ROOT=Path('/opt/build-sources');ROOT.mkdir(exist_ok=False)
rows=json.loads((P/'source_archive_lock.json').read_text(encoding='utf-8'))['sources']
rows+=[dict(next(r for r in json.loads((P/'extra_inputs_lock.json').read_text(encoding='utf-8'))['flash_attention_gitlinks'] if r['selected']),name='flash-attention-cutlass')]
for r in rows:
    archive=P/'archives'/Path(r['path']).name
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=r['sha256']:raise RuntimeError('Source input hash mismatch')
    if r['name']=='cpython':continue
    dest=ROOT/r['name'];dest.mkdir()
    with tarfile.open(archive) as t:
        for member in t:
            # Strip only the archive's one top-level directory; data filter blocks traversal/unsafe links.
            parts=Path(member.name).parts
            if len(parts)==1:continue
            member.name=Path(*parts[1:]).as_posix()
            t.extract(member,path=dest,filter='data')
fa=ROOT/'vllm-flash-attention/csrc/cutlass'
if fa.exists() and any(fa.iterdir()):raise RuntimeError('Unexpected gitlink contents')
if fa.exists():fa.rmdir()
(ROOT/'flash-attention-cutlass').rename(fa)
