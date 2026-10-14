"""Component scientific regression. NEVER interpreted as full REI admission."""
import math
import pytest
from threshold_rt import (
 TaggedGrid,OriginalGrid,Node,frozen_source,frozen_grid,
 verner,ION_NAMES,ATOMIC,C_CM_S
)
from benchmark import benchmark_one,multistep,exact_packet_control,NEUTRALS


@pytest.mark.parametrize('n',[8,16,32,64,128])
def test_source_identity_and_count(n):
 src=frozen_source(n)
 assert len(src)==3*n
 assert math.isclose(sum(p for _,p in src),1.,abs_tol=1e-13)
 assert len(frozen_grid(n))==1+3*n
 assert all(frozen_grid(n)[i]<frozen_grid(n)[i+1] for i in range(3*n))


def test_threshold_species_tags_three_way():
 g=TaggedGrid(frozen_grid(16))
 assert len(g.states)==len(g.base)+2
 for kind,chi in [('HeI',24.59),('HeII',54.42)]:
  low=g.deposit(math.nextafter(chi,-math.inf))[0]
  hi=g.deposit(chi)[0]
  assert sum(p*node.cross_section(kind) for p,node in zip(low,g.states))==0.
  assert sum(p*node.cross_section(kind) for p,node in zip(hi,g.states))>0.


def test_other_absorbers_not_silenced_at_tagged_endpoint():
 g=TaggedGrid(frozen_grid(16))
 x=next(x for x in g.states if x.threshold=='HeII' and x.side=='inactive')
 assert x.cross_section('HeII')==0
 assert x.cross_section('HeI')==verner('HeI',x.E)
 assert x.cross_section('HI')==verner('HI',x.E)


@pytest.mark.parametrize('n',[16,32,64])
def test_source_conservation_exact_moments(n):
 g=TaggedGrid(frozen_grid(n));orig=OriginalGrid(frozen_grid(n))
 for E,f in frozen_source(n):
  v,na,ua=g.deposit(E,f)
  assert na==ua==0
  N,U=g.moments(v)
  assert N==pytest.approx(f,abs=1e-15)
  assert U==pytest.approx(f*E,rel=3e-15)
 src=g.from_frozen_source(n)
 assert g.moments(src)==pytest.approx(orig.moments(orig.from_frozen_source(n)),abs=3e-14)
 assert all(x>=0 for x in src)


def test_zero_redshift_does_not_erase_inactive_side():
 g=TaggedGrid(frozen_grid(16));x=g.empty()
 i=next(i for i,node in enumerate(g.states) if node.side=='inactive' and node.threshold=='HeI')
 x[i]=1.
 out,ledger=g.redshift(x,1.0)
 assert out==x
 assert ledger['boundary_count']==0
 assert ledger['photon_redshift_work_eV']==0
 assert sum(n*node.cross_section('HeI') for n,node in zip(out,g.states))==0


def test_repeated_redshift_threshold_crossing():
 g=TaggedGrid(frozen_grid(16));state=g.deposit(24.59)[0]
 assert sum(n*node.cross_section('HeI') for n,node in zip(state,g.states))>0
 state,info=g.redshift(state,0.999)
 assert info['boundary_count']==0
 assert sum(n*node.cross_section('HeI') for n,node in zip(state,g.states))==0
 for _ in range(5):
  state,info=g.redshift(state,0.995)
  assert sum(n*node.cross_section('HeI') for n,node in zip(state,g.states))==0
  assert abs(info['energy_residual_eV'])<1e-12


def test_boundary_lost_energy_owned_once():
 g=TaggedGrid(frozen_grid(16));orig=g.deposit(13.6)[0]
 new,ledge=g.redshift(orig,.95)
 assert g.moments(new)==(0.,0.)
 assert ledge['boundary_count']==pytest.approx(1.)
 assert ledge['boundary_energy_eV']==pytest.approx(12.92)
 assert ledge['photon_redshift_work_eV']==pytest.approx(.68)
 assert abs(ledge['energy_residual_eV'])<1e-12


def test_large_redshift_does_not_create_negative_packets():
 g=TaggedGrid(frozen_grid(16)); x=g.from_frozen_source(16)
 for ratio in (.999,.99,.95,.92):
  x,led=g.redshift(x,ratio)
  assert all(v>=0 for v in x)
  assert abs(led['count_residual'])<1e-12
  assert abs(led['energy_residual_eV'])<1e-11


@pytest.mark.parametrize('dt',[0.,1e3,1e9,1e14])
def test_BE_absorption_count_and_energy_ledger(dt):
 g=TaggedGrid(frozen_grid(16));p=g.from_frozen_source(16)
 after,led=g.absorb_backward_euler(p,NEUTRALS,dt)
 assert all(v>=0 for v in after)
 assert abs(led['count_ledger_residual'])<1e-12
 assert abs(led['energy_ledger_residual_eV'])<1e-12
 assert all(x>=-1e-15 for x in led['direct_photoheat_eV_per_H'].values())
 assert led['free_electron_births_per_H']==pytest.approx(sum(led['photo_events_per_H'].values()))
 if dt==0.:assert after==p


def test_empty_neutrals_no_absorption():
 g=TaggedGrid(frozen_grid(16));p=g.from_frozen_source(16)
 after,led=g.absorb_backward_euler(p,[0,0,0],1e10)
 assert after==p
 assert all(x==0 for x in led['photo_events_per_H'].values())


def test_native_original_SOURCE_sigma_anchor():
 # Same frozen source and Verner numbers used by actual 2026-10-14 native Rust probe.
 g=OriginalGrid(frozen_grid(16));stock=g.from_frozen_source(16)
 observed=[sum(v*node.cross_section(kind) for v,node in zip(stock,g.states)) for kind in ION_NAMES]
 native=[2.93394735614069928e-18,1.18339156119082926e-18,1.37986297394576854e-21]
 for x,y in zip(observed,native):assert x==pytest.approx(y,rel=1e-12)


def test_he_positive_bias_initial_source_reduced():
 y=benchmark_one(16)
 old=y['relative_error']['baseline'];new=y['relative_error']['tagged']
 assert old['events_HeI']>.1 and old['events_HeII']>.3
 assert abs(new['events_HeI'])<.001 and abs(new['events_HeII'])<.002
 assert abs(new['heat_HeI'])<.01 and abs(new['heat_HeII'])<.01


def test_initial_source_refinement_order():
 rows=[benchmark_one(n) for n in (16,32,64)]
 for kind in ('events_HeI','events_HeII'):
  assert all(abs(row['relative_error']['tagged'][kind]) < abs(row['relative_error']['baseline'][kind]) for row in rows)
  # For initial threshold-aligned source, residual drops approximately quadratically.
  a,b,c=[abs(row['relative_error']['tagged'][kind]) for row in rows]
  assert 3.<a/b<5. and 3.<b/c<5.


def test_redshift_bias_does_not_inherit_source_only_small_error():
 y=benchmark_one(32,.98)
 assert abs(y['relative_error']['tagged']['events_HeII']) > .1
 assert abs(y['relative_error']['baseline']['events_HeII']) > .2
 assert abs(y['relative_error']['tagged']['events_HeII']) < abs(y['relative_error']['baseline']['events_HeII'])


def test_multistep_full_accounting_and_nonnegative_heat():
 result=multistep()
 for x in result.values():
  assert abs(x['number_balance'])<1e-12
  assert abs(x['energy_balance'])<1e-11
  assert len(x['steps'])==3
  for step in x['steps']:
   assert step['N_after']>=0 and step['U_after_eV']>=0
   assert abs(step['absorption_energy_residual'])<1e-11


def test_exact_centroid_control_is_not_exact_continuum_after_redshift():
 # A no-rebin kinetic centroid is another numerical *control*, not the continuum truth.
 y=benchmark_one(16,.98);z=exact_packet_control(16,.98)
 assert abs(z['events']['HeI']/y['reference']['events']['HeI']-1)>.1
 assert abs(z['events']['HeII']/y['reference']['events']['HeII']-1)>.15


@pytest.mark.parametrize('bad',[float('nan'),-1.,float('inf')])
def test_reject_invalid_source_energy(bad):
 g=TaggedGrid(frozen_grid(16))
 with pytest.raises(ValueError):g.deposit(bad,1.)


def test_reject_above_support_without_silent_clipping():
 g=TaggedGrid(frozen_grid(16))
 with pytest.raises(ValueError):g.deposit(101.,1.)
 with pytest.raises(ValueError):g.redshift(g.from_frozen_source(16),1.1)

@pytest.mark.parametrize('dt',[1e7,1e9,1e11])
def test_hydrogen_helium_stoichiometric_ledger(dt):
 g=TaggedGrid(frozen_grid(16))
 _,out=g.absorb_backward_euler(g.from_frozen_source(16),NEUTRALS,dt)
 v=out['stoichiometric_deltas_per_H']
 assert abs(v['H_I']+v['H_II'])<1e-15
 assert abs(v['He_I']+v['He_II']+v['He_III'])<1e-15
 assert v['electron']==pytest.approx(v['H_II']+v['He_II']+2*v['He_III'])
 assert all(out['photo_events_per_H'][k]>=0 for k in ION_NAMES)


def test_project_redshift_noncommutation_ionization_counterexample():
 from threshold_rt import CohortTransport
 g=TaggedGrid(frozen_grid(16))
 E,ratio=25.0,0.98
 projected=g.deposit(E)[0]
 after,_=g.redshift(projected,ratio)
 direct=g.deposit(E*ratio)[0]
 sigma_path=sum(v*node.cross_section('HeI') for v,node in zip(after,g.states))
 sigma_direct=sum(v*node.cross_section('HeI') for v,node in zip(direct,g.states))
 assert g.moments(after)==pytest.approx(g.moments(direct),abs=1e-12)
 assert sigma_path>2e-18 and sigma_direct==0
 c=CohortTransport([(E,1.)]);c.redshift(ratio)
 assert c.cohorts[0][0]==pytest.approx(24.5)
 assert verner('HeI',c.cohorts[0][0])==0


def test_unmerged_cohort_repeated_transport_ledger():
 from threshold_rt import CohortTransport
 c=CohortTransport.frozen_source(16);count_before,energy_before=c.moments()
 boundary_n=boundary_u=work=absorbed=heat=binding=0.
 for r in [.997,.992,.986]:
  red=c.redshift(r);absorb=c.absorb_backward_euler(NEUTRALS,1e9)
  boundary_n+=red['boundary_count'];boundary_u+=red['boundary_energy_eV'];work+=red['photon_work_eV']
  absorbed+=sum(absorb['photo_events_per_H'].values())
  heat+=sum(absorb['direct_photoheat_eV_per_H'].values());binding+=sum(absorb['binding_eV_per_H'].values())
  assert abs(red['number_residual'])<1e-12
  assert abs(red['energy_residual_eV'])<1e-11
  assert abs(absorb['number_residual'])<1e-12
  assert abs(absorb['energy_residual_eV'])<1e-11
 n,u=c.moments()
 assert abs(count_before-n-boundary_n-absorbed)<1e-12
 assert abs(energy_before-u-boundary_u-work-heat-binding)<1e-11


def test_source_grid_axis_identity_required():
 g=TaggedGrid(frozen_grid(16))
 with pytest.raises(ValueError,match='identity mismatch'):
  g.from_frozen_source(32)
