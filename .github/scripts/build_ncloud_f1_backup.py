#!/usr/bin/env python3
import hashlib, json, os, shutil, subprocess, zipfile
from pathlib import Path

NAME="BASS_CR_NCLOUD_F1_DUAL_CHECKPOINT_20260928T073802Z"
repo=Path.cwd()
root=Path(os.environ["RUNNER_TEMP"])/NAME
pay=root/"payload"
pay.mkdir(parents=True,exist_ok=False)

def cp(rel):
    src=repo/rel
    if not src.exists():
        raise FileNotFoundError(rel)
    dst=pay/rel
    if src.is_dir():
        shutil.copytree(src,dst,dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)

for rel in [
    "research/foundation_rebuild/ncloud_c64g3_20260928",
    "research/foundation_rebuild/ncloud_f1_engine_admission_20260928",
    "docs/plans/2026-09-28-bass-ncloud-c64g3-codex.md",
    "docs/plans/2026-09-28-bass-ncloud-f1-engine-admission.md",
    "AGENTS.md",
    "docs/READBACK_POLICY.md",
]:
    cp(rel)

pins=json.loads((repo/"research/foundation_rebuild/ncloud_f1_engine_admission_20260928/SOURCE_PINS.json").read_text())
dep=pins["inherited_dependency_pins"]
cp(dep["path"])
depdoc=json.loads((repo/dep["path"]).read_text())
for row in depdoc.get("files",[]):
    cp(row["path"])
for row in pins.get("additional_pins",[]):
    cp(row["path"])

state={
    "schema":"BASS_CR_NCLOUD_F1_DUAL_CHECKPOINT_STATE_V1",
    "created_utc":"2026-09-28T07:38:02Z",
    "repository":"cosmosapjw-quantum/bass_cr",
    "source_control_branch":"research/fnd-ncloud-f1-engine-admission-20260928",
    "source_control_head":"7f2608e0f6fad516ec4e6d9a42a13d40f26e9d16",
    "source_control_tree":"8b60018a13befc1fabc99b0ac0619560d3d866a8",
    "frozen_f1_implementation_commit":"8236887dd8869de57522d5c87a48972f287969fe",
    "frozen_f1_implementation_tree":"d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae",
    "f0_status":"F0_DURABLE_CLOSED",
    "f0_scientific_status":"TP2E_CACHE_ONLY_M4_COMPARISON_PASS",
    "f1_status":"F1_RUN_AUTHORIZED_READY_PENDING_EXECUTION",
    "authorization":{"max_wall_seconds":7200,"spending_limit_krw":8000},
    "storage":{"class":"CB1","provisioned_gb":100,"block_device":"/dev/vda","observed_filesystem":"/dev/vda2 ext4"},
    "claim_ceiling":{"capture_execution_allowed":False,"production_admission":"HOLD","all_bound":"OPEN","b_grid":"NO_GO","original_capture_gap_resolved":False,"continuous_global_supremum_bound":False},
    "backup_scope":"NCP/F0/F1 sidecars, binary inputs/evidence, implementation receipts, authorization, and frozen scientific dependency closure"
}
(pay/"BACKUP_STATE.json").write_text(json.dumps(state,indent=2)+"\n")

(pay/"README_RESTORE.md").write_text("""# Restore notes

This checkpoint captures BASS CR NCloud F0/F1 source, evidence and control artifacts.

Control identity at packaging:
- branch: research/fnd-ncloud-f1-engine-admission-20260928
- HEAD: 7f2608e0f6fad516ec4e6d9a42a13d40f26e9d16
- tree: 8b60018a13befc1fabc99b0ac0619560d3d866a8

Frozen F1 implementation:
- commit: 8236887dd8869de57522d5c87a48972f287969fe
- tree: d114060c6dc6bdc1aa10fc6d9ffe9de19da99fae

Verify FILE_MANIFEST.json before use. This checkpoint does not imply that the authorized F1
scientific run has already executed and does not expand the preserved claim ceiling.
""")

rows={}
for p in sorted(pay.rglob("*")):
    if p.is_file():
        b=p.read_bytes()
        rows[str(p.relative_to(pay))]={"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
(pay/"FILE_MANIFEST.json").write_text(json.dumps({"schema":"BASS_CR_NCLOUD_F1_FILE_MANIFEST_V1","files":rows},indent=2)+"\n")

zip_path=root/f"{NAME}.zip"
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(pay.rglob("*")):
        if p.is_file():
            z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(zip_path) as z:
    bad=z.testzip()
    if bad is not None:
        raise RuntimeError("ZIP CRC failure: "+bad)
sha=hashlib.sha256(zip_path.read_bytes()).hexdigest()
bytes_=zip_path.stat().st_size
sha_path=root/f"{NAME}.zip.sha256"
sha_path.write_text(f"{sha}  {NAME}.zip\n")
receipt={
    "schema":"BASS_CR_NCLOUD_F1_BACKUP_ARTIFACT_V1",
    "file_name":zip_path.name,
    "bytes":bytes_,
    "sha256":sha,
    "payload_file_count":len(rows)+3,
    "source_control_head":state["source_control_head"],
    "source_control_tree":state["source_control_tree"],
    "zip_crc":"PASS"
}
(root/"BACKUP_ARTIFACT.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
