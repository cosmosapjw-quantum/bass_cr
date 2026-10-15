"""Compare exactly the same dyadic packet-moment queries with/without prefix sums."""
import json,time,random
from bisect import bisect_left
from fractions import Fraction
from adaptive_benchmark import current_packets


def slow_moments(oracle,a,b):
    n=u=Fraction(0)
    for E,N in zip(oracle.energies,oracle.counts):
        if a<=E<b:
            n+=N;u+=N*E
    return n,u


def run(queries=150,repeat=3):
    o,_,_,_=current_packets(True)
    rng=random.Random(12)
    cuts=[Fraction.from_float(13.6+i*410/256) for i in range(257)]
    pairs=[(cuts[rng.randrange(0,256)],cuts[rng.randrange(1,257)]) for _ in range(queries)]
    pairs=[(min(a,b),max(a,b)) for a,b in pairs if a!=b]
    numbers=[]
    for _ in range(repeat):
        t=time.perf_counter();ref=[slow_moments(o,a,b) for a,b in pairs];s=time.perf_counter()-t
        t=time.perf_counter();fast=[o.moments(a,b) for a,b in pairs];q=time.perf_counter()-t
        assert ref==fast
        numbers.append((s,q))
    return {'packets':len(o.energies),'queries':len(pairs),'median_scan_s':sorted(t[0] for t in numbers)[repeat//2],
            'median_prefix_s':sorted(t[1] for t in numbers)[repeat//2],
            'speedup':sorted(t[0] for t in numbers)[repeat//2]/sorted(t[1] for t in numbers)[repeat//2],
            'exact_fraction_results_identical':True}

if __name__=='__main__':print(json.dumps(run(),indent=2))
