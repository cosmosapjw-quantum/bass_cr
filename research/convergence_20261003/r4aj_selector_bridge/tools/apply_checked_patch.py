"""Apply the supplied create-only patch on the exact, clean existing branch.

Does not commit, push, create a branch, force update, or bypass conflicts.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,subprocess,sys
BRANCH='research/r4q-gap-closure-20261001'
BASE='0d7bdbe76dc35d38668d750e6312919cecb09144'
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def verify_paths(repo,entries):
    repo=Path(repo).resolve();seen=set()
    for item in entries:
        name=item['path'];p=PurePosixPath(name)
        if not isinstance(name,str) or p.is_absolute() or '..' in p.parts or '\\' in name or name in seen:raise ValueError('unsafe or duplicate mapped path')
        if not name.startswith(('research/convergence_20261003/r4ai_local_pre_codex/','research/convergence_20261003/r4aj_selector_bridge/')):raise ValueError('unapproved publication prefix')
        seen.add(name);target=repo.joinpath(*p.parts)
        if target.exists() or target.is_symlink():raise ValueError('create-only target already exists: '+name)
        if not target.resolve().is_relative_to(repo):raise ValueError('symlink escape')
    return len(seen)
def apply(repo,patch,manifest,commit_requested=False):
    repo=Path(repo).resolve();patch=Path(patch).resolve();m=json.loads(Path(manifest).read_text())
    if m['expected_parent']!=BASE or m['branch']!=BRANCH:raise ValueError('publication contract mismatch')
    if git(repo,'branch','--show-current')!=BRANCH or git(repo,'rev-parse','HEAD')!=BASE:raise ValueError('branch advanced or wrong branch; review actual diff and create a new publication contract')
    if git(repo,'status','--porcelain','--untracked-files=all'):raise ValueError('working tree/index not clean')
    if hashlib.sha256(patch.read_bytes()).hexdigest()!=m['patch_sha256']:raise ValueError('patch hash mismatch')
    n=verify_paths(repo,m['files'])
    subprocess.run(['git','-C',str(repo),'apply','--check','--index',str(patch)],check=True)
    subprocess.run(['git','-C',str(repo),'apply','--index',str(patch)],check=True)
    for e in m['files']:
        if hashlib.sha256((repo/e['path']).read_bytes()).hexdigest()!=e['sha256']:raise ValueError('applied bytes mismatch; do not commit')
        data=subprocess.check_output(['git','-C',str(repo),'show',':'+e['path']])
        if hashlib.sha256(data).hexdigest()!=e['sha256']:raise ValueError('index bytes mismatch; do not commit')
    return {'status':'PATCH_STAGED_BYTES_VERIFIED_NOT_COMMITTED','files':n,'base':BASE,'new_branch':False,'push':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);p.add_argument('--patch',required=True);p.add_argument('--manifest',required=True)
    a=p.parse_args()
    try:print(json.dumps(apply(a.repo,a.patch,a.manifest)))
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as e:print(str(e),file=sys.stderr);sys.exit(2)
