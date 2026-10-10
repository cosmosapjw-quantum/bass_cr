"""One frozen campaign; preserve first execution and never overwrite evidence."""
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import signal
import sys
import time
import numpy as np
import scipy
import response as r

def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else r.ROOT / 'evidence/VALIDATION.json'
    if output.exists():
        raise FileExistsError('Existing evidence must be preserved')
    output.parent.mkdir(parents=True, exist_ok=True)
    wall, cpu = time.monotonic(), time.process_time()
    def timeout(signum, frame):
        raise TimeoutError('CAMPAIGN_WALL_LIMIT_600S')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(600)
    result = {'id': 'CR-PHYS02C-CONDITIONAL-CROSSING-RESPONSE01',
              'status': 'RUNNING', 'command': [sys.executable, *sys.argv],
              'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
              'source_sha256': {str(p.relative_to(r.ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (r.P_PATH, r.ROOT/'CONTRACT.json', r.ROOT/'response.py', r.ROOT/'validate.py')},
              'harness': 'HARNESS_UNAVAILABLE', 'nonzero_evolve_calls': 0,
              'histories': [], 'checks': {}, 'global_scientific_admission': 'HOLD'}
    try:
        T = 1e11
        def evolve(g, steps, method='sparse'):
            if result['nonzero_evolve_calls'] >= 8:
                raise ValueError('EVOLVE_CALL_LIMIT')
            result['nonzero_evolve_calls'] += 1
            y0 = r.initial(g)
            y = (r.P.evolve_ssprk2(g, y0, T, steps) if method == 'ssprk2'
                 else r.P.evolve(g, y0, T, steps=steps))
            rows = r.observe(g, y)
            result['histories'].append({'grid_intervals': g.n-1, 'quadrature': g.quadrature_order,
                                       'steps': steps, 'method': method, 'age_s': T, 'columns': rows})
            return y
        generators = [r.P.assemble(n) for n in (128,256,512)]
        zero_checks = []
        for g in generators:
            y0 = r.initial(g)
            zero_checks.append(np.array_equal(r.P.evolve(g, y0, 0), y0)
                               and np.array_equal(r.P.evolve(g, y0, T, enabled=False), y0)
                               and np.all(y0[g.n:] == 0))
            result['histories'].append({'grid_intervals': g.n-1, 'age_s': 0, 'columns': r.observe(g,y0)})
        ys = [evolve(g,64) for g in generators]
        cs = [r.channels(g,y) for g,y in zip(generators,ys)]
        gd = [float(np.max(np.abs(b-a))/r.E0) for a,b in zip(cs[:-1],cs[1:])]
        result['grid_refinement'] = {'differences_over_E0': gd}
        result['checks']['grid'] = gd[1] <= .02 and gd[1] < gd[0]
        g = generators[0]
        y128, y256 = evolve(g,128), evolve(g,256)
        nref = max(256, math.ceil(T*g.rho/.2))
        if nref > 4096:
            raise ValueError(f'REFERENCE_STAGE_BUDGET:{nref}')
        ref = evolve(g,nref,'ssprk2')
        cref = r.channels(g,ref)
        td = [float(np.max(np.abs(r.channels(g,y)-cref))/r.E0) for y in (ys[0],y128,y256)]
        result['time_refinement'] = {'stages': [64,128,256], 'reference_stages': nref,
                                     'reference_method': 'SSPRK2', 'differences_over_E0': td}
        result['checks']['time'] = td[-1] <= 2e-4 and td[-1] < td[1] < td[0]
        gq = r.P.assemble(128,quadrature_order=12)
        yq = evolve(gq,64)
        qd = float(np.max(np.abs(r.channels(gq,yq)-cs[0]))/r.E0)
        result['quadrature_refinement'] = {'orders':[8,12], 'difference_over_E0': qd}
        result['checks']['quadrature'] = qd <= 1e-8
        rows = [row for h in result['histories'] for row in h['columns']]
        ne = max(abs(row['number_ledger']-1) for row in rows)
        ee = max(abs(row['combined_energy_ledger_eV']/r.E0-1) for row in rows)
        result['ledger'] = {'maximum_number_absolute_error':ne, 'maximum_energy_relative_error':ee}
        result['checks']['ledger'] = ne <= 2e-11 and ee <= 2e-11
        result['checks']['finite_nonnegative'] = all(np.all(np.isfinite(y)) and np.all(y>=0)
                                                      for y in (*ys,y128,y256,ref,yq))
        result['checks']['t0_OFF'] = all(zero_checks)
        result['status'] = 'PASS_SCOPED' if all(result['checks'].values()) else 'FAIL'
    except Exception as e:
        result.update(status='FAIL', first_failure=f'{type(e).__name__}: {e}')
    finally:
        signal.alarm(0)
    result['measured_process_wall_s'] = time.monotonic()-wall
    result['measured_process_cpu_s'] = time.process_time()-cpu
    result['unmeasured_overhead'] = 'UNKNOWN_NOT_ZERO'
    result['exit_code'] = 0 if result['status']=='PASS_SCOPED' else 1
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='histories'},indent=2))
    return result['exit_code']

if __name__ == '__main__':
    raise SystemExit(main())
