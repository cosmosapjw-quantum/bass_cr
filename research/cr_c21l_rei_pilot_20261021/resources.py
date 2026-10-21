"""Linux resource observations and cooperative C21K-compatible cpu_N.lock leases."""
import fcntl, math, os, time, platform, socket
from pathlib import Path
GIB=1024**3

def cpu_set(s):
    out=set()
    for part in s.strip().split(','):
        if part:
            z=part.split('-');out.update(range(int(z[0]),int(z[-1])+1))
    return out

def cgroup_paths():
    root=Path('/sys/fs/cgroup')
    if not (root/'cgroup.controllers').exists():raise RuntimeError('CGROUP_V2_NOT_VISIBLE')
    relative=next((x[3:].lstrip('/') for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::')),'')
    p=root/relative
    if not p.is_dir():p=root
    result=[]
    while p.is_relative_to(root):
        result.append(p)
        if p==root:break
        p=p.parent
    return result

def snapshot(affinity=None):
    mem={}
    for l in Path('/proc/meminfo').read_text().splitlines():
        k,v=l.split(':',1)
        if k in ('MemTotal','MemAvailable'):mem[k]=int(v.split()[0])*1024
    cpus=set(os.sched_getaffinity(0) if affinity is None else affinity);quotas=[];limits=[];remaining=[];obs=[]
    for p in cgroup_paths():
        item={'path':str(p)}
        for n in ('cpu.max','cpuset.cpus.effective','memory.max','memory.current'):
            f=p/n;item[n]=f.read_text().strip() if f.is_file() else None
        if item['cpuset.cpus.effective']:cpus &= cpu_set(item['cpuset.cpus.effective'])
        if item['cpu.max']:
            q,t=item['cpu.max'].split()
            if q!='max':quotas.append(int(q)/int(t))
        if item['memory.max'] and item['memory.max']!='max':
            limit=int(item['memory.max']);limits.append(limit)
            if item['memory.current'] is not None:remaining.append(max(0,limit-int(item['memory.current'])))
        obs.append(item)
    return {'allowed_cpus':sorted(cpus-{55}),'affinity':sorted(os.sched_getaffinity(0) if affinity is None else affinity),'quota':min(quotas) if quotas else None,'memory_limit':min([mem['MemTotal']]+limits),'memory_available':min([mem['MemAvailable']]+remaining),'cgroups':obs,'protected_cpu':55}

def capacity(s,workers=4,restrict=None):
    if workers<1:raise ValueError('workers must be positive')
    cpus=set(s['allowed_cpus'])-{55}
    if restrict is not None:cpus &= set(restrict)
    cpus=sorted(cpus)
    slots=min(len(cpus),math.floor(s['quota']) if s['quota'] is not None else len(cpus))
    reserve=max(GIB,math.ceil(s['memory_limit']/8))
    usable=max(0,s['memory_available']-reserve-256*1024**2)
    n=max(0,min(workers,slots-1,usable//(512*1024**2)))
    return {'cpu_candidates':cpus,'maximum_workers':n,'cpu_slots_including_coordinator':slots,'memory_reserve_bytes':reserve,'worker_budget_bytes':512*1024**2,'coordinator_budget_bytes':256*1024**2,'memory_worker_slots':usable//(512*1024**2)}

def proc_cpu():
    result={}
    for l in Path('/proc/stat').read_text().splitlines():
        z=l.split()
        if z and z[0].startswith('cpu') and z[0][3:].isdigit():
            a=list(map(int,z[1:]));result[int(z[0][3:])]=(sum(a[:8]),a[3]+(a[4] if len(a)>4 else 0))
    return result

def sample_load(seconds=.25):
    a=proc_cpu();time.sleep(seconds);b=proc_cpu();out={}
    for c,(total,idle) in b.items():
        if c in a:
            dt=total-a[c][0];out[c]=max(0.,min(1.,1-(idle-a[c][1])/dt)) if dt>0 else 1.
    return out

def acquire_cpu(directory,cpu):
    f=(Path(directory)/('cpu_%d.lock'%cpu)).open('a+b')
    try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:f.close();return None
    return f

def execution_metadata(site='unspecified'):
    if site not in ('unspecified','sandbox','ncp','other'):raise ValueError('unknown execution site')
    return {'execution_site':site,'execution_site_basis':'operator-declared; not automatic attestation','NCP_execution':None if site=='unspecified' else site=='ncp','observed_hostname':socket.gethostname(),'observed_platform':platform.platform()}

def admit(workers,lease_dir,restrict=None,wait_seconds=3.,execution_site='unspecified'):
    directory=Path(lease_dir);directory.mkdir(parents=True,exist_ok=True)
    deadline=time.monotonic()+wait_seconds;observations=[]
    while True:
        snap=snapshot();cap=capacity(snap,workers,restrict);loads=sample_load()
        obs={'snapshot':snap,'capacity':cap,'load_fraction':loads,'idle_threshold':.35};observations.append(obs)
        handles=[]
        if cap['maximum_workers']>=1:
            for cpu in sorted(cap['cpu_candidates'],key=lambda c:(loads.get(c,1.),c)):
                if loads.get(cpu,1.)>.35:continue
                f=acquire_cpu(directory,cpu)
                if f is not None:handles.append((cpu,f))
                if len(handles)>=cap['maximum_workers']+1:break
        if len(handles)>=2:
            return {'observations':observations,'coordinator_cpu':handles[0][0],'worker_cpus':[c for c,f in handles[1:]],'lease_directory':str(directory),'scope':'OPERATOR_DECLARED_'+execution_site.upper(),**execution_metadata(execution_site),'unmanaged_jobs':'observed only; cooperative leases cover clients using same directory'},handles
        for c,f in handles:f.close()
        if time.monotonic()>=deadline:raise RuntimeError('NO_IDLE_LEASED_COORDINATOR_PLUS_WORKER_CAPACITY:'+str(obs))
        time.sleep(.25)
