#!/usr/bin/env python3
"""Restore PHYS23 full science ZIP from nine binary files tracked by Git."""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,argparse
EXPECTED="22d97f477199e71e2250b83ceb8fb10914457c343125456d981c0f9f34024111"
SIZE=3813848
ROOT=Path(__file__).resolve().parent
def run(destination):
 parts=sorted((ROOT/"zip_parts").glob("PHYS23_FULL.zip.part*"))
 if len(parts)!=9 or any(p.name!=f"PHYS23_FULL.zip.part{i:03d}" for i,p in enumerate(parts)):
  raise ValueError("NINE_CONSECUTIVE_PARTS_REQUIRED")
 if destination.resolve() in {p.resolve() for p in parts}:raise ValueError("OVERWRITE_SOURCE_FORBIDDEN")
 destination.parent.mkdir(parents=True,exist_ok=True)
 with destination.open("wb") as out:
  for p in parts:out.write(p.read_bytes())
 data=destination.read_bytes()
 if len(data)!=SIZE or hashlib.sha256(data).hexdigest()!=EXPECTED:raise ValueError("ZIP_SHA256_MISMATCH")
 with ZipFile(destination) as z:
  if z.testzip() is not None:raise ValueError("ZIP_CRC_FAILURE")
  manifest=json.loads(z.read("MANIFEST_SHA256.json"))
  if len(manifest["members"])!=43:raise ValueError("MANIFEST_COUNT")
  for item in manifest["members"]:
   b=z.read(item["name"])
   if hashlib.sha256(b).hexdigest()!=item["sha256"] or len(b)!=item["size_bytes"]:
    raise ValueError("ZIP_MEMBER_IDENTITY:"+item["name"])
 print(json.dumps({"restored":True,"size_bytes":len(data),"sha256":EXPECTED,"zip_members":44,"output":str(destination)}))
if __name__=="__main__":
 ap=argparse.ArgumentParser()
 ap.add_argument("--output",type=Path,default=ROOT/"PHYS23_FULL_RESTORED.zip")
 run(ap.parse_args().output)
