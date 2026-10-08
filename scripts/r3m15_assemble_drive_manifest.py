"""Assemble completed multipart receipts, without reading remote file bodies."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FOLDER = '1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI'

def load(path):
    return json.loads(path.read_text())

def assemble(stage):
    source = load(ROOT / f'DRIVE_PARTS_{stage}.json')
    rows = []
    for expected in source['ordered_parts']:
        stem = ROOT / 'backup_steps' / stage / f"part{expected['index']:03d}"
        prefix = str(stem) + ('.retry1' if Path(str(stem)+'.retry1.upload.json').exists() else '')
        up = load(Path(prefix+'.upload.json'))
        md = load(Path(prefix+'.metadata.json'))
        u, m = up['structuredContent'], md['structuredContent']
        assert not up.get('isError') and u['success'] is True
        assert not md.get('isError') and m['id'] == u['id']
        assert m['title'] == expected['name'] and int(m['size']) == expected['bytes']
        assert FOLDER in m['parent_ids']
        rows.append(dict(expected, remote_id=u['id'], remote_url=u['url'],
                         remote_size=int(m['size']), remote_sha256=None,
                         upload_verified=True, raw_readback_performed=False,
                         upload_receipt=str(Path(prefix+'.upload.json').relative_to(ROOT)),
                         metadata_receipt=str(Path(prefix+'.metadata.json').relative_to(ROOT))))
    assert len({x['remote_id'] for x in rows}) == len(rows)
    assert [x['index'] for x in rows] == list(range(1,len(rows)+1))
    assert sum(x['remote_size'] for x in rows) == source['archive']['bytes']
    result = dict(schema='R3M15_DRIVE_MULTIPART_MANIFEST_V1', stage=stage,
                  archive=source['archive'], ordered_parts=rows, verification_tier='R2',
                  status=f'ALL_{len(rows)}_PARTS_UPLOAD_VERIFIED',
                  restore_status='RESTORE_NOT_TESTED',
                  restore_instructions='Download listed IDs, concatenate ordered bytes, verify archive size and SHA256, decompress and verify contained MANIFEST.json. No remote content restoration was executed.')
    destination = ROOT / f'BASS_CR_R3M15_{stage}_20260922_v1_DRIVE_MANIFEST.json'
    with destination.open('x') as out:
        out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'stage':stage,'parts':len(rows),'manifest':str(destination)}))

if __name__ == '__main__':
    assemble(sys.argv[1])
