"""Pure resource planning helpers. No process/resource mutation or run authorization."""
from __future__ import annotations
import math

def quota_cores(text: str) -> float:
    values=text.strip().split()
    if len(values)!=2: raise ValueError('cpu.max requires quota and period')
    quota,period=values; period=int(period)
    if period<=0: raise ValueError('positive period required')
    if quota=='max': return math.inf
    quota=int(quota)
    if quota<=0: raise ValueError('positive quota required')
    return quota/period

def effective_cpu_slots(affinity_count: int, quota_texts: list[str], reserve: int=8) -> int:
    if type(affinity_count) is not int or affinity_count<1 or type(reserve) is not int or reserve<0:
        raise ValueError('positive affinity, nonnegative reserve required')
    effective=min([float(affinity_count)]+[quota_cores(x) for x in quota_texts])
    return max(0,math.floor(effective)-reserve)

def memory_worker_cap(cpu_grant: int, memory_grant: float, baseline: float,
                      peak_per_worker: float, safety: float=1.5) -> int:
    # Caller must use the same units for all memory quantities.
    vals=(memory_grant,baseline,peak_per_worker,safety)
    if (type(cpu_grant) is not int or cpu_grant<0 or any(v is None or not math.isfinite(v) for v in vals)
        or memory_grant<0 or baseline<0 or peak_per_worker<=0 or safety<1):
        raise ValueError('explicit positive measured worker peak and valid budgets required')
    return min(cpu_grant,max(0,math.floor((memory_grant-baseline)/(safety*peak_per_worker))))

def roots_of_process_tree(rows: dict[int,dict]) -> list[int]:
    candidates={pid for pid,row in rows.items() if 'codex' in row.get('comm','').lower()}
    roots=[]
    for pid in sorted(candidates):
        seen={pid}; parent=rows[pid]['ppid']; nested=False
        while parent in rows and parent not in seen:
            if parent in candidates: nested=True; break
            seen.add(parent); parent=rows[parent]['ppid']
        if not nested: roots.append(pid)
    return roots
