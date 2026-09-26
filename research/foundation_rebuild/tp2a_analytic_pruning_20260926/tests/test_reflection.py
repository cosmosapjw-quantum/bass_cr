import os
from pathlib import Path
import numpy as np
import pytest
import bootstrap
from runtime import load_bank
from bass_foundations.two_center import Trajectory,symmetric_channels
from reflection import sector_transform,prune_even
from exact_cross import cross,MomentKernel,cartesian_transform,KEYS

W=Path(__file__).resolve().parents[1]

def test_stored_full_operator_decouples_four_odd_channels():
    bank,_=load_bank(W/'inputs/z0');channels=symmetric_channels(bank)
    trajectory=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,2.00798106651023)))
    with np.load(W/'inputs/z0/hp/h2q64_z+0.00000000.npz') as f:
        full={k:f[k] for k in ('S','H','D')}
    c0=np.zeros(18,complex);c0[0]=1
    reduced=prune_even(full,c0,channels,trajectory)
    assert reduced['metadata']['even_dimension']==14
    assert reduced['metadata']['odd_dimension']==4
    U=reduced['embedding']
    rng=np.random.default_rng(53);a=rng.normal(size=14)+1j*rng.normal(size=14)
    for k in ('S','H','D'):
        np.testing.assert_allclose(full[k]@(U@a),U@(reduced['matrices'][k]@a),rtol=1e-12,atol=1e-12)

def test_odd_initial_state_is_not_discarded():
    bank,_=load_bank(W/'inputs/z0');channels=symmetric_channels(bank)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,2.)))
    U,ne,_=sector_transform(channels,tr)
    full={'S':np.eye(18),'H':np.eye(18),'D':np.zeros((18,18))}
    with pytest.raises(ValueError,match='odd-sector'):prune_even(full,U[:,ne],channels,tr)

def test_nonplanar_motion_rejects_pruning():
    bank,_=load_bank(W/'inputs/z0');channels=symmetric_channels(bank)
    with pytest.raises(ValueError,match='plane'):
        sector_transform(channels,Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,.01,2.))))

def test_direct_even_contraction_equals_full_operator_projection():
    from bass_foundations.radial_basis import RadialSpec,atomic_bank
    bank=atomic_bank(RadialSpec(radius=10,elements=6,lmax=1,bound_nmax=2,positive_per_l=1));ch=symmetric_channels(bank)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,2.)))
    kernel=MomentKernel(os.environ.get('BASS_MOMENT_BUILD',W/'native_build_final'))
    full=cross(tr,ch,-.8,kernel,order=8);even=cross(tr,ch,-.8,kernel,order=8,sector='even')
    n=len(ch)//2;ut=cartesian_transform(ch[:n]);up=cartesian_transform(ch[n:]);it=even['metadata']['sector_columns_T'];ip=even['metadata']['sector_columns_P']
    Ut=ut[:,it];Up=up[:,ip]
    for k in KEYS:
        expected=Ut.conj().T@full[k]@Up if k.endswith('tp') else Up.conj().T@full[k]@Ut
        np.testing.assert_allclose(even[k],expected,rtol=2e-12,atol=1e-13,err_msg=k)

def test_direct_even_full_assembly_matches_full_projection():
    from bass_foundations.radial_basis import RadialSpec,atomic_bank
    from assemble import assemble
    bank=atomic_bank(RadialSpec(radius=10,elements=6,lmax=1,bound_nmax=2,positive_per_l=1));ch=symmetric_channels(bank)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,2.)))
    engine=MomentKernel(os.environ.get('BASS_MOMENT_BUILD',W/'native_build_final'))
    _,full=assemble(tr,ch,-.8,engine,order=8,subdivisions=1)
    _,even=assemble(tr,ch,-.8,engine,order=8,subdivisions=1,sector='even')
    U,ne,_=sector_transform(ch,tr);U=U[:,:ne]
    for k in ('S','H','D'):
        np.testing.assert_allclose(even[k],U.conj().T@full[k]@U,rtol=4e-12,atol=2e-13)

def test_small_but_physical_odd_initial_amplitude_is_not_threshold_pruned():
    bank,_=load_bank(W/'inputs/z0');channels=symmetric_channels(bank)
    tr=Trajectory(((0,0,0),(2,0,0)),((0,0,0),(0,0,2.)))
    U,ne,_=sector_transform(channels,tr)
    full={'S':np.eye(18),'H':np.eye(18),'D':np.zeros((18,18))}
    c0=np.zeros(18,complex);c0[0]=1.;c0+=1e-14*U[:,ne]
    with pytest.raises(ValueError,match='odd-sector'):prune_even(full,c0,channels,tr)
