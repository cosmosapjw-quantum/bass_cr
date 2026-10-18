from dataclasses import replace
import json,math,sys
from pathlib import Path
import numpy as np
import pytest
from event_coupler import *
from run_experiment import make_fixture,run_history,run_reference,Fixture,breakpoints,write_json
from native_micro import NativeMicro,OWNER

Y=Y_HE

def gas():return gas_from_temperature([.2,.15,.01],8500,Y)

def point_args(g=None,Yvalue=Y):
    if g is None:g=gas()
    return (g,np.array([1e-4]),np.array([80.]),np.zeros((1,3)),1e11,1./12.,N_H0,Yvalue)

class LinearRecombination:
    kind='MANUFACTURED_LINEAR_RECOMBINATION'
    def __init__(self,r):self.r=r
    def __call__(self,a,g,nh0,Y):
        rr=np.array([self.r*g[0],0.,0.]);f=-rr
        return MicroRates(f,0.,float(binding_weights(Y)@f),float(rr@BIND_EV),0.,np.zeros(3),rr)


def test_recombination_requirement_now_evolves_without_photons():
    args=list(point_args());args[1]=np.zeros(1)
    r=LinearRecombination(1e-13)
    result=reaction_step(*args,r)
    z=args[4]*r.r
    assert result.gas[0] < args[0][0]
    assert result.gas[0]==pytest.approx(args[0][0]*(1-z/2)/(1+z/2),rel=3e-12)
    assert abs(result.energy_defect)<3e-14


@pytest.mark.parametrize('mode',list(MODES))
def test_zero_micro_zero_opacity_identity(mode):
    r=reaction_step(*point_args(),ZeroMicro(),MODES[mode])
    np.testing.assert_array_equal(r.gas,gas())
    np.testing.assert_array_equal(r.photons,np.array([1e-4]))
    assert not r.events.any()


def test_micro_stiff_midpoint_rejects_without_clipping_or_mutation():
    args=list(point_args());args[4]=3e13
    before=args[0].copy();phot=args[1].copy()
    with pytest.raises(StepRejected):reaction_step(*args,LinearRecombination(1e-13))
    np.testing.assert_array_equal(args[0],before);np.testing.assert_array_equal(args[1],phot)


def test_stiff_be_control_has_positive_solution():
    args=list(point_args());args[4]=3e13
    r=reaction_step(*args,LinearRecombination(1e-13),MODES['BE'])
    assert r.gas[0]==pytest.approx(.2/4,rel=3e-12)


def test_endpoint_depleted_start_needs_no_gamma_division():
    g=gas_from_temperature([1.,.15,.01],8500,Y)
    args=list(point_args(g));args[3]=np.ones((1,3))*1e-12
    result=reaction_step(*args,ManufacturedMicro())
    assert state_valid(result.gas,Y)
    assert result.events[0,0]>0
    assert np.isfinite(result.gas).all()


def test_replenished_heii_and_integrated_charge_ledger():
    g=gas_from_temperature([.2,0.,0.],8500,Y)
    n=np.array([.001]);E=np.array([80.]);k=np.ones((1,3))*1e-12
    r=reaction_step(g,n,E,k,1e11,1/12,N_H0,Y,ZeroMicro())
    assert r.events[0,1]>0 and r.events[0,2]>0
    delta=r.gas[:3]-g[:3];S=event_fractions(r.events.sum(axis=0),Y)
    np.testing.assert_allclose(delta,S,rtol=1e-10,atol=2e-13)
    assert delta[0]+Y*(delta[1]+2*delta[2])==pytest.approx(r.events.sum(),abs=3e-13)


def test_helium_absent_has_structural_zero_not_epsilon():
    g=gas_from_temperature([.2,0.,0.],8500,0.)
    r=reaction_step(g,np.array([1e-3]),np.array([80.]),np.ones((1,3))*1e-12,1e11,1/12,N_H0,0.,ManufacturedMicro())
    assert (r.gas[1:3]==0).all() and not r.events[:,1:].any()


def test_energy_residual_matches_weighted_newton_residual():
    args=list(point_args());args[1]=np.array([.001]);args[3]=np.ones((1,3))*1e-12
    r=reaction_step(*args,ManufacturedMicro())
    expected=r.residual[3]+binding_weights(Y)@r.residual[:3]
    assert abs(r.energy_defect-expected)<2e-16
    assert abs(r.energy_defect)<1e-13
    assert abs(r.number_defect)<1e-18


def test_below_helium_threshold_channels_are_exact_zero():
    args=list(point_args());args[2]=np.array([20.]);args[3]=np.array([[1e-12,0.,0.]])
    r=reaction_step(*args,ManufacturedMicro())
    assert not r.events[:,1:].any()


@pytest.mark.parametrize('bad',[-1.,float('nan'),float('inf'),0.])
def test_invalid_time_rejected(bad):
    args=list(point_args());args[4]=bad
    with pytest.raises(DomainError):reaction_step(*args,ZeroMicro())


def test_bad_threshold_rejected():
    args=list(point_args());args[2]=np.array([13.59]);args[3]=np.array([[1.,0.,0.]])
    with pytest.raises(DomainError,match='FIT'):reaction_step(*args,ZeroMicro())


def test_nonphoto_wrong_energy_owner_fails_before_acceptance():
    class Bad(ZeroMicro):
        def __call__(self,*args):return MicroRates(np.zeros(3),1e-9,0.,0.,0.)
    with pytest.raises(ProviderFailure,match='ENERGY_OWNER'):reaction_step(*point_args(),Bad())


def test_wrong_species_owner_rejected():
    class Bad(ZeroMicro):
        def __call__(self,*args):return MicroRates(np.array([1e-9,0,0]),0.,0.,0.,0.)
    with pytest.raises(ProviderFailure,match='STOICHIOMETRY'):reaction_step(*point_args(),Bad())


def test_failed_provider_preserves_all_inputs():
    class Broken:
        kind='PROTOCOL_FAILURE'
        def __call__(self,*args):raise ProviderFailure('injected')
    args=point_args();before=[v.copy() for v in args[:4]]
    with pytest.raises(ProviderFailure):reaction_step(*args,Broken())
    for i in range(4):np.testing.assert_array_equal(args[i],before[i])


def test_same_mixed_micro_point_identity_at_multiple_epochs():
    for a in (.06,.09,.15):
        r=ManufacturedMicro()(a,gas(),N_H0,Y);r.validate(Y)
        assert r.rr_h_s.sum()>0 and r.ci_h_s.sum()>0 and r.dr_h_s>0


@pytest.mark.parametrize('mode',list(MODES))
def test_short_history_ledgers(mode):
    r=run_history(make_fixture(dx=.0002),2,ManufacturedMicro(),mode)
    assert r['status']=='PASS_SCOPED_FIXED_GRID_TRANSACTION'
    assert max(abs(x) for x in r['species_defect'])<3e-12
    assert abs(r['number_defect_H'])<3e-17
    assert abs(r['energy_defect_eV_H'])<3e-12
    assert min(r['photons'])>=0
    assert min(r['ledgers']['rr'])>0


def test_radau_independent_same_source_ledger():
    f=make_fixture(dx=.0002);r=run_reference(f,ManufacturedMicro())
    assert abs(r['energy_defect_eV_H'])<1e-11
    assert max(abs(x) for x in r['species_defect'])<1e-11
    assert abs(r['number_defect_H'])<1e-15


def test_source_off_inventory_exact():
    f=make_fixture(dx=.0002,source_on=False)
    assert len(f.q)==3
    r=run_history(f,2,ManufacturedMicro())
    assert r['ledgers']['source_n']==0 and r['ledgers']['source_u']==0


def test_future_born_packet_not_advanced_before_birth():
    f=make_fixture(dx=.002)
    assert len(breakpoints(f))>=4
    r=run_history(f,2,ZeroMicro())
    born=sum(n for n,b in zip(f.amounts,f.birth) if b>f.x0)
    assert r['ledgers']['source_n']==pytest.approx(born,rel=2e-15)
    expected=sum(n*q/math.exp(b) for n,q,b in zip(f.amounts,f.q,f.birth) if b>f.x0)
    assert r['ledgers']['source_u']==pytest.approx(expected,rel=2e-15)


def test_shared_fixture_unchanged_by_run():
    f=make_fixture(dx=.0002);before=f.digest
    run_history(f,1,ZeroMicro())
    assert before==f.digest


def test_immutable_output_refuses_overwrite(tmp_path):
    path=tmp_path/'a.json';write_json(path,{'pass':1})
    with pytest.raises(FileExistsError):write_json(path,{'pass':2})
    assert json.loads(path.read_text())=={'pass':1}


@pytest.mark.parametrize('change',[{'dx':0.},{'opacity_scale':-1.},{'birth':(1.,)},{'amounts':(-1.,)*9}])
def test_invalid_fixture(change):
    with pytest.raises(DomainError):replace(make_fixture(),**change).validate()


# This executable is only a protocol boundary fixture, never used for science.
SERVER=r'''
import sys,time
owner='6ea2b1b4b3875c9163cafc45efe720afded43fc4'
mode=sys.argv[1]
print('C21E_NONPHOTO_V1\t'+('wrong' if mode=='owner' else owner),flush=True)
for line in sys.stdin:
 if line.strip()=='QUIT':break
 if mode=='timeout':time.sleep(1)
 v=list(map(float,line.split()[1:]));a,nh0,nhe0,x,y,z,w=v
 Y=nhe0/nh0;T=w/(1.5*(1.380649e-16/1.602176634e-12)*(1+Y+x+Y*(y+2*z)))
 out=[a,nh0/a**3,nhe0/a**3,T]+[0.]*19
 if mode=='photo':out[18]=1e-9
 if mode=='density':out[1]*=.9998
 print('OK\t'+'\t'.join(format(v,'.17e') for v in out),flush=True)
'''


def test_persistent_protocol_roundtrip_and_shutdown(tmp_path):
    with NativeMicro([sys.executable,'-u','-c',SERVER,'ok'],tmp_path) as p:
        for a in (.06,.09):
            r=p(a,gas(),N_H0,Y);assert r.thermal_ev_h_s==0
        process=p.process
    assert process.poll()==0 and p.calls==2
    assert len((tmp_path/'native_points.jsonl').read_text().splitlines())==2


@pytest.mark.parametrize('mode,error',[('photo','DOUBLE_PHOTO'),('density','DENSITY')])
def test_native_protocol_owners_strict(tmp_path,mode,error):
    with NativeMicro([sys.executable,'-u','-c',SERVER,mode],tmp_path) as p:
        with pytest.raises(ProviderFailure,match=error):p(.09,gas(),N_H0,Y)


def test_wrong_source_handshake_rejected(tmp_path):
    with pytest.raises(ProviderFailure,match='HANDSHAKE'):NativeMicro([sys.executable,'-u','-c',SERVER,'owner'],tmp_path)


def test_native_timeout_child_is_reaped(tmp_path):
    with NativeMicro([sys.executable,'-u','-c',SERVER,'timeout'],tmp_path,timeout=2.) as p:
        p.timeout=.15  # isolate response timeout after successful process startup
        with pytest.raises(ProviderFailure,match='TIMEOUT'):p(.09,gas(),N_H0,Y)
        assert p.process.poll() is not None


def test_native_call_budget(tmp_path):
    with NativeMicro([sys.executable,'-u','-c',SERVER,'ok'],tmp_path,max_calls=1) as p:
        p(.09,gas(),N_H0,Y)
        with pytest.raises(ProviderFailure,match='BUDGET'):p(.09,gas(),N_H0,Y)

@pytest.mark.parametrize('newmode,oldmode',[('BE','BE'),('FULLMID','MIDEXP')])
def test_photo_only_reduces_to_pinned_pr79_at_same_gas(newmode,oldmode):
    import c21d_trilane as old
    g0=gas();atoms=np.array([1-g0[0],g0[0],Y*(1-g0[1]-g0[2]),Y*g0[1],Y*g0[2]])
    E=np.array([20.,30.,80.]);n=np.array([.001,.002,.0003]);k=np.array([[1e-12,0,0],[.4e-12,.6e-12,0],[.1e-12,.5e-12,.8e-12]])
    nold,atomold,ev,_,_=old.evaluate_frozen_endpoint(n,atoms,k,1e10,oldmode)
    r=reaction_step(g0,n,E,k,1e10,1/12,N_H0,Y,ZeroMicro(),MODES[newmode])
    np.testing.assert_allclose(r.photons,nold,rtol=3e-10,atol=3e-13)
    expect=np.array([atomold[1],atomold[3]/Y,atomold[4]/Y])
    np.testing.assert_allclose(r.gas[:3],expect,rtol=3e-10,atol=3e-13)


def test_pinned_source_helpers_byte_identity():
    import hashlib
    root=Path(__file__).resolve().parents[1]
    meta=json.loads((root/'vendor/PROVENANCE.json').read_text())
    for name,sha in meta['files'].items():
        assert hashlib.sha256((root/'vendor/pr79'/name).read_bytes()).hexdigest()==sha


def test_actual_cli_manufactured_pipeline(tmp_path):
    import subprocess
    script=Path(__file__).resolve().parents[1]/'src/run_experiment.py'
    out=tmp_path/'fresh'
    proc=subprocess.run([sys.executable,str(script),'--out',str(out),'--micro','manufactured','--steps','2','--modes','FULLMID','--dx','.0002'],capture_output=True,text=True,timeout=30)
    assert proc.returncode==0,proc.stderr
    doc=json.loads((out/'SUMMARY.json').read_text())
    assert doc['native_science'] is False and len(doc['cases'])==1
    assert doc['cases'][0]['normalized_state_error']>0
    assert (out/'FULLMID_0002/accepted_steps.jsonl').is_file()


def test_native_cli_fails_closed_without_binary(tmp_path):
    import subprocess
    script=Path(__file__).resolve().parents[1]/'src/run_experiment.py'
    out=tmp_path/'no_native'
    proc=subprocess.run([sys.executable,str(script),'--out',str(out),'--micro','native','--native',str(tmp_path/'missing')],capture_output=True,text=True,timeout=15)
    assert proc.returncode==2 and not out.exists()
