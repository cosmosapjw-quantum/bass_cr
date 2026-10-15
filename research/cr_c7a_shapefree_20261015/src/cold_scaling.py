"""Fair cold-process timing: each trial launches a fresh Python interpreter.

This is component preparation/reconstruction timing, NOT a whole native RT solver.
"""
import argparse, subprocess,sys,json,os,statistics,time


def one(workers,nq):
    from source_subcells import source_quadrature,reference_edges
    from parallel_moments import parallel_enclose_q_bins
    t=__import__('time').perf_counter()
    q=source_quadrature(nq);N,U=q.number_and_energy()
    result=parallel_enclose_q_bins(reference_edges(nq),N*4.298036114764196e-8,U*4.298036114764196e-8,1.,
        (.0017575700008892194,.0001429214010766023,0.),1e10,4,workers)
    seconds=__import__('time').perf_counter()-t
    print(json.dumps({'workers':workers,'seconds':seconds,'nq':nq,'heI_event_lower':result['event'][1,0],'heI_event_upper':result['event'][1,1]}))


def outer(nq,reps=3):
    rows=[]
    for w in (1,2,4):
        r=[]
        for _ in range(reps):
            cp=subprocess.run([sys.executable,__file__,'--child','--bins',str(nq),'--workers',str(w)],
                              capture_output=True,text=True,timeout=120)
            if cp.returncode:raise RuntimeError(cp.stderr[:1000])
            r.append(json.loads(cp.stdout))
        assert all(t['heI_event_lower']==r[0]['heI_event_lower'] and t['heI_event_upper']==r[0]['heI_event_upper'] for t in r)
        rows.append({'workers':w,'median_s':statistics.median(x['seconds'] for x in r),
                     'runs_s':[x['seconds'] for x in r], 'same_dyadic_output':True})
    return {'nq':nq,'repetitions':reps,'cold_worker_processes_each_trial':True,'rows':rows}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bins',type=int,default=512);p.add_argument('--reps',type=int,default=3)
    p.add_argument('--child',action='store_true');p.add_argument('--workers',type=int,default=1)
    a=p.parse_args()
    if a.child:one(a.workers,a.bins)
    else:print(json.dumps(outer(a.bins,a.reps),indent=2))
