"""Render one repaired PDF through stdout and persist the verified image bytes."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--worker',required=True,type=Path);p.add_argument('--cpu',required=True,type=int)
a=p.parse_args();os.sched_setaffinity(0,{a.cpu})
source=ROOT/'runs/c23c_pdf_transport_repair_20261023_v3/cutoff_source_90mm.pdf'
b=source.read_bytes()
assert len(b)==22729 and hashlib.sha256(b).hexdigest()=='2e59921bcac6bda9aa8fe25cc1cdb5eaada720913c3c037d5ab4266c5d78c2ab'
out=subprocess.run(['pdftoppm','-singlefile','-scale-to','1600','-png',str(source)],capture_output=True,check=True,timeout=30).stdout
with Image.open(io.BytesIO(out)) as im:im.verify()
target=a.worker/'cutoff_source_90mm_pdf_render.png'
with target.open('xb') as f:f.write(out);f.flush();os.fsync(f.fileno())
assert target.read_bytes()==out
summary={'status':'PDF_RASTER_BYTES_PASS_AWAITING_VISUAL_READ','source':str(source.relative_to(ROOT)),
 'source_sha256':hashlib.sha256(b).hexdigest(),'render_bytes':len(out),'render_sha256':hashlib.sha256(out).hexdigest(),
 'worker_cpu':a.cpu,'new_science_evaluations':0,'new_ODE':0}
with (a.worker/'SUMMARY.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps(summary))
