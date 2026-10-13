"""New source-bound reaction/cutoff crossing witness; no prior suite rerun."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'inputs/prior'))
sys.path.insert(0,str(ROOT))
from kernel_event_adapter import BoundKernel,EV_J,K_B,dot,event_json
from reaction_branch_continuation import AtomicRaw,raw_reaction_state,single_ion_step_for_extent

def exact(v):
    if isinstance(v,Q):return {'exact':str(v),'float':float(v)}
    if isinstance(v,dict):return {str(k):exact(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [exact(x) for x in v]
    return v

def run():
    started=datetime.now(timezone.utc).isoformat()
    kernel=BoundKernel();event=kernel.ion_event(4762,'HI',38)
    cv=Q(3,2)*K_B;alpha=Q(4)*K_B
    chi=Q(4);nbase=Q(10);sstar=Q(1,4)
    w0=EV_J*kernel.Eq[0];lower=EV_J*kernel.cut
    g=event.projection.ghost_count;a0=event.column['A:0']
    assert event.projection.actual_subcut_count==0 and g>0 and a0>0 and g+a0==1
    assert event.column['e_th']==g and event.column['U_th']==g*lower
    u0=(cv/alpha)*w0*nbase-g*(lower-(cv/alpha)*w0)*sstar
    indices=sorted({event.parent,*event.projection.active})
    energies=tuple(EV_J*kernel.Eq[j] for j in indices)
    base={k:Q(0) for k in event.column}
    base.update({'HI':Q(7),'HII':Q(2),'e_th':Q(1),'U_th':u0,f'A:{event.parent}':Q(1)})
    invariants=kernel.invariants(indices)
    assert dot(invariants['charge_over_e'],base)==0
    prior=0;rows=[]
    for extent in (Q(0),Q(1,5),sstar,Q(3,10),Q(1,2)):
        state=raw_reaction_state(base,event.column,extent)
        raw=AtomicRaw(state['HI']+state['HII']+state['e_th'],state['U_th'],energies,
                      tuple(state.get(f'A:{j}',Q(0)) for j in indices),K_B,chi)
        chosen,trace=raw.select_from(prior)
        before=raw.branch(0)
        h=single_ion_step_for_extent(extent,Q(7),event.coefficient)
        f=event.coefficient*(Q(7)-extent)
        reproduced=h*f/(1+h*f*(1+Q(1,7)))
        assert reproduced==extent and chosen['consistent']
        residuals={name:dot(row,state)-dot(row,base) for name,row in invariants.items()}
        assert all(v==0 for v in residuals.values())
        assert chosen['thermal_count']+chosen['active_count']==raw.base_count+sum(raw.weights,Q(0))
        assert chosen['thermal_energy']+chosen['active_energy']==raw.base_energy+sum((w*n for w,n in zip(raw.energies,raw.weights)),Q(0))
        assert cv*chosen['temperature']*chosen['thermal_count']==chosen['thermal_energy']
        assert chosen['cutoff']>=lower
        if extent==0:assert chosen['branch']==0 and lower<chosen['cutoff']<w0
        if extent==Q(1,5):assert raw.branch(0)['consistent'] and raw.branch(1)['consistent']
        if extent==sstar:
            assert before['cutoff']==w0 and not before['consistent']
            assert chosen['branch']==1 and [x['branch'] for x in trace]==[0,1]
            dn=chosen['thermal_count']-before['thermal_count']
            du=chosen['thermal_energy']-before['thermal_energy']
            assert dn==a0*sstar and du==w0*dn
            jump=chosen['temperature']-before['temperature']
            expected=dn*(w0-cv*before['temperature'])/(cv*chosen['thermal_count'])
            assert jump==expected and jump>0
        prior=chosen['branch']
        rows.append({'extent':extent,'h_s':h,'raw_state':state,'zero_branch':before,'selected':chosen,
                     'trace':trace,'invariant_residuals':residuals,'extent_residual':reproduced-extent})
    # Both roots at the same reaction extent demonstrate why the inherited
    # branch is an input; no unqualified global uniqueness is asserted.
    slow=EV_J*event.daughters_eV[0]
    sdown=(w0*cv*nbase-alpha*u0)/(alpha*slow-w0*cv)
    assert 0<sdown<Q(1,5)<sstar
    transversality=alpha*g*lower-w0*cv*g
    assert transversality>0
    # Exact full admitted path 0 <= s <= 1/2 retains the parent and neutral.
    amax=single_ion_step_for_extent(Q(1,2),Q(7),event.coefficient)*event.coefficient
    assert amax<1
    source_paths=['reaction_branch_continuation.py','checks/check_reaction_branch.py',
                  'inputs/prior/kernel_event_adapter.py','inputs/prior/inputs/KERNEL_SOURCE_BINDING.json']
    result={'unit':'CR-THEORY-BRANCH-GEOMETRY-20261013','status':'PASS',
            'scope':'Exact rational event path and branch selection; source coefficient is its finite binary value; no ODE time accuracy or full-kernel history.',
            'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
            'commands':['python3 checks/check_reaction_branch.py'],
            'chi':chi,'background_construction':base,'lower_cutoff_J':lower,'first_node_J':w0,
            'ghost_fraction':g,'first_node_created_fraction':a0,'crossing_extent':sstar,
            'lower_branch_reentry_extent':sdown,'crossing_transversality':transversality,
            'max_fixed_point_Lipschitz_on_extent_interval':amax,
            'h_max_s':amax/event.coefficient,'source_event':event_json(event,kernel),'rows':rows,
            'checks':{'new_extent_states':len(rows),'four_invariants_exact_each_state':True,
                      'self_consistent_rate_equation_exact':True,'h0_identity':True,
                      'positive_stocks':True,'equality_is_thermal':True,'created_crossing_atom':True,
                      'two_roots_at_extent_one_fifth':True,'no_geometry_work':True},
            'source_sha256':{x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in source_paths}}
    out=ROOT/'results/REACTION_BRANCH_CHECKS.json';out.write_text(json.dumps(exact(result),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','crossing_extent':float(sstar),'h_cross_s':float(rows[2]['h_s']),
                      'T_initial_K':float(rows[0]['selected']['temperature']),
                      'T_before_cross_K':float(rows[2]['zero_branch']['temperature']),
                      'T_after_cross_K':float(rows[2]['selected']['temperature']),
                      'cutoff_after_eV':float(rows[2]['selected']['cutoff']/EV_J),
                      'created_count_at_cross':float(a0*sstar),'second_root_onset_extent':float(sdown),
                      'result_path':str(out)},ensure_ascii=False))

if __name__=='__main__':run()
