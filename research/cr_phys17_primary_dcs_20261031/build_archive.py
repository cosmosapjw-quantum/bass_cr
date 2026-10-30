#!/usr/bin/env python3
"""Deterministic content manifest and single archive. Upstream binary is nested exactly once.
Original user-provided Kingston/Williams PDFs are NOT included/reposted, only PDF digests.
"""
import json,zipfile,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PREFIX='research/cr_phys17_primary_dcs_20261031/'
EXCLUDED={'sources/PR140_PHYS15_SOURCE.zip','sources/PHYS16_SOURCE_EMISSION_PROFILES.npz','sources/PHYS16_SOURCE_RECOIL_MODEL_CROSSWALK.csv'}

def build(target):
 target=Path(target)
 files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith(('.pyc','.log')) and p.relative_to(ROOT).as_posix() not in EXCLUDED)
 m=[]
 with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for p in files:
   rel=p.relative_to(ROOT).as_posix();b=p.read_bytes();m.append(dict(path=rel,size=len(b),sha256=hashlib.sha256(b).hexdigest()))
   info=zipfile.ZipInfo(PREFIX+rel,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
   z.writestr(info,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=7)
  b=(json.dumps(dict(members=m,unit='PHYS17_ORIGINAL_1976_DCS_CONDITIONAL',original_pdf_binaries_included=False),sort_keys=True,indent=2)+'\n').encode()
  info=zipfile.ZipInfo('SOURCE_MANIFEST.json',date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
 print('ARCHIVE_CREATED',target,'bytes',target.stat().st_size,'member_count',len(m),'sha256',hashlib.sha256(target.read_bytes()).hexdigest())

if __name__=='__main__':build(sys.argv[1])
