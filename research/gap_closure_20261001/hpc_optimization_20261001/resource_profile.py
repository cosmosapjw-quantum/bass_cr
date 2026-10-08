"""Single-node OpenMPI launch admission; never launches a physics job."""
from pathlib import Path
import argparse,json,math,os
GiB=1024**3
# Linux counter definitions:
# https://docs.kernel.org/admin-guide/cgroup-v2.html#memory-interface-files
# https://docs.kernel.org/filesystems/proc.html#meminfo
# This is a conservative admission estimate, not the kernel's MemAvailable
# algorithm or a guarantee that a future allocation cannot fail. Preserve half
# the eligible cache in addition to plan()'s unchanged OS/orchestration reserve.
_CACHE_KEYS=('file','active_file','inactive_file','file_mapped','file_dirty',
             'file_writeback','shmem','unevictable')

def clean_file_credit(stat,current,minimum,low,descendants):
    """Half of eligible clean unmapped file LRU; no anon/slab/swap credit.

    Subtracting whole categories may double-subtract overlapping pages, which
    intentionally underestimates reclaimability. Missing/invalid counters and
    non-leaf cgroups get no credit: protected descendants cannot be inferred
    from the parent's aggregate memory.stat. memory.min/low are also excluded.
    """
    values=[current,minimum,low,descendants]+[stat.get(k) for k in _CACHE_KEYS]
    if any(type(v) is not int or v<0 for v in values) or descendants!=0:return 0
    file_lru=min(current,stat['file'],stat['active_file']+stat['inactive_file'])
    excluded=sum(stat[k] for k in ('file_mapped','file_dirty','file_writeback','shmem','unevictable'))
    return max(0,file_lru-excluded-max(minimum,low))//2

def _flat_counters(path):
    return {k:int(v) for k,v in (line.split() for line in path.read_text().splitlines())}

def _cache_snapshot(path,current):
    stat=_flat_counters(path/'memory.stat');group=_flat_counters(path/'cgroup.stat')
    minimum=int((path/'memory.min').read_text());low=int((path/'memory.low').read_text())
    if any(group[k]<0 for k in ('nr_descendants','nr_dying_descendants')):
        raise ValueError('negative cgroup descendant count')
    descendants=group['nr_descendants']+group['nr_dying_descendants']
    return {'counters':{k:stat.get(k) for k in _CACHE_KEYS},'memory_min_bytes':minimum,
            'memory_low_bytes':low,'descendants':descendants,
            'credit_bytes':clean_file_credit(stat,current,minimum,low,descendants)}

def cgroup_memory_headroom(path,limit):
    """Read-only bounded cache allowance for one finite cgroup memory.max.

    Bracket observations; charge the larger usage and retain the smaller cache
    credit. Non-atomic counters still make this an estimate, rechecked at launch.
    If accounting needed for credit is unavailable, retain raw headroom only;
    if usage itself cannot be read, this finite cap supplies zero availability.
    """
    path=Path(path);row={'path':str(path),'limit_bytes':limit,
                       'clean_file_credit_bytes':0,'estimated_available_bytes':0,
                       'unreclaimed_headroom_bytes':0,'policy':'HALF_CLEAN_UNMAPPED_LEAF_FILE_V1'}
    try:
        before=int((path/'memory.current').read_text())
        if before<0:raise ValueError('negative memory.current')
        snapshots=[]
        try:
            snapshots=[_cache_snapshot(path,before),_cache_snapshot(path,before)]
        except (OSError,ValueError,KeyError) as exc:
            row['credit_disabled_reason']=type(exc).__name__
        after=int((path/'memory.current').read_text())
        if after<0:raise ValueError('negative memory.current')
        current=max(before,after)
        # Clamp once more to the smaller usage observation, preserving evidence.
        credit=min(clean_file_credit(s['counters'],min(before,after),s['memory_min_bytes'],
                                    s['memory_low_bytes'],s['descendants']) for s in snapshots) if len(snapshots)==2 else 0
        row.update(current_bytes=current,unreclaimed_headroom_bytes=max(0,limit-current),
                   clean_file_credit_bytes=credit,
                   estimated_available_bytes=min(limit,max(0,limit-current+credit)),
                   cache_observations=snapshots)
    except (OSError,ValueError) as exc:
        row['usage_unavailable_reason']=type(exc).__name__
    return row

def census():
    cpus=sorted(os.sched_getaffinity(0));physical=set();unknown=False
    for c in cpus:
        p=Path(f'/sys/devices/system/cpu/cpu{c}/topology')
        try:physical.add(((p/'physical_package_id').read_text().strip(),(p/'core_id').read_text().strip()))
        except OSError:unknown=True
    mem={k:int(v.split()[0])*1024 for k,v in (l.split(':',1) for l in Path('/proc/meminfo').read_text().splitlines())}
    quotas=[];memlimits=[];memfree=[];memadmission=[]
    # Read current cgroup and accessible ancestors: tighter parent limits count.
    rel=next((x.split(':',2)[2] for x in Path('/proc/self/cgroup').read_text().splitlines() if x.startswith('0::')),'/')
    root=Path('/sys/fs/cgroup');p=root/rel.lstrip('/')
    if not p.is_dir():p=root
    while p==root or root in p.parents:
        try:
            q,period=(p/'cpu.max').read_text().split()
            if q!='max':quotas.append(int(q)/int(period))
        except (OSError,ValueError):pass
        try:
            m=(p/'memory.max').read_text().strip()
            if m!='max':
                memlimits.append(int(m))
                estimate=cgroup_memory_headroom(p,int(m))
                memadmission.append(estimate);memfree.append(estimate['estimated_available_bytes'])
        except (OSError,ValueError):pass
        if p==root:break
        p=p.parent
    budget=min([mem['MemTotal'],*memlimits]);quota=min([float(len(cpus)),*quotas])
    return {'affinity_cpus':cpus,'logical_cpus':len(cpus),'physical_cores':0 if unknown else len(physical),'cpu_quota':quota,'usable_cpu_budget':max(0,math.floor(quota)),'memory_limit_bytes':budget,'memory_available_bytes':min([budget,mem['MemAvailable'],*memfree]),'memory_available_is_estimate':True,'cgroup_memory_admission':memadmission,'topology_source':'Linux sysfs; missing topology requires explicit logical CPU mode','cgroup_source':'current accessible cgroup and parents','cpu_model':next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),'unknown')}
def plan(info,ranks,threads,per_rank_gib,*,logical=False,program=None):
    if type(ranks) is not int or ranks<2 or type(threads) is not int or threads<1:raise ValueError('MPI requires>=2 ranks and positive integral threads')
    if not math.isfinite(per_rank_gib) or per_rank_gib<=0:raise ValueError('positive measured/estimated per-rank RSS required')
    slots=min(info['usable_cpu_budget'],info['logical_cpus'] if logical else info['physical_cores'])
    if ranks*threads>slots:raise ValueError('ranks*threads exceeds admitted CPU slots')
    memory=min(info['memory_limit_bytes'],info['memory_available_bytes']);reserve=max(GiB,memory//8)
    request=math.ceil(per_rank_gib*GiB)*ranks
    if request>memory-reserve:raise ValueError('RSS estimate exceeds memory budget after reserve')
    env={k:'1' for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']}
    allowed=info['affinity_cpus']
    if len(allowed)!=len(set(allowed)) or len(allowed)!=info['logical_cpus']:raise ValueError('exact admitted affinity IDs required')
    env.update(OMP_NUM_THREADS=str(threads),OMP_DYNAMIC='FALSE',OMP_MAX_ACTIVE_LEVELS='1',OMP_PROC_BIND='close',OMP_PLACES='threads' if logical else 'cores',BASS_HPC_ADMITTED_CPUS=','.join(map(str,allowed)),BASS_HPC_CPU_UNIT='logical' if logical else 'physical_core')
    argv=['mpirun','-np',str(ranks),'--nooversubscribe','--map-by',f'slot:PE={threads}','--bind-to','hwthread' if logical else 'core','--report-bindings']
    if logical:argv.append('--use-hwthread-cpus')
    for k,v in env.items():argv+=['-x',k+'='+v]
    argv+=program or ['python','mpi_queue.py','--self-test']
    return {'schema':'BASS_HPC_LAUNCH_PLAN_V1','argv':argv,'environment':env,'ranks_including_coordinator':ranks,'worker_ranks':ranks-1,'threads_per_rank':threads,'total_bound_slots':ranks*threads,'cpu_unit':'logical' if logical else 'physical_core','estimated_total_rss_bytes':request,'memory_reserve_bytes':reserve,'memory_budget_bytes':memory-reserve,'rss_is_estimate_not_os_enforcement':True,'fresh_physical_admission_required':True,'science_launch_authorized':False,'census':info}
def verify_rank_allocation(threads,*,actual=None,environ=None):
    env=os.environ if environ is None else environ
    if not env.get('BASS_HPC_ADMITTED_CPUS'):raise ValueError('missing exact launch CPU allocation')
    allowed={int(x) for x in env['BASS_HPC_ADMITTED_CPUS'].split(',')};info=census() if actual is None else actual
    if not set(info['affinity_cpus'])<=allowed:raise ValueError('rank rebound outside admitted CPU IDs')
    unit=env.get('BASS_HPC_CPU_UNIT')
    if unit not in ('logical','physical_core'):raise ValueError('unknown CPU unit')
    slots=info['logical_cpus'] if unit=='logical' else info['physical_cores']
    if slots!=threads:raise ValueError('actual bound rank slots do not match thread allocation')
    return {'affinity_cpus':info['affinity_cpus'],'slots':slots,'unit':unit}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ranks',type=int);p.add_argument('--threads',type=int,default=1);p.add_argument('--per-rank-gib',type=float,default=1.0);p.add_argument('--logical-cpus',action='store_true');a=p.parse_args();info=census();print(json.dumps(info if a.ranks is None else plan(info,a.ranks,a.threads,a.per_rank_gib,logical=a.logical_cpus),indent=2))
