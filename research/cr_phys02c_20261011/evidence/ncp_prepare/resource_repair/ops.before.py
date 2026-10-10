#!/usr/bin/env python3
"""Standard-library operational helpers; no numerical import or transport."""
import os
for _k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS'):
    os.environ[_k]='1'
import argparse, hashlib, json, pathlib, shutil, sys, time, uuid, zipfile
GIB=1024**3

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def read(p):
    try:return pathlib.Path(p).read_text().strip()
    except OSError:return None

def probe(root):
    mem={}
    for line in (read('/proc/meminfo') or '').splitlines():
        k,v=line.split(':',1);mem[k]=int(v.strip().split()[0])*1024
    cgroup={p:read('/sys/fs/cgroup/'+p) for p in ('cpu.max','cpuset.cpus.effective','memory.max','memory.current')}
    # Resolve the current process's delegated cgroup, when the mount is not namespace-rooted.
    for line in (read('/proc/self/cgroup') or '').splitlines():
        if line.startswith('0::'):
            base=pathlib.Path('/sys/fs/cgroup')/line[3:].lstrip('/')
            for p in cgroup:
                value=read(base/p)
                if value is not None:cgroup[p]=value
    limit=cgroup['memory.max']; current=cgroup['memory.current']
    bounded=min(mem.get('MemTotal',0),int(limit)) if limit and limit!='max' else mem.get('MemTotal',0)
    remaining=bounded-int(current) if current and limit and limit!='max' else mem.get('MemAvailable',0)
    available=min(mem.get('MemAvailable',0),remaining)
    reserve=max(int(bounded*.125),GIB)
    working=max(0,available-reserve)
    status=read('/proc/self/status') or ''
    rss=next((x.split(':',1)[1].strip() for x in status.splitlines() if x.startswith('VmRSS:')),None)
    topology=[]
    for cpu in sorted(os.sched_getaffinity(0)):
        base=f'/sys/devices/system/cpu/cpu{cpu}/topology/'
        topology.append({'cpu':cpu,'core_id':read(base+'core_id'),'package_id':read(base+'physical_package_id')})
    quota=cgroup['cpu.max']; quota_cpu=None
    if quota and quota.split()[0]!='max':quota_cpu=int(quota.split()[0])/int(quota.split()[1])
    live=0
    for p in pathlib.Path('/proc').iterdir():
        if p.name.isdigit():
            st=read(p/'status') or ''
            if '\nUid:\t'+str(os.getuid())+'\t' in st:live+=1
    return {'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'affinity_cpus':sorted(os.sched_getaffinity(0)), 'cpu_quota':quota_cpu,'cgroup':cgroup,'topology':topology,'load_average':os.getloadavg(),'same_uid_process_count_no_commandlines':live,'coordinator_pid':os.getpid(),'coordinator_RSS':rss,'memory_host_bytes':mem,'bounded_memory_bytes':bounded,'available_before_reserve_bytes':available,'reserve_bytes':reserve,'available_working_bytes':working,'estimated_peak_bytes':8*GIB,'minimum_working_bytes':12*GIB,'free_disk_bytes':shutil.disk_usage(root).free,'admitted':working>=12*GIB and shutil.disk_usage(root).free>=8*GIB and bool(os.sched_getaffinity(0)) and (quota_cpu is None or quota_cpu>=1),'thread_environment':{k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS')}}

def entries(manifest):
    data=manifest.get('files',manifest.get('entries',manifest.get('payload')))
    if isinstance(data,dict):return list(data.items())
    if isinstance(data,list):return [(x.get('path',x.get('name')),x) for x in data]
    raise ValueError('Manifest has no supported files/entries/payload collection')

def verify(root,manifest):
    root=pathlib.Path(root).resolve(); failures=[]; count=0;seen=set()
    for name,item in entries(json.loads(pathlib.Path(manifest).read_text())):
        if not isinstance(name,str):raise ValueError('Missing path')
        rel=pathlib.PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or name in seen:raise ValueError('Unsafe or duplicate path: '+name)
        seen.add(name);p=root.joinpath(*rel.parts)
        if not p.resolve().is_relative_to(root) or p.is_symlink():raise ValueError('Escaping/symlink entry: '+name)
        expected=item.get('bytes',item.get('size')); digest=item.get('sha256')
        if not isinstance(expected,int) or not isinstance(digest,str):raise ValueError('Incomplete identity: '+name)
        if not p.is_file() or p.stat().st_size!=expected or sha(p)!=digest:failures.append(name)
        count+=1
    if failures:raise ValueError('Manifest verification FAILED; do not trust any partial success: '+repr(failures))
    return {'verified_entries':count,'manifest_sha256':sha(manifest),'tier':'R3_ACTUAL_LOCAL_PAYLOAD_HASH_VERIFICATION'}

def extract(archive,dest,external=None):
    archive=pathlib.Path(archive);dest=pathlib.Path(dest)
    if external and sha(archive)!=external:raise ValueError('External archive SHA256 mismatch')
    if dest.exists():raise ValueError('Extraction destination must be new; preserve dirty work')
    with zipfile.ZipFile(archive) as z:
        seen=set()
        for i in z.infolist():
            n=pathlib.PurePosixPath(i.filename)
            if n.is_absolute() or '..' in n.parts or '\\' in i.filename or i.filename in seen or (i.external_attr>>16)&0o170000==0o120000:raise ValueError('Unsafe ZIP member')
            seen.add(i.filename)
        if 'BUNDLE_MANIFEST.json' not in seen:raise ValueError('Archive-root BUNDLE_MANIFEST.json required')
        dest.mkdir(parents=True);z.extractall(dest)
    return verify(dest,dest/'BUNDLE_MANIFEST.json')

def collect(study,run,out):
    study=pathlib.Path(study).resolve();run=pathlib.Path(run).resolve();out=pathlib.Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    if out.is_relative_to(run):raise ValueError('Return output must be outside run directory')
    dest=out/('CR_PHYS02C_NCP_RETURN_'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'_'+uuid.uuid4().hex[:12]+'.zip')
    payload={}
    for base,prefix in ((run,'run'),(study/'ncp','ncp'),(study/'state','state')):
        if not base.exists():continue
        for p in sorted(base.rglob('*')):
            if p.is_file() and not p.is_symlink():payload[prefix+'/'+p.relative_to(base).as_posix()]=p
    manifest={'schema':'cr-phys02c-ncp-return.v1','collection_status':'COLLECTED_ACTUAL_FILES_NO_FAILURE_SUPPRESSION','files':{n:{'bytes':p.stat().st_size,'sha256':sha(p)} for n,p in payload.items()}}
    with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED) as z:
        for n,p in payload.items():z.write(p,n)
        z.writestr('RETURN_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    return {'path':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'scientific_status':'INDEPENDENT_ASTRA_REVIEW_REQUIRED'}

if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    a=s.add_parser('probe');a.add_argument('--root',default='.')
    a=s.add_parser('verify');a.add_argument('root');a.add_argument('manifest')
    a=s.add_parser('extract');a.add_argument('archive');a.add_argument('destination');a.add_argument('--archive-sha256')
    a=s.add_parser('collect');a.add_argument('--study',required=True);a.add_argument('--run',required=True);a.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        result={'probe':lambda:probe(a.root),'verify':lambda:verify(a.root,a.manifest),'extract':lambda:extract(a.archive,a.destination,a.archive_sha256),'collect':lambda:collect(a.study,a.run,a.out)}[a.cmd]()
        print(json.dumps(result,indent=2))
    except Exception as e:print(json.dumps({'status':'OPERATIONAL_FAILURE','exception':repr(e)}),file=sys.stderr);sys.exit(1)
