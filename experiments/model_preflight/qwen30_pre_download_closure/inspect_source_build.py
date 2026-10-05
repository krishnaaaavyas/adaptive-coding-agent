import json,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent
rows=[]
for name,files in [('cpython',['Include/patchlevel.h']),('transformers',['setup.py']),('peft',['setup.py']),('vllm',['cmake/external_projects/vllm_flash_attn.cmake','CMakeLists.txt'])]:
    with tarfile.open(P/'sources/archives'/f'{name}.tar.gz') as t:
        root=t.getmembers()[0].name.split('/')[0]
        for f in files:
            try: text=t.extractfile(root+'/'+f).read().decode('utf-8')
            except KeyError: continue
            rows.append({'source':name,'path':f,'text':text})
(P/'sources/source_build_declarations.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
for r in rows:
    print(r['source'],r['path'])
    for s in r['text'].splitlines():
        if any(k in s.lower() for k in ['fetchcontent','git_','url ','cutlass','src_dir','setup_requires','install_requires','version=','py_version','pip','ext_c','flash_attn']):print(s)
