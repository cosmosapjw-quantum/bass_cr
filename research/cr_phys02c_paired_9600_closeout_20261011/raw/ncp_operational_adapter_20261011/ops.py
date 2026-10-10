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

def mount_unescape(value):
    import re
    return re.sub(r'\\([0-7]{3})',lambda m:chr(int(m.group(1),8)),value)

def resource_read(p,allow_absent=False):
    """Only ENOENT can be an expected absence; other read failures HOLD."""
    try:return pathlib.Path(p).read_text().strip()
    except FileNotFoundError:
        if allow_absent:return None
        raise ValueError('CGROUP2_REQUIRED_FILE_ABSENT '+str(p))
    except OSError as e:raise ValueError('CGROUP2_RESOURCE_READ_ERROR '+str(p)) from e

def cgroup2_hierarchy(proc_root='/proc'):
    """Resolve current membership and every visible ancestor up to mount root.

    Missing or ambiguous mapping raises; it never falls back to /sys/fs/cgroup.
    """
    proc=pathlib.Path(proc_root)
    membership=read(proc/'self/cgroup');mountinfo=read(proc/'self/mountinfo')
    if membership is None or mountinfo is None:raise ValueError('CGROUP_MEMBERSHIP_OR_MOUNTINFO_UNREADABLE')
    members=[line[3:] for line in membership.splitlines() if line.startswith('0::')]
    if len(members)!=1:raise ValueError('CGROUP2_MEMBERSHIP_NOT_UNIQUE')
    member=pathlib.PurePosixPath(members[0])
    if not member.is_absolute() or '..' in member.parts:raise ValueError('CGROUP_MEMBERSHIP_UNSAFE')
    mappings=[]
    for line in mountinfo.splitlines():
        fields=line.split()
        try:split=fields.index('-')
        except ValueError:continue
        if len(fields)<=split+1 or fields[split+1]!='cgroup2':continue
        if len(fields)<6:raise ValueError('CGROUP2_MOUNTINFO_MALFORMED')
        mountroot=pathlib.PurePosixPath(mount_unescape(fields[3]));mountpoint=pathlib.Path(mount_unescape(fields[4]))
        if not mountroot.is_absolute() or '..' in mountroot.parts or not mountpoint.is_absolute():raise ValueError('CGROUP2_MOUNT_PATH_UNSAFE')
        if not member.is_relative_to(mountroot):continue
        base=mountpoint.joinpath(*member.relative_to(mountroot).parts)
        if not base.is_dir() or not mountpoint.is_dir():continue
        if base.resolve()!=base or mountpoint.resolve()!=mountpoint:raise ValueError('CGROUP2_SYMLINK_OR_UNRESOLVED_PATH')
        mappings.append((len(mountroot.parts),mountroot,mountpoint,base))
    if not mappings:raise ValueError('CGROUP2_MEMBERSHIP_MOUNT_MAPPING_UNRESOLVED')
    # A nested visible mount is narrower; use the broadest matching mount to
    # inspect the most visible ancestors. Ambiguous equally broad views HOLD.
    depth=min(x[0] for x in mappings);chosen=[x for x in mappings if x[0]==depth]
    distinct={(str(x[1]),str(x[2]),str(x[3])) for x in chosen}
    if len(distinct)!=1:raise ValueError('CGROUP2_MEMBERSHIP_MOUNT_MAPPING_AMBIGUOUS')
    _,mountroot,mountpoint,base=chosen[0]
    ancestors=[];p=base
    while True:
        true_root=p==mountpoint and mountroot==pathlib.PurePosixPath('/')
        values={name:resource_read(p/name,allow_absent=true_root) for name in ('cpu.max','memory.max','memory.current')}
        ancestors.append({'path':str(p),'is_true_cgroup2_root':true_root,'values':values})
        if p==mountpoint:break
        p=p.parent
        if not p.is_relative_to(mountpoint):raise ValueError('CGROUP2_ANCESTOR_WALK_ESCAPED_MOUNT')
    p=base;disabled=[]
    while True:
        cpuset=resource_read(p/'cpuset.cpus.effective',allow_absent=True)
        if cpuset is not None:
            if not cpuset:raise ValueError('CGROUP2_EFFECTIVE_CPUSET_EMPTY '+str(p))
            break
        # A missing effective set is normal only when cpuset was not enabled
        # by the parent. Verify both controller views before inheriting.
        if p==mountpoint:raise ValueError('CGROUP2_EFFECTIVE_CPUSET_UNRESOLVED')
        controllers=resource_read(p/'cgroup.controllers').split()
        subtree=resource_read(p.parent/'cgroup.subtree_control').split()
        if 'cpuset' in controllers or 'cpuset' in subtree:
            raise ValueError('CGROUP2_ENABLED_CPUSET_FILE_ABSENT '+str(p))
        disabled.append(str(p));p=p.parent
    cpus=set()
    for part in cpuset.split(','):
        pair=part.split('-')
        if len(pair)==1:cpus.add(int(pair[0]))
        elif len(pair)==2:
            lo,hi=map(int,pair)
            if lo<0 or hi<lo:raise ValueError('CGROUP2_CPUSET_INVALID')
            cpus.update(range(lo,hi+1))
        else:raise ValueError('CGROUP2_CPUSET_INVALID')
    if not cpus or min(cpus)<0:raise ValueError('CGROUP2_CPUSET_INVALID')
    return {'membership':str(member),'mount_root':str(mountroot),'mount_point':str(mountpoint),'leaf':str(base),'inspection_scope':'ALL_READABLE_VISIBLE_ANCESTORS_TO_MOUNT_ROOT','ancestors':ancestors,'effective_cpuset':cpuset,'effective_cpuset_cpus':sorted(cpus),'effective_cpuset_source':str(p),'cpuset_disabled_descendants':disabled}

def effective_capacity(mem,hierarchy):
    total=mem.get('MemTotal');host_available=mem.get('MemAvailable')
    if not isinstance(total,int) or total<=0 or not isinstance(host_available,int) or host_available<0:raise ValueError('HOST_MEMORY_CAPACITY_UNREADABLE')
    limits=[total];headrooms=[host_available];quotas=[]
    for row in hierarchy['ancestors']:
        vals=row['values']
        if any(v is None for v in vals.values()) and not row.get('is_true_cgroup2_root'):
            raise ValueError('CGROUP2_NONROOT_LIMIT_ABSENT')
        if vals['cpu.max'] is not None:
            cpu=vals['cpu.max'].split()
            if len(cpu)!=2 or int(cpu[1])<=0:raise ValueError('CGROUP2_CPU_QUOTA_INVALID')
            if cpu[0]!='max':
                q=int(cpu[0])
                if q<=0:raise ValueError('CGROUP2_CPU_QUOTA_INVALID')
                quotas.append(q/int(cpu[1]))
        current=int(vals['memory.current']) if vals['memory.current'] is not None else None
        if current is not None and current<0:raise ValueError('CGROUP2_MEMORY_USAGE_INVALID')
        if vals['memory.max'] is not None and vals['memory.max']!='max':
            if current is None:raise ValueError('CGROUP2_BOUNDED_MEMORY_USAGE_ABSENT')
            limit=int(vals['memory.max'])
            if limit<=0:raise ValueError('CGROUP2_MEMORY_LIMIT_INVALID')
            limits.append(limit);headrooms.append(max(0,limit-current))
    bounded=min(limits);available=min(headrooms);reserve=max(int(bounded*.125),GIB)
    return {'bounded_memory_bytes':bounded,'available_before_reserve_bytes':available,'reserve_bytes':reserve,'available_working_bytes':max(0,available-reserve),'cpu_quota':min(quotas) if quotas else None}

def probe(root,proc_root='/proc'):
    mem={};capacity={};hierarchy=None;error=None
    try:
        for line in (read(pathlib.Path(proc_root)/'meminfo') or '').splitlines():
            k,v=line.split(':',1);mem[k]=int(v.strip().split()[0])*1024
        hierarchy=cgroup2_hierarchy(proc_root);capacity=effective_capacity(mem,hierarchy)
    except (ValueError,OSError,IndexError) as e:error=str(e)
    status=read(pathlib.Path(proc_root)/'self/status') or ''
    rss=next((x.split(':',1)[1].strip() for x in status.splitlines() if x.startswith('VmRSS:')),None)
    affinity=sorted(os.sched_getaffinity(0));effective=sorted(set(affinity)&set(hierarchy['effective_cpuset_cpus'])) if hierarchy else []
    topology=[]
    for cpu in effective:
        base=f'/sys/devices/system/cpu/cpu{cpu}/topology/'
        topology.append({'cpu':cpu,'core_id':read(base+'core_id'),'package_id':read(base+'physical_package_id')})
    live=0
    for p in pathlib.Path(proc_root).iterdir():
        if p.name.isdigit():
            st=read(p/'status') or ''
            if '\nUid:\t'+str(os.getuid())+'\t' in st:live+=1
    disk=shutil.disk_usage(root).free
    admitted=error is None and capacity['available_working_bytes']>=12*GIB and disk>=8*GIB and bool(effective) and (capacity['cpu_quota'] is None or capacity['cpu_quota']>=1)
    reason=error or (None if admitted else 'INSUFFICIENT_EFFECTIVE_MEMORY_CPU_OR_DISK')
    return {'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'ADMITTED_RESOURCE_ONLY' if admitted else 'HOLD','reason':reason,'capacity_established':error is None,'affinity_cpus':affinity,'effective_allowed_cpus':effective,'cgroup_hierarchy':hierarchy,'cgroup':hierarchy['ancestors'][0]['values'] if hierarchy else None,'topology':topology,'load_average':os.getloadavg(),'same_uid_process_count_no_commandlines':live,'coordinator_pid':os.getpid(),'coordinator_RSS':rss,'memory_host_bytes':mem,**capacity,'estimated_peak_bytes':8*GIB,'minimum_working_bytes':12*GIB,'free_disk_bytes':disk,'admitted':admitted,'thread_environment':{k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS','NUMEXPR_NUM_THREADS','OMP_MAX_ACTIVE_LEVELS')}}

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
