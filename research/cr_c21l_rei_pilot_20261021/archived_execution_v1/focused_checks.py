"""Small falsifiable contract checks; no performance benchmark or old suite."""
import os
for _k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[_k]='1'
import dataclasses,hashlib,json,math,traceback
from pathlib import Path
import numpy as np
from adapter import HERE,verify_source,make_template,map_case,normalized,solve_case,G_SI,C_SI
from resources import capacity,acquire_cpu
from runner import write_new,resume_status

def main():
    out=HERE/'checks';out.mkdir(exist_ok=False);records=[]
    def check(name,fn):
        try:
            details=fn();records.append({'name':name,'status':'PASS','details':details});print(name,'PASS',flush=True)
        except BaseException:
            records.append({'name':name,'status':'FAILED','error':traceback.format_exc()});print(name,'FAILED',flush=True)
    def sources():return {'immutable_files_verified':len(verify_source()['files'])}
    check('source_byte_identity',sources)
    def normalizations():
        d={'s':.03,'H':.8,'Pi_gamma_J_m3':2.,'Pi_nu_J_m3':-1.5,'Pi_matter_J_m3':-.5}
        z=normalized(d);assert z['P']==0. and z['Pi_F']==0.
        sigma=np.diag([-.03,-.03,.06]);assert math.isclose(z['Sigma_F'],np.linalg.norm(sigma)/.8,rel_tol=2e-16)
        d['Pi_matter_J_m3']=-.4;z=normalized(d)
        p=.1;assert math.isclose(z['Pi_F'],(8*math.pi*G_SI/C_SI**2)*np.linalg.norm(np.diag([-p,-p,2*p]))/.8**2,rel_tol=3e-15)
        assert z['Sigma_half']==z['Sigma_F']/math.sqrt(2)
        return {'signed_stress_cancellation':True,'c_squared_and_Frobenius_checked':True}
    check('normalizations_signed_cancellation',normalizations)
    base=make_template(False);opt=make_template(True)
    def independence():
        a,ma=map_case(opt,-.04,.001);b,mb=map_case(opt,.01,-.001)
        assert a is not b and a.momentum is b.momentum
        assert a.energy_matrix is b.energy_matrix and not a.energy_matrix.flags.writeable
        ya=a.initial_state();yb=b.initial_state();original=yb.copy();ya[4]=99
        assert not np.shares_memory(ya,yb) and np.array_equal(yb,original)
        assert opt.k_gamma==0. and opt.Sigma_ref==0. and opt._nfev==0
        return {'shared_immutable_operators':True,'independent_state_arrays':True,'state_width':len(ya)}
    check('template_independence',independence)
    def moments():
        coords=[(0.,0.),(.2,.001),(math.log(4.2),-.04),(1.,.04)]
        for eta,b in coords:
            a=np.array(dataclasses.astuple(base.momentum.moments(eta,b)))
            z=np.array(dataclasses.astuple(opt.momentum.moments(eta,b)))
            assert np.array_equal(a.view(np.uint64),z.view(np.uint64)),(eta,b,a-z)
        return {'bitwise_samples':coords}
    check('moment_common_subexpression_bitwise',moments)
    def solutions():
        results=[]
        for i,(s,p) in enumerate([(-.04,.001),(0.,0.),(.02,-.00075)]):
            a,ha=solve_case(base,s,p);b,hb=solve_case(opt,s,p)
            np.savez_compressed(out/('baseline_pair_%d.npz'%i),**{'baseline_'+k:v for k,v in ha.items()},**{'reuse_'+k:v for k,v in hb.items()})
            assert ha.keys()==hb.keys()
            errors={k:float(np.max(np.abs(ha[k]-hb[k]))) for k in ha}
            assert all(np.array_equal(ha[k].view(np.uint64),hb[k].view(np.uint64)) for k in ha),errors
            results.append({'S0':s,'P0':p,'all_full_history_arrays_bitwise_equal':True,'max_abs_difference':max(errors.values()),'nfev':a['nfev'],'diagnostics':b['diagnostics']})
        return results
    check('three_full_baseline_vs_reuse_solutions',solutions)
    def resource_math():
        snap={'allowed_cpus':[1,2,3,4,55],'quota':3.9,'memory_limit':8*1024**3,'memory_available':6*1024**3}
        c=capacity(snap,4);assert 55 not in c['cpu_candidates'] and c['maximum_workers']==2
        assert capacity(snap,4,{1,2,55})['maximum_workers']==1
        low=dict(snap,memory_available=1024**3);assert capacity(low,4)['maximum_workers']==0
        lease=out/'lease_test';lease.mkdir();a=acquire_cpu(lease,1)
        try:
            assert acquire_cpu(lease,1) is None
            b=acquire_cpu(lease,2);assert b is not None;b.close()
        finally:a.close()
        b=acquire_cpu(lease,1);assert b is not None;b.close()
        return {'quota_includes_coordinator':True,'memory_floor':True,'CPU55_excluded':True,'held_lease_skipped':True}
    check('resource_arithmetic_and_lease',resource_math)
    def resume():
        d=out/'resume_test';assert resume_status(d,'same')=='MISSING';d.mkdir();write_new(d/'RESERVATION.json',{'identity':'same'});assert resume_status(d,'same')=='INCOMPLETE'
        try:resume_status(d,'different')
        except RuntimeError:pass
        else:raise AssertionError('identity accepted')
        h=d/'history.npz';h.write_bytes(b'test history fixture')
        write_new(d/'RESULT.json',{'identity':'same','status':'COMPLETE','history_sha256':hashlib.sha256(h.read_bytes()).hexdigest()})
        assert resume_status(d,'same')=='COMPLETE';h.write_bytes(b'changed')
        try:resume_status(d,'same')
        except RuntimeError:pass
        else:raise AssertionError('changed completed history accepted')
        failed=out/'failed_fixture';failed.mkdir();write_new(failed/'RESERVATION.json',{'identity':'same'});write_new(failed/'RESULT.json',{'identity':'same','status':'FAILED'});assert resume_status(failed,'same')=='FAILED'
        return {'completed_only_resume':True,'identity_mismatch_rejected':True,'partial_explicit':True,'failed_not_retried':True}
    check('partial_result_resume_identity',resume)
    result={'status':'PASS' if all(r['status']=='PASS' for r in records) else 'FAILED','checks':records,'scope':'focused implementation parity/resource/recovery checks; no convergence or global certification claim','global_error_bound':None}
    write_new(out/'CHECKS.json',result);print(json.dumps(result,indent=2));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
