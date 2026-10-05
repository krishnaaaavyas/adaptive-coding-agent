"""Bounded ranges of a runtime wheel only; no complete package or model body."""
import hashlib, json, struct, urllib.request, zlib
from pathlib import Path
P=Path(__file__).resolve().parent
def span(url,start,end):
    request=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}','User-Agent':'runtime-metadata-audit'})
    with urllib.request.urlopen(request,timeout=60) as r:
        if r.status!=206 or r.headers.get('Content-Range','').split('/')[0]!=f'bytes {start}-{end}':
            raise RuntimeError('Range not honored; refuse whole wheel transfer')
        data=r.read(end-start+2)
    assert len(data)==end-start+1
    return data
def main():
    p=P/'extra_inputs_lock.json'; d=json.loads(p.read_text(encoding='utf-8')); a=d['flashinfer_jit_cache']; n=a['bytes']
    data=span(a['url'],n-65536,n-1); i=data.rfind(b'PK\x05\x06'); e=struct.unpack_from('<4s4H2IH',data,i)
    size,offset=e[5:7]; central=span(a['url'],offset,offset+size-1)
    pos=0; entries=[]
    while pos<len(central):
        v=struct.unpack_from('<4s6H3I5H2I',central,pos); assert v[0]==b'PK\x01\x02'
        name=central[pos+46:pos+46+v[10]].decode('utf-8'); entries.append((name,v[4],v[8],v[9],v[16])); pos+=46+v[10]+v[11]+v[12]
    name,method,compressed,uncompressed,local=next(x for x in entries if x[0].endswith('.dist-info/METADATA'))
    header=span(a['url'],local,local+29); h=struct.unpack('<4s5H3I2H',header); assert h[0]==b'PK\x03\x04'
    start=local+30+h[9]+h[10]; raw=span(a['url'],start,start+compressed-1)
    metadata=zlib.decompress(raw,-15) if method==8 else raw; assert len(metadata)==uncompressed
    (P/'sources/flashinfer-jit-cache-METADATA.txt').write_bytes(metadata)
    requirements=[s.split(': ',1)[1] for s in metadata.decode('utf-8').splitlines() if s.startswith('Requires-Dist: ')]
    a.update(metadata_requires_dist=requirements,metadata_path='sources/flashinfer-jit-cache-METADATA.txt',metadata_sha256=hashlib.sha256(metadata).hexdigest(),metadata_authentication='RANGE_READ_ONLY; full pinned wheel digest verification still required',range_metadata_read=True)
    p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'requires_dist':requirements,'metadata_bytes':len(metadata),'complete_wheel_downloaded':False}))
if __name__=='__main__': main()
