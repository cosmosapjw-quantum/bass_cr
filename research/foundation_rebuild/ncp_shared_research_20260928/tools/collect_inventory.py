#!/usr/bin/env python3
"""Read-only Linux shared-host sampler. Stdlib only. No process/resource mutation.

Never reads environment variables, command-line arguments, keys, or credentials of
other processes. Auto-discovery is advisory; use --session PID:LABEL for precise
mapping. Outputs only process names, PIDs, counters, and hashed cgroup identities.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import time
from resource_model import roots_of_process_tree


def read_text(path):
    try:
        return Path(path).read_text().strip()
    except (OSError, UnicodeError):
        return None


def parse_stat(text, page_size):
    left, sep, tail = text.rpartition(')')
    if not sep:
        raise ValueError('invalid proc stat')
    pid_text, comm = left.split('(', 1)
    f = tail.split()
    return {'pid':int(pid_text), 'comm':comm, 'state':f[0], 'ppid':int(f[1]),
            'cpu_ticks':int(f[11])+int(f[12]), 'start_ticks':int(f[19]),
            'rss_bytes':max(0,int(f[21]))*page_size, 'threads':int(f[17])}


def interval_cores(before, after, members, seconds, hz):
    if seconds <= 0 or hz <= 0:
        raise ValueError('positive interval and clock frequency required')
    delta = sum(max(0, after[p]['cpu_ticks']-before[p]['cpu_ticks']) for p in members
                if p in before and p in after and before[p]['start_ticks']==after[p]['start_ticks'])
    return delta/hz/seconds


def descendants(rows, root):
    if root not in rows:
        return set()
    found={root}; pending=[root]
    children={}
    for pid,row in rows.items():
        children.setdefault(row['ppid'],[]).append(pid)
    while pending:
        for pid in children.get(pending.pop(),[]):
            if pid not in found:
                found.add(pid); pending.append(pid)
    return found


def cgroup_ancestors(group, mount):
    mount=Path(mount)
    p=PurePosixPath(group)
    if not p.is_absolute() or '..' in p.parts:
        return []
    current=mount.joinpath(*p.parts[1:])
    if not current.is_dir():
        return []
    result=[]
    while current != mount:
        result.append(current); current=current.parent
    return result+[mount]


def parse_limit(text):
    if text is None:
        return None
    return 'unlimited' if text.strip()=='max' else int(text)


def process_snapshot():
    rows={}; page=os.sysconf('SC_PAGE_SIZE'); unreadable=0
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():
            continue
        text=read_text(path/'stat')
        if text is None:
            unreadable+=1; continue
        try:
            row=parse_stat(text,page)
            # Executable basename, never argv. Node-based wrappers may be missed.
            try: row['exe_basename']=(path/'exe').resolve(strict=True).name
            except OSError: row['exe_basename']=None
            rows[row['pid']]=row
        except (ValueError,IndexError):
            unreadable+=1
    return rows,unreadable


def cgroup_receipt(pid):
    text=read_text(f'/proc/{pid}/cgroup')
    v2=next((line[3:] for line in (text or '').splitlines() if line.startswith('0::')),None)
    if v2 is None:
        return {'status':'CGROUP_V2_UNAVAILABLE_OR_UNREADABLE'}
    mount=Path('/sys/fs/cgroup')
    ancestors=cgroup_ancestors(v2,mount)
    if not ancestors:
        return {'status':'CGROUP_PATH_UNRESOLVED_DO_NOT_ASSUME_UNLIMITED'}
    entries=[]
    for path in ancestors:
        row={'relative_path_sha256':hashlib.sha256(str(path.relative_to(mount)).encode()).hexdigest()}
        for name in ('cpu.max','cpu.stat','memory.max','memory.high','memory.current',
                     'memory.events','cpuset.cpus.effective','pids.current','pids.max'):
            row[name]=read_text(path/name)
        entries.append(row)
    return {'status':'VISIBLE_V2_ANCESTORS_READ',
            'membership_sha256':hashlib.sha256(v2.encode()).hexdigest(),
            'namespace_caveat':'Host ancestors outside this namespace may be hidden.',
            'ancestors_leaf_to_visible_root':entries}


def host_snapshot():
    memory={}
    for line in (read_text('/proc/meminfo') or '').splitlines():
        k,v=line.split(':',1)
        if k in ('MemTotal','MemAvailable','SwapTotal','SwapFree'):
            memory[k]=int(v.split()[0])*1024
    cpu_line=next((x for x in (read_text('/proc/stat') or '').splitlines() if x.startswith('cpu ')),None)
    return {'affinity_count_sampler':len(os.sched_getaffinity(0)),
            'meminfo_bytes':memory, 'host_cpu_ticks':cpu_line,
            'pressure':{kind:read_text(f'/proc/pressure/{kind}') for kind in ('cpu','memory','io')},
            'sampler_cgroup':cgroup_receipt(os.getpid())}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True,help='new JSON file; parent directory must exist')
    parser.add_argument('--session',action='append',default=[],help='known root PID:label, repeat for each session')
    parser.add_argument('--samples',type=int,default=3)
    parser.add_argument('--interval',type=float,default=10.0)
    args=parser.parse_args(argv)
    if not 2<=args.samples<=60 or not 0.1<=args.interval<=300:
        parser.error('samples must be 2..60 and interval 0.1..300 seconds')
    out=Path(args.out)
    if out.exists() or not out.parent.is_dir():
        parser.error('output must be new and its parent directory must already exist')
    explicit={}
    for value in args.session:
        try:
            pid,label=value.split(':',1); pid=int(pid)
            if pid<=0 or not re.fullmatch(r'[A-Za-z0-9_.-]{1,60}',label): raise ValueError()
            explicit[pid]=label
        except ValueError:
            parser.error('--session requires positive PID and safe alphanumeric label')
    rows,missed=process_snapshot()
    for row in rows.values():
        if 'codex' in (row.get('exe_basename') or '').lower(): row['comm']='codex'
    roots=explicit or {p:f'codex_{i+1}' for i,p in enumerate(roots_of_process_tree(rows))}
    result={'schema':'READ_ONLY_MULTISESSION_RESOURCE_INVENTORY_V1',
            'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'host_kind':'UNVERIFIED_EXECUTION_HOST', 'resource_mutations':False,
            'science_launched':False, 'read_sensitive_args_or_environment':False,
            'discovery_mode':'EXPLICIT_PIDS' if explicit else 'ADVISORY_CODEX_NAME_DISCOVERY',
            'roots':roots,'roots_observed_at_start':len(roots), 'unreadable_process_entries_at_start':missed,
            'limitations':['Auto-discovery cannot guarantee exactly the three user sessions.',
                          'Processes born or gone between samples are not fully charged.',
                          'Summed RSS double-counts shared pages; use isolated memory.current or PSS for admission.',
                          'Shared cgroup counters are not attributable to a single job.',
                          'Unknown or hidden cgroup limits are not treated as unlimited.'],
            'samples':[]}
    hz=os.sysconf('SC_CLK_TCK'); previous=None; previous_t=None
    for index in range(args.samples):
        if index: time.sleep(args.interval)
        now=time.monotonic(); rows,_=process_snapshot(); sessions=[]
        for root,label in roots.items():
            members=descendants(rows,root)
            cores=None if previous is None else interval_cores(previous,rows,members,now-previous_t,hz)
            sessions.append({'label':label,'root_pid':root,'root_present':root in rows,
                'process_count':len(members),'thread_count':sum(rows[p]['threads'] for p in members),
                'rss_sum_bytes_not_unique_memory':sum(rows[p]['rss_bytes'] for p in members),
                'interval_cpu_core_equivalents_partial':cores,
                'cgroup':cgroup_receipt(root) if root in rows else None})
        top=[]
        if previous is not None:
            for pid,row in rows.items():
                core=interval_cores(previous,rows,{pid},now-previous_t,hz)
                if core>0:
                    top.append({'pid':pid,'ppid':row['ppid'],'comm':row['comm'],
                                'cpu_core_equivalents':core,'rss_bytes':row['rss_bytes']})
            top=sorted(top,key=lambda x:x['cpu_core_equivalents'],reverse=True)[:20]
        result['samples'].append({'index':index,'monotonic_seconds':now,
            'host':host_snapshot(),'sessions':sessions,'top_cpu_processes_no_argv':top})
        previous,previous_t=rows,now
    with out.open('x') as stream:
        json.dump(result,stream,indent=2,allow_nan=False); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'status':'READ_ONLY_INVENTORY_WRITTEN','path':str(out),
                      'session_roots':len(roots),'science_launched':False}))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
