import numpy as np
import pytest

def test_cupy_fft_and_strang_match_numpy(tmp_path):
    cp=pytest.importorskip('cupy')
    from cr_repro.tdl import TDLRunner
    cfg={'energy_keV_per_u':100.,'b':2.,'grid':{'xlim':[-4,4],'ylim':[-4,4],'zlim':[-4,8],'dx':1.},'dt':0.12,'z_start':-3.,'z_stop':3.,'imag_steps':10,'project_nmax':1,'capture_plane':1.,'absorber_width':1.}
    cpu=TDLRunner(dict(cfg,backend='numpy')).run(tmp_path/'cpu')
    gpu=TDLRunner(dict(cfg,backend='cupy')).run(tmp_path/'gpu')
    np.testing.assert_allclose(np.load(tmp_path/'gpu/state.npy'),np.load(tmp_path/'cpu/state.npy'),atol=1e-12,rtol=1e-10)
    np.testing.assert_allclose(gpu['analysis']['P_bound_truncated_nmax'],cpu['analysis']['P_bound_truncated_nmax'],atol=1e-12,rtol=1e-10)
