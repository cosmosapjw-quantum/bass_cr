"""Verify all staged ZIP/member bytes against original manifest before execution."""
import argparse,hashlib,json,zipfile
from pathlib import Path

def check(stage,manifest):
    spec=json.loads(manifest.read_text());count=0
    for row in spec['packages']:
        p=stage/'inputs'/row['name']
        assert p.stat().st_size==row['size'],('SIZE',row['name'])
        assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],('HASH',row['name'])
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            root=stage/'extracted'/row['name'].removesuffix('.zip')
            for member in z.infolist():
                if member.is_dir():continue
                assert (root/member.filename).read_bytes()==z.read(member),('MEMBER_BYTES',member.filename)
                count+=1
    print('VERIFIED_ZIPS',len(spec['packages']),'EXACT_EXTRACTED_MEMBERS',count)
    return count

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--stage',type=Path,required=True);a.add_argument('--manifest',type=Path,required=True)
    x=a.parse_args();check(x.stage,x.manifest)
