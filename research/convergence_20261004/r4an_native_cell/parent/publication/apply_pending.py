"""Apply only the pinned, still-missing create-only patch to the exact branch.

Never fetch, commit, push, reset, overwrite, or execute scientific code.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path, PurePosixPath

def git(root,*args):
    return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True).stdout

def main():
    p=argparse.ArgumentParser();p.add_argument('--repository',required=True);p.add_argument('--manifest',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    root=Path(a.repository).resolve();mp=Path(a.manifest).resolve();m=json.loads(mp.read_text())
    if git(root,'rev-parse','HEAD').decode().strip()!=m['expected_parent']:raise SystemExit('HEAD changed; review actual diff before a new contract')
    if git(root,'branch','--show-current').decode().strip()!=m['branch']:raise SystemExit('wrong branch')
    if git(root,'status','--porcelain').strip():raise SystemExit('working tree/index must be clean')
    patch=(mp.parent/m['patch_name']).resolve()
    if not patch.is_relative_to(mp.parent) or hashlib.sha256(patch.read_bytes()).hexdigest()!=m['patch_sha256']:raise SystemExit('patch identity mismatch')
    def path(rel):
        pp=PurePosixPath(rel)
        if pp.is_absolute() or '..' in pp.parts or '\\' in rel:raise SystemExit('unsafe path')
        target=root.joinpath(*pp.parts)
        if not target.resolve().is_relative_to(root):raise SystemExit('path escape')
        if any(x.is_symlink() for x in (target,*target.parents) if x!=root and x.is_relative_to(root)):raise SystemExit('symlink payload')
        return target
    for e in m['already_published']:
        q=path(e['path'])
        if not q.is_file() or hashlib.sha256(q.read_bytes()).hexdigest()!=e['sha256']:raise SystemExit('published source mismatch: '+e['path'])
    for e in m['files']:
        if path(e['path']).exists():raise SystemExit('create-only target already exists: '+e['path'])
    git(root,'apply','--check','--index',str(patch))
    if a.apply:
        git(root,'apply','--index',str(patch))
        for e in m['files']:
            q=path(e['path']);b=q.read_bytes();idx=git(root,'show',':'+e['path'])
            if len(b)!=e['bytes'] or hashlib.sha256(b).hexdigest()!=e['sha256'] or idx!=b:raise SystemExit('post-apply identity mismatch: '+e['path'])
    print(json.dumps({'check':True,'applied':a.apply,'files':len(m['files']),'commit_created':False,'pushed':False,'science_calls':0}))
if __name__=='__main__':main()
