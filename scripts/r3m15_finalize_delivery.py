"""Bind actual provider receipts to the completed R3M15 data checkpoints."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REPO = ROOT/'worktree'
HELPER = '/mnt/sn850x2t/local_ai_foundry/60_runtime/cuhg/policy-authorities/4ba71de2ef3e5656f32e917bd8dfe6e2299598a3/scripts/codex_harness/verify_publication.py'
FOLDER = '1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI'

def read(path): return json.loads(path.read_text())
def write(path, value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def finish():
    stages=[]
    for stage in ['A','B','C','B_preparation_refinement']:
        archive=read(ROOT/f'ARCHIVE_{stage}.json')
        mp=ROOT/f'BASS_CR_R3M15_{stage}_20260922_v1_DRIVE_MANIFEST.json'
        manifest=read(mp)
        up=read(ROOT/f'receipts/{stage}-drive-manifest-upload.json')
        md=read(ROOT/f'receipts/{stage}-drive-manifest-metadata.json')
        u,m=up['structuredContent'],md['structuredContent']
        assert u['success'] and not up.get('isError') and not md.get('isError')
        assert m['id']==u['id'] and m['title']==mp.name and int(m['size'])==mp.stat().st_size
        assert FOLDER in m['parent_ids'] and manifest['archive']['sha256']==archive['sha256']
        parts=manifest['ordered_parts']; expected=read(ROOT/f'DRIVE_PARTS_{stage}.json')['ordered_parts']
        assert len(parts)==len(expected) and len({x['remote_id'] for x in parts})==len(parts)
        for p,e in zip(parts,expected):
            for key in ['index','name','bytes','sha256']:assert p[key]==e[key]
            assert p['remote_size']==e['bytes'] and p['upload_verified'] is True
        assert sum(p['remote_size'] for p in parts)==archive['bytes']
        entries=[{'path':p['name'],'size':p['bytes'],'sha256':p['sha256']} for p in parts]
        dest=FOLDER+'/'+mp.name
        request={'operation':'canonical_checkpoint','intent':{'provider':'GoogleDrive','destination':dest,'size':mp.stat().st_size,'sha256':sha(mp),'manifest':entries,'upload_set':[x['path'] for x in entries]},'provider_receipt':{'provider':'GoogleDrive','destination':dest,'success':True,'receipt_id':str(ROOT/f'receipts/{stage}-drive-manifest-metadata.json'),'object_id':m['id'],'size':int(m['size']),'sha256':None}}
        rp=ROOT/f'receipts/{stage}-GoogleDrive-verify-request.json';write(rp,request)
        vp=ROOT/f'receipts/{stage}-GoogleDrive-verified.json'
        with vp.open('x') as out:subprocess.run(['python',HELPER,'artifact','--request-json',str(rp)],stdout=out,check=True)
        assert read(vp)['status']=='UPLOAD_VERIFIED_R2'
        db=read(ROOT/f'receipts/{stage}-dropbox-final-verification.json')
        assert db['provider_content_hash_verified'] and read(ROOT/f'receipts/{stage}-Dropbox-verified.json')['status']=='UPLOAD_VERIFIED_R2'
        stages.append({'stage':stage,'archive':archive,'Dropbox':db,'GoogleDrive':{'status':'UPLOAD_VERIFIED_R2','layout':'ORDERED_MULTIPART','completed_parts':len(parts),'expected_parts':len(expected),'remote_manifest_id':m['id'],'remote_manifest_bytes':int(m['size']),'local_manifest_sha256':sha(mp),'remote_sha256':'UNAVAILABLE_FROM_ADAPTER','manifest_path':'results/R3M15/delivery/'+mp.name,'restore_status':'RESTORE_NOT_TESTED'},'dual_backup_status':'DUAL_UPLOAD_VERIFIED_R2'})
    delivery=REPO/'results/R3M15/delivery';delivery.mkdir(exist_ok=True)
    for p in ROOT.glob('BASS_CR_R3M15_*_DRIVE_MANIFEST.json'):shutil.copy2(p,delivery/p.name)
    shutil.copytree(ROOT/'backup_steps',delivery/'provider_parts',dirs_exist_ok=True)
    for pattern in ['*-verified.json','*-metadata.json','*-final-verification.json','TRANSPORT_RETRY.json','HOST_CLOSEOUT_REVIEW.json']:
        for p in (ROOT/'receipts').glob(pattern):shutil.copy2(p,delivery/p.name)
    result={'schema':'BASS_CR_R3M15_DELIVERY_RECEIPT_V1','work_unit':'R3M15_OBSERVABLE_GATE_RECONCILIATION_AND_CONTROLLED_SPATIAL_REFINEMENT','repository':'https://github.com/cosmosapjw-quantum/bass_cr','branch':'cr/r3m15-observable-spatial-20260922','parent_commit':'8c7bbfce157f17b85dc9082c62c63c05fef3b294','scientific_report_commit':'678777d5f898bd5afdac57ab5d2e70dab90b75bf','scientific_report_git_verification':'VERIFIED_R1','numerical_source_digest':'581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b','data_archives':stages,'data_archives_dual_backup':'COMPLETE_UPLOAD_VERIFIED_R2','checkpoint_kind':'CANONICAL_RESEARCH_CHECKPOINT_NOT_ATOMIC_DATASET_RELEASE','remote_content_readback':False,'restore_status':'RESTORE_NOT_TESTED','local_sources_retained':True,'local_root':str(ROOT),'final_report_checkpoint':'PENDING_CREATE_ONLY_PACKAGE_AFTER_THIS_COMMIT','transport_failure_and_recovery':read(ROOT/'receipts/TRANSPORT_RETRY.json'),'old_R3M14_backup':'UNCHANGED_COMPLETED_AS_PREVIOUSLY_RECORDED','old_R3M12_Drive':'UNCHANGED_1_OF_19_NOT_COMPLETE','main_mutation':False,'force_push':False,'bgrid_execution':False,'physical_rate_execution':False,'scientific_convergence':'NO_GO','next_canonical_node':'N1_TDL_COULOMB_FFT_H_DT_REPRESENTATION_DECISION','receipt_self_binding':'This receipt records prior scientific and provider identities. The final enclosing Git commit is supplied by branch publication, avoiding a self-referential commit hash.'}
    write(REPO/'docs/r3m15/DELIVERY_RECEIPT.json',result)
    print(json.dumps({'data_archives':len(stages),'status':result['data_archives_dual_backup']}))

if __name__=='__main__':finish()
