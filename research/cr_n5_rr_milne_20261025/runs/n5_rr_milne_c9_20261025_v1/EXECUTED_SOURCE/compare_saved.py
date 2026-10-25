"""Complete the prescribed conditional kinetic-energy comparisons from saved rows."""
import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

def main(unit,out,runid):
    start=time.process_time()
    if runid!='n5_rr_milne_kinetic_comparison_20261025_v1':
        raise ValueError('RUN_ID_MISMATCH')
    c=json.loads((unit/'inputs/CONFIG.json').read_text())
    primary=unit/'runs'/c['primary_run_id']
    originals={name:hashlib.sha256((primary/name).read_bytes()).hexdigest() for name in ['RESULT.json','SOURCE_WEIGHTED_RESULTS.json']}
    rows=json.loads((primary/'SOURCE_WEIGHTED_RESULTS.json').read_text())['rows']
    def find(chi,R,N,z):
        return next(v for v in rows if (v['chi'],v['R'],v['N'],v['z'])==(chi,R,N,z))
    comparisons=[]
    for chi,z in itertools.product(c['chi'],c['source_z']):
        pairs=[('grid',find(chi,R,1024,z),find(chi,R,2048,z)) for R in c['R']]
        pairs.append(('boundary',find(chi,40,2048,z),find(chi,80,2048,z)))
        for kind,a,b in pairs:
            key='conditional_RR_kinetic_eV'
            scale=max(abs(a[key]),abs(b[key]));relative=abs(a[key]-b[key])/scale if scale else 0.0
            tol=c['tolerances'][kind]
            comparisons.append(dict(chi=chi,z=z,kind=kind,observable=key,a_case=a['case'],b_case=b['case'],relative_difference=relative,tolerance=tol,pass_scoped=relative<=tol))
    assert len(comparisons)==18
    after={name:hashlib.sha256((primary/name).read_bytes()).hexdigest() for name in originals}
    assert originals==after
    result=dict(schema='N5_RR_SAVED_KINETIC_COMPLETION_V1',status='PASS' if all(r['pass_scoped'] for r in comparisons) else 'FAILED_RETAINED',run_id=runid,comparisons=comparisons,original_primary_hashes_before=originals,original_primary_hashes_after=after,implementation_obligation='Conditional RR kinetic r_RR/p_RR comparison completed additively; original162 comparisons and RESULT unchanged',threshold_provenance='original frozen grid.005/boundary1e-5, no changed tolerance',new_RHS=0,quadrature=0,old_replay=0,process_cpu_s=time.process_time()-start,EXECUTION='COMPLETED',PUBLICATION='ROOT_OWNED',BACKUP='ROOT_PENDING',DAG='N5_PARTIAL_OPEN')
    with (out/'RESULT.json').open('x') as f:
        json.dump(result,f,indent=2,allow_nan=False)
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--unit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args();raise SystemExit(main(a.unit,a.output,a.run_id))
