"""Extract the exact previously delivered R4AH package to a NEW directory.

Byte restoration only. No build, old test replay, authorization or native run.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,stat,zipfile,sys
EXPECTED='95f9c09b7c5108384d440c6fb21026d9dff03046194b27c58abeee3f18bb4119'
def unpack(archive,output):
    archive=Path(archive);output=Path(output)
    if not output.is_absolute() or output.exists():raise ValueError('absolute nonexisting runtime destination required')
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=EXPECTED:raise ValueError('R4AH archive identity mismatch')
    with zipfile.ZipFile(archive) as z:
        seen=set()
        for e in z.infolist():
            p=PurePosixPath(e.filename)
            if p.is_absolute() or '..' in p.parts or '\\' in e.filename or not e.filename or e.filename in seen:raise ValueError('unsafe or duplicate archive path')
            if stat.S_ISLNK(e.external_attr>>16):raise ValueError('archive symlink')
            seen.add(e.filename)
        if z.testzip() is not None:raise ValueError('CRC mismatch')
        output.mkdir(parents=True,exist_ok=False);z.extractall(output)
    return {'runtime_root':str(output),'archive_sha256':EXPECTED,'science_calls':0,'status':'LOCAL_BYTES_RESTORED_NOT_EXECUTED'}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[1]
    try:print(json.dumps(unpack(root/'legacy_runtime/BASS_CR_R4AH_RUNTIME_PREFLIGHT_PACKAGE_20261003_v1.zip',a.output)))
    except (ValueError,OSError,zipfile.BadZipFile) as e:print(str(e),file=sys.stderr);sys.exit(2)
