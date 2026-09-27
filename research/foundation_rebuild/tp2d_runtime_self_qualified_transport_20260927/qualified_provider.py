from __future__ import annotations
from dataclasses import dataclass
import hashlib,json,os,tempfile
from pathlib import Path
import numpy as np

CROSS_KEYS=('S_tp','S_pt','H_tp','H_pt','D_tp','D_pt')

class ResolutionQualificationError(RuntimeError):
    pass

class OperatorQueryBudgetExceeded(RuntimeError):
    pass

@dataclass(frozen=True)
class QualifiedSnapshot:
    t: float
    S: np.ndarray
    H: np.ndarray
    D: np.ndarray
    diagnostics: dict
    qualification: dict
    identity: str


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _atomic_file(path,writer):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.partial_',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            writer(f);f.flush();os.fsync(f.fileno())
        os.link(tmp,path)
        dfd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def _relative(a,b):
    a=np.asarray(a);b=np.asarray(b)
    den=max(float(np.linalg.norm(a)),float(np.linalg.norm(b)),1e-300)
    return float(np.linalg.norm(a-b)/den)


def _raw_difference(a,b):
    detail={};value=0.0
    for key in CROSS_KEYS:
        x=_relative(a[key],b[key]);detail[key]=x;value=max(value,x)
    return value,detail


def _screen_full(full,screens):
    S=np.asarray(full['S'],complex);H=np.asarray(full['H'],complex);D=np.asarray(full['D'],complex)
    if S.ndim!=2 or S.shape[0]!=S.shape[1] or H.shape!=S.shape or D.shape!=S.shape:
        raise ResolutionQualificationError('operator shape mismatch')
    if not all(np.isfinite(a).all() for a in (S,H,D)):
        raise ResolutionQualificationError('nonfinite full operator')
    sdef=float(np.linalg.norm(S-S.conj().T)/max(float(np.linalg.norm(S)),1e-300))
    hdef=float(np.linalg.norm(H-H.conj().T)/max(float(np.linalg.norm(H)),1e-300))
    ev=np.linalg.eigvalsh((S+S.conj().T)/2)
    ratio=float(ev[0]/ev[-1]) if ev[-1]>0 else -1.0
    return {
        'S_hermiticity_relative':sdef,
        'H_hermiticity_relative':hdef,
        'hermiticity_relative_max':max(sdef,hdef),
        'hermiticity_pass':max(sdef,hdef)<=float(screens['operator_hermiticity_relative_max']),
        'metric_min':float(ev[0]),'metric_max':float(ev[-1]),'metric_ratio':ratio,
        'metric_pass':ratio>=float(screens['metric_min_ratio']),
    }


class ResolutionQualifiedProvider:
    def __init__(self,*,evaluate,resolutions,screens,context_id,out_dir=None,max_unique_queries=2048,on_qualified=None):
        if not callable(evaluate):raise ValueError('callable evaluator required')
        if not isinstance(resolutions,list) or len(resolutions)<2:raise ValueError('at least two finite resolutions required')
        norm=[];seen=set()
        for row in resolutions:
            q=row.get('order');h=row.get('subdivisions')
            if type(q) is not int or not 2<=q<=64:raise ValueError('bounded order required')
            if type(h) is not int or h not in (1,2,4):raise ValueError('subdivisions must be 1,2,4')
            pair=(q,h)
            if pair in seen:raise ValueError('duplicate resolution rule')
            seen.add(pair);norm.append({'order':q,'subdivisions':h})
        for key in ('raw_cross_relative_max','operator_hermiticity_relative_max','metric_min_ratio'):
            if key not in screens or not np.isfinite(screens[key]) or float(screens[key])<=0:raise ValueError('positive finite screen required: '+key)
        if type(max_unique_queries) is not int or max_unique_queries<1:raise ValueError('positive query budget required')
        if not isinstance(context_id,str) or not context_id:raise ValueError('context identity required')
        self.evaluate=evaluate;self.resolutions=tuple(norm);self.screens=dict(screens);self.context_id=context_id
        self.out_dir=Path(out_dir).resolve() if out_dir is not None else None
        if on_qualified is not None and not callable(on_qualified):raise ValueError('on_qualified must be callable')
        self.on_qualified=on_qualified;self.identity=context_id
        self.max_unique_queries=max_unique_queries;self._cache={}
        self.unique_query_count=0;self.raw_operator_evaluation_count=0;self.restored_query_reads=0;self.cache_hits=0

    def _query_id(self,t):
        obj={'schema':'BASS_TP2D_RUNTIME_QUERY_V1','context_id':self.context_id,'time_hex':float(t).hex()}
        return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def _paths(self,qid):
        if self.out_dir is None:return None,None
        base=self.out_dir/'runtime_queries'/qid
        return base.with_suffix('.json'),base.with_suffix('.npz')

    def _load(self,t,qid):
        jp,npz=self._paths(qid)
        if jp is None or not jp.exists() or not npz.exists():return None
        rec=json.loads(jp.read_text())
        if rec.get('schema')!='BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1' or rec.get('query_id')!=qid or rec.get('context_id')!=self.context_id or rec.get('time_hex')!=float(t).hex():
            raise ResolutionQualificationError('stored runtime query identity mismatch')
        if _sha(npz)!=rec.get('payload_sha256'):raise ResolutionQualificationError('stored runtime query payload hash mismatch')
        with np.load(npz,allow_pickle=False) as f:
            S=np.array(f['selected__S']);H=np.array(f['selected__H']);D=np.array(f['selected__D'])
        q=rec['qualification'];diag=rec['selected_diagnostics']
        self.restored_query_reads+=1
        return QualifiedSnapshot(float(t),S,H,D,diag,q,qid)

    def _save(self,t,qid,snapshot,attempt_payload,attempts):
        jp,npz=self._paths(qid)
        if jp is None:return
        arrays={'selected__S':snapshot.S,'selected__H':snapshot.H,'selected__D':snapshot.D}
        arrays.update(attempt_payload)
        _atomic_file(npz,lambda f:np.savez_compressed(f,**arrays))
        rec={
            'schema':'BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1','query_id':qid,'context_id':self.context_id,
            'time_hex':float(t).hex(),'qualification':snapshot.qualification,'selected_diagnostics':snapshot.diagnostics,
            'attempts':attempts,'payload_sha256':_sha(npz),'capture_execution_allowed':False,
            'continuous_global_supremum_bound':False,
        }
        data=(json.dumps(rec,indent=2,allow_nan=False)+'\n').encode()
        _atomic_file(jp,lambda f:f.write(data))

    def audit_summary(self):
        hist={};maxdiff=0.0
        for snap in self._cache.values():
            r=snap.qualification['selected_resolution'];tag=f"q{r['order']}_h{r['subdivisions']}"
            hist[tag]=hist.get(tag,0)+1
            maxdiff=max(maxdiff,float(snap.qualification['max_raw_cross_relative_difference']))
        return {
            'all_runtime_operator_queries_qualified':len(self._cache)==self.unique_query_count,
            'unique_runtime_queries':int(self.unique_query_count),
            'qualified_runtime_queries':len(self._cache),
            'raw_operator_evaluations':int(self.raw_operator_evaluation_count),
            'restored_query_reads':int(self.restored_query_reads),
            'cache_hits':int(self.cache_hits),
            'max_selected_raw_cross_relative_difference':float(maxdiff),
            'resolution_histogram':dict(sorted(hist.items())),
            'continuous_global_supremum_bound':False,
        }

    def at(self,t):
        t=float(t)
        if not np.isfinite(t):raise ValueError('finite time required')
        key=np.float64(t).tobytes()
        if key in self._cache:
            self.cache_hits+=1;return self._cache[key]
        if self.unique_query_count>=self.max_unique_queries:
            raise OperatorQueryBudgetExceeded('runtime operator query budget exhausted')
        self.unique_query_count+=1
        qid=self._query_id(t)
        restored=self._load(t,qid)
        if restored is not None:
            self._cache[key]=restored
            if self.on_qualified is not None:
                self.on_qualified({'event':'runtime_query_qualified','time_hex':float(t).hex(),'query_id':qid,
                    'restored':True,'selected_resolution':restored.qualification['selected_resolution'],
                    'max_raw_cross_relative_difference':restored.qualification['max_raw_cross_relative_difference'],
                    'unique_runtime_queries':self.unique_query_count,'raw_operator_evaluations':self.raw_operator_evaluation_count})
            return restored
        previous=None;attempts=[];payload={}
        for rule in self.resolutions:
            raw,full=self.evaluate(t,rule['order'],rule['subdivisions']);self.raw_operator_evaluation_count+=1
            if set(CROSS_KEYS)-set(raw):raise ResolutionQualificationError('cross operator keys missing')
            if any(not np.isfinite(np.asarray(raw[k])).all() for k in CROSS_KEYS):raise ResolutionQualificationError('nonfinite cross operator')
            diag=_screen_full(full,self.screens)
            tag=f"q{rule['order']}_h{rule['subdivisions']}"
            for k in CROSS_KEYS:payload[f'{tag}__{k}']=np.asarray(raw[k],complex)
            row={'resolution':dict(rule),'diagnostics':diag,'previous_raw_cross_relative_max':None,
                 'previous_raw_cross_relative_differences':None,'raw_cross_convergence_pass':None}
            if previous is not None:
                diff,detail=_raw_difference(previous['raw'],raw)
                row['previous_raw_cross_relative_max']=diff;row['previous_raw_cross_relative_differences']=detail
                row['raw_cross_convergence_pass']=diff<=float(self.screens['raw_cross_relative_max'])
                pdiag=previous['diagnostics']
                if (pdiag['hermiticity_pass'] and pdiag['metric_pass'] and diag['hermiticity_pass'] and diag['metric_pass'] and row['raw_cross_convergence_pass']):
                    qualification={'status':'RUNTIME_QUERY_QUALIFIED','lower_resolution':previous['resolution'],
                        'selected_resolution':dict(rule),'max_raw_cross_relative_difference':diff,
                        'raw_cross_relative_differences':detail,
                        'evidence_relation':'INDEPENDENT_NUMERICAL_RESOLUTION_COMPARISON'}
                    snap=QualifiedSnapshot(t,np.asarray(full['S'],complex),np.asarray(full['H'],complex),np.asarray(full['D'],complex),diag,qualification,qid)
                    attempts.append(row);self._save(t,qid,snap,payload,attempts);self._cache[key]=snap
                    if self.on_qualified is not None:
                        self.on_qualified({'event':'runtime_query_qualified','time_hex':float(t).hex(),'query_id':qid,
                            'restored':False,'selected_resolution':qualification['selected_resolution'],
                            'max_raw_cross_relative_difference':qualification['max_raw_cross_relative_difference'],
                            'unique_runtime_queries':self.unique_query_count,'raw_operator_evaluations':self.raw_operator_evaluation_count})
                    return snap
            attempts.append(row);previous={'resolution':dict(rule),'raw':raw,'diagnostics':diag}
        raise ResolutionQualificationError('finite resolution ladder exhausted without qualified adjacent pair')

def restore_query_store(source_dir,destination_dir,context_id):
    source=Path(source_dir).resolve()/'runtime_queries';destination=Path(destination_dir).resolve()/'runtime_queries'
    if not source.exists():return 0
    count=0
    for jp in sorted(source.glob('*.json')):
        qid=jp.stem;npz=source/(qid+'.npz')
        if not npz.is_file():raise ResolutionQualificationError('resume query payload missing')
        rec=json.loads(jp.read_text())
        if rec.get('schema')!='BASS_TP2D_QUALIFIED_RUNTIME_QUERY_V1' or rec.get('query_id')!=qid or rec.get('context_id')!=context_id:
            raise ResolutionQualificationError('resume query identity mismatch')
        if _sha(npz)!=rec.get('payload_sha256'):
            raise ResolutionQualificationError('resume query payload hash mismatch')
        _atomic_file(destination/(qid+'.npz'),lambda f,npz=npz:f.write(npz.read_bytes()))
        _atomic_file(destination/(qid+'.json'),lambda f,jp=jp:f.write(jp.read_bytes()))
        count+=1
    return count
