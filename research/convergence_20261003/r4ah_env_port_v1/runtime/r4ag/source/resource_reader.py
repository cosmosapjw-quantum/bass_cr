"""Fail-closed cgroup-v2 accounting. Production observes live proc/cgroupfs.

Pure snapshot evaluation is a test boundary, never a prepare input channel.
Namespace-hidden or truncated hierarchies need a separate accounting contract.
"""
from fractions import Fraction
import json
import os
from pathlib import Path, PurePosixPath
import re
import time

class ResourceError(ValueError):
    """Insufficient resource accounting or provenance."""

def fail(message):
    raise ResourceError('UNRESOLVED_RESOURCE_HIERARCHY: '+message)

def absolute(value):
    if not isinstance(value,str) or not value.startswith('/') or '\x00' in value:
        fail('absolute hierarchy path required')
    if value!='/' and (any(p in ('','.','..') for p in value[1:].split('/')) or value.endswith(' (deleted)')):
        fail('noncanonical or deleted hierarchy path')
    return PurePosixPath(value)

def unescape(value):
    table={'040':' ','011':'\t','012':'\n','134':'\\'}
    if re.search(r'\\(?!040|011|012|134)',value):fail('invalid mountinfo escape')
    return re.sub(r'\\(040|011|012|134)',lambda m:table[m[1]],value)

def membership(text):
    if not isinstance(text,str):fail('unreadable membership')
    rows=text.splitlines()
    if len(rows)!=1 or not rows[0].startswith('0::'):fail('v2-only membership required; v1/hybrid/duplicate rejected')
    return absolute(rows[0][3:])

def mounts(text):
    if not isinstance(text,str):fail('unreadable mountinfo')
    result=[]
    for line in text.splitlines():
        parts=line.split(' - ')
        if len(parts)!=2:fail('malformed mountinfo record')
        before,after=parts[0].split(),parts[1].split()
        if len(before)<6 or len(after)<3:fail('incomplete mountinfo record')
        if after[0]=='cgroup':fail('hybrid/v1 mount rejected')
        if after[0]!='cgroup2':continue
        if not before[0].isdigit() or not before[1].isdigit() or not re.fullmatch(r'\d+:\d+',before[2]):fail('invalid mount identity')
        result.append({'mount_id':before[0],'parent_id':before[1],'device':before[2],
                       'root':str(absolute(unescape(before[3]))),'mountpoint':str(absolute(unescape(before[4]))),'filesystem':'cgroup2'})
    if not result:fail('no visible cgroup2 mount')
    return result

def global_visibility(s):
    # PID1 namespace equality alone is insufficient in a container. A visible
    # kthreadd kernel task at PID2 ties this process to the initial namespaces.
    try:
        status=dict(line.split(':',1) for line in s['kernel2_status'].splitlines() if ':' in line)
        if s['kernel2_comm'].strip()!='kthreadd' or any(status.get(k,'').strip()!=v for k,v in {'Pid':'2','PPid':'0','NSpid':'2','Kthread':'1'}.items()):
            fail('initial kernel-thread identity not established')
        if membership(s['kernel2_membership'])!=PurePosixPath('/'):fail('kernel-thread root membership not established')
        ns=s['namespaces']
        for role in ('self','1','2'):
            for kind in ('pid','cgroup','mnt'):
                if not re.fullmatch(kind+r':\[\d+\]',ns[role][kind]):fail('invalid namespace identity')
        for kind in ('pid','cgroup'):
            if not ns['self'][kind]==ns['1'][kind]==ns['2'][kind]:fail('initial PID/cgroup namespace visibility not established')
    except (KeyError,TypeError,AttributeError,ValueError) as error:
        if isinstance(error,ResourceError):raise
        fail('unreadable initial-namespace evidence')

def locate(s):
    member=membership(s['membership']);candidates=[]
    for mount in mounts(s['mountinfo']):
        root=PurePosixPath(mount['root'])
        if member.is_relative_to(root):relative,mode=member.relative_to(root),'MOUNT_ROOT_RELATIVE'
        else:relative,mode=member.relative_to('/'),'NAMESPACE_RELATIVE_UNPROVEN'
        candidates.append((mount,PurePosixPath(mount['mountpoint'])/relative,mode))
    if len(candidates)!=1:fail('ambiguous cgroup2 mapping')
    mount,leaf,mode=candidates[0];global_visibility(s)
    if mount['root']!='/' or mode=='NAMESPACE_RELATIVE_UNPROVEN':fail('mount hides ancestor limits; separate visibility contract required')
    point=PurePosixPath(mount['mountpoint']);ancestors=[leaf]
    while ancestors[-1]!=point:
        parent=ancestors[-1].parent
        if not parent.is_relative_to(point):fail('path escapes mountpoint')
        ancestors.append(parent)
    return member,mount,leaf,ancestors

def file_value(s,path,optional=False):
    value=s['files'].get(str(path))
    if isinstance(value,dict):fail('unreadable resource file: '+str(path)+' '+str(value))
    if value is None:
        if optional:return None
        fail('missing required resource file: '+str(path))
    if not isinstance(value,str):fail('invalid resource file type: '+str(path))
    return value

def integer(text,name,positive=False):
    if not re.fullmatch(r'[0-9]+',text):fail('invalid nonnegative integer in '+name)
    value=int(text)
    if positive and value==0:fail('positive value required in '+name)
    return value

def memory_info(text):
    values={}
    for line in text.splitlines():
        if ':' not in line:fail('malformed meminfo')
        key,value=line.split(':',1)
        if key in ('MemTotal','MemAvailable'):
            if key in values or not re.fullmatch(r'\s*[0-9]+\s+kB\s*',value):fail('invalid/duplicated host memory observation')
            values[key]=integer(value.split()[0],key,positive=(key=='MemTotal'))*1024
    if set(values)!={'MemTotal','MemAvailable'} or values['MemAvailable']>values['MemTotal']:fail('incomplete/inconsistent host memory')
    return values['MemTotal'],values['MemAvailable']

def evaluate_snapshot(s):
    member,mount,leaf,ancestors=locate(s);aff=s['affinity']
    if not isinstance(aff,list) or not aff or any(type(x) is not int or x<0 for x in aff) or len(set(aff))!=len(aff):fail('invalid process affinity')
    total,available=memory_info(s['meminfo']);root=PurePosixPath(mount['mountpoint'])
    if not {'cpu','memory'}<=set(file_value(s,root/'cgroup.controllers').split()):fail('CPU/memory controllers unavailable')
    quotas,limits,headrooms,rows=[],[total],[available],[]
    for path in ancestors:
        cpu=file_value(s,path/'cpu.max',path==root)
        maximum=file_value(s,path/'memory.max',path==root)
        current=file_value(s,path/'memory.current',path==root)
        if path==root:
            if any(x is not None for x in (cpu,maximum,current)):fail('unexpected/partial global-root accounting files')
            rows.append({'path':str(path),'accounting':'GLOBAL_ROOT_CONTROLLER_EXEMPTION',
                         'evidence':'initial kernel-thread namespace identity and full cgroup2 mount root',
                         'cpu.max':None,'memory.max':None,'memory.current':None})
            continue
        words=cpu.split()
        if len(words)!=2:fail('cpu.max requires quota and period')
        period=integer(words[1],'cpu.max period',True)
        quota=None if words[0]=='max' else Fraction(integer(words[0],'cpu.max quota',True),period)
        if quota is not None:quotas.append(quota)
        maximum_value=None if maximum.strip()=='max' else integer(maximum.strip(),'memory.max')
        current_value=integer(current.strip(),'memory.current');headroom=None
        if maximum_value is not None:
            limits.append(maximum_value);headroom=max(0,maximum_value-current_value);headrooms.append(headroom)
        rows.append({'path':str(path),'accounting':'OBSERVED_V2_CONTROLLER_FILES','cpu.max':cpu,'memory.max':maximum,
                     'memory.current':current,'cpu_quota':str(quota) if quota is not None else 'EXPLICIT_MAX','memory_headroom':headroom})
    quota=min(quotas) if quotas else None
    binding={'membership':str(member),'mount':mount,'namespaces':s['namespaces']['self']}
    return {'affinity':sorted(aff),'quota':'unlimited' if quota is None else str(quota),
            'effective_cpu_capacity':str(min(Fraction(len(aff)),quota) if quota is not None else len(aff)),
            'memory_limit':min(limits),'memory_available':min(headrooms),
            'cgroup_cpu_max':rows[0]['cpu.max'].split() if rows[0]['cpu.max'] is not None else None,
            'cgroup_memory_current':int(rows[0]['memory.current']) if rows[0]['memory.current'] is not None else None,
            'observed_utc':s['observed_utc'],
            'resource_hierarchy':{'schema':'R4AH_PROCESS_CGROUP_V2_V1','binding':binding,'leaf':str(leaf),'ancestors':rows,
                                  'global_root_visibility':'INITIAL_KERNEL_THREAD_NAMESPACE_MATCH',
                                  'host_mem_total':total,'host_mem_available':available,'raw_snapshot':s}}

def read_live(path,optional=False):
    try:return Path(path).read_text()
    except FileNotFoundError:
        if optional:return None
        fail('missing observation: '+str(path))
    except OSError as error:fail('unreadable observation: '+str(path)+' '+type(error).__name__)

def namespaces(role):
    try:return {kind:os.readlink('/proc/'+role+'/ns/'+kind) for kind in ('pid','cgroup','mnt')}
    except OSError as error:fail('namespace observation failed: '+role+' '+type(error).__name__)

def observe_resources():
    """Live reads only. No fixture/file/host override parameters."""
    s={'membership':read_live('/proc/self/cgroup'),'mountinfo':read_live('/proc/self/mountinfo'),
       'meminfo':read_live('/proc/meminfo'),'affinity':sorted(os.sched_getaffinity(0)),
       'namespaces':{role:namespaces(role) for role in ('self','1','2')},
       'kernel2_comm':read_live('/proc/2/comm'),'kernel2_status':read_live('/proc/2/status'),
       'kernel2_membership':read_live('/proc/2/cgroup'),
       'observed_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'files':{}}
    _,mount,_,ancestors=locate(s);root=Path(mount['mountpoint'])
    for directory in ancestors:
        path=Path(str(directory))
        if path.resolve()!=path:fail('symlink/resource path substitution')
        for name in ('cpu.max','memory.max','memory.current'):
            p=path/name
            if p.is_symlink():fail('symlink resource file')
            s['files'][str(p)]=read_live(p,optional=(path==root))
    p=root/'cgroup.controllers'
    if p.is_symlink():fail('symlink controller file')
    s['files'][str(p)]=read_live(p)
    after={'membership':read_live('/proc/self/cgroup'),'mountinfo':read_live('/proc/self/mountinfo'),
           'namespaces':namespaces('self'),'affinity':sorted(os.sched_getaffinity(0))}
    if any(after[k]!=s[k] for k in ('membership','mountinfo','affinity')) or after['namespaces']!=s['namespaces']['self']:
        fail('process membership/namespace/mount/affinity changed during observation')
    s['observation_after']=after
    return evaluate_snapshot(s)

def assert_same_hierarchy(prepared, observed):
    try:
        original = prepared['resource_hierarchy']['binding']
        current = observed['resource_hierarchy']['binding']
    except (KeyError, TypeError):
        fail('prepared/current hierarchy binding is missing')
    if original != current:
        fail('membership/namespace/mount changed since preparation')

if __name__=='__main__':
    print(json.dumps(observe_resources(),indent=2,sort_keys=True))
