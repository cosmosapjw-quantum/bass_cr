"""Timing script executed as module file: forkserver requires __main__ guard."""
import argparse,json,time
from source_subcells import source_quadrature,reference_edges
from parallel_moments import parallel_enclose_q_bins

RHO=(.0017575700008892194,.0001429214010766023,0.)
SOURCE=4.298036114764196e-8

def measure(n=512,reps=3):
    q=source_quadrature(n)
    x,u=q.number_and_energy()
    ed=reference_edges(n)
    res=[]
    ref=None
    for w in (1,2,4):
        elapsed=[];output=None
        for _ in range(reps):
            t=time.perf_counter()
            output=parallel_enclose_q_bins(ed,x*SOURCE,u*SOURCE,1.,RHO,1e10,4,w)
            elapsed.append(time.perf_counter()-t)
            if ref is not None:
                assert (output['event']==ref['event']).all()
                assert (output['heat']==ref['heat']).all()
        if ref is None:ref=output
        res.append(dict(workers=w,median_s=sorted(elapsed)[len(elapsed)//2],
                        min_s=min(elapsed),max_s=max(elapsed),
                        same_dyadic_endpoints=True))
    return dict(nq=n,repeats=reps,rows=res)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bins',type=int,default=512);p.add_argument('--reps',type=int,default=2)
    x=p.parse_args()
    print(json.dumps(measure(x.bins,x.reps),indent=2))
