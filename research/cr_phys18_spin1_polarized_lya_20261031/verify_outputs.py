import hashlib,json,argparse
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=P);a=ap.parse_args()
j=json.loads((P/'EXPECTED_OUTPUT_SHA256.json').read_text())['members']
for f,meta in j.items():
 b=(a.root/f).read_bytes()
 assert len(b)==meta['bytes'],('SIZE',f,len(b),meta['bytes'])
 assert hashlib.sha256(b).hexdigest()==meta['sha256'],('HASH',f)
print('BYTE_EXACT',len(j),'/',len(j))
