"""Identity-bound qualified query cache. This module has no evaluator fallback."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import numpy as np
import bootstrap_runtime
from execution_admission import strict_json
from parallel_bridge import PlannedQuery,validate_pair
from solver_plan import validate_plan,digest
from cache_consistency import validate_cached_cross_binding

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class QualifiedCache:
    def __init__(self,directory,plan):
        self.directory=Path(directory).resolve();self.plan=validate_plan(plan)
        self.identity=plan['context_id'];self.native_calls=0;self.reads=0;self._cache={}
        self.by_time={q['time_hex']:q for q in plan['queries']}
        self.records={}
        for query in plan['queries']:
            item=PlannedQuery(query['query_id'],query['time_hex'],query['step'],None)
            rec=validate_pair(self.directory,item,self.identity,plan['qualification_contract'])
            validate_cached_cross_binding(self.directory,item.query_id)
            self.records[item.query_id]=rec
        self.manifest={'schema':'BASS_PRODUCTION_CANDIDATE_CACHE_MANIFEST_V1',
                       'plan_sha256':plan['plan_sha256'],'context_id':self.identity,
                       'records':[self.records[q['query_id']] for q in plan['queries']],
                       'native_calls':0,'operator_interpolation_used':False}
        self.manifest_sha256=digest(self.manifest)

    def at(self,t):
        th=float(t).hex()
        if th not in self.by_time:raise KeyError('exact cache miss; native fallback forbidden: '+th)
        qid=self.by_time[th]['query_id']
        if th not in self._cache:
            rec=self.records[qid];jp=self.directory/(qid+'.json');npz=self.directory/(qid+'.npz')
            if sha(jp)!=rec['json_sha256'] or sha(npz)!=rec['payload_sha256']:
                raise ValueError('qualified cache changed after admission: '+qid)
            row=strict_json(jp)
            with np.load(npz,allow_pickle=False) as data:
                arrays=[np.array(data['selected__'+key],dtype=complex) for key in ('S','H','D')]
            for a in arrays:a.setflags(write=False)
            self._cache[th]=SimpleNamespace(t=float(t),S=arrays[0],H=arrays[1],D=arrays[2],
                                           identity=qid,qualification=row['qualification'])
            self.reads+=1
        return self._cache[th]
