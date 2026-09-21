"""No expensive physics jobs are launched by these contract tests."""
import importlib
import importlib.util
from pathlib import Path
import numpy as np
from cr_repro.grid import GridSpec


def api():
    assert importlib.util.find_spec('cr_repro.r3m11_jobs'), 'run matrix not implemented'
    return importlib.import_module('cr_repro.r3m11_jobs')


def test_all_jobs_are_one_energy_one_impact_parameter():
    jobs=api().build_matrix()
    assert len(jobs)>=10
    for j in jobs.values():
        assert j['config']['energy_keV_per_u']==100.
        assert j['config']['b']==2.


def test_dt_control_keeps_cap_and_all_other_inputs():
    jobs=api().build_matrix();base=jobs['tdl_cap_base']['config'];fine=jobs['tdl_dt025']['config']
    assert {k:v for k,v in base.items() if k!='dt'}=={k:v for k,v in fine.items() if k!='dt'}
    assert base['absorber_reference_dt']==fine['absorber_reference_dt']==.05


def test_initial_preparation_preserves_total_imaginary_time():
    jobs=api().build_matrix();a=jobs['tdl_cap_base']['config'];b=jobs['tdl_imag025']['config']
    assert a['imag_dt']*a['imag_steps']==b['imag_dt']*b['imag_steps']
    assert b['imag_steps']==2*a['imag_steps']


def test_radial_and_exponent_changes_are_separate():
    jobs=api().build_matrix();base=jobs['aocc_base']['config'];rad=jobs['aocc_radial_only']['config'];exp=jobs['aocc_exponent_only']['config']
    assert {k:v for k,v in rad.items() if k not in ('ns','np')}=={k:v for k,v in base.items() if k not in ('ns','np')}
    assert {k:v for k,v in exp.items() if k!='alpha_max'}=={k:v for k,v in base.items() if k!='alpha_max'}


def test_grid_refinements_keep_nuclei_off_nodes():
    for j in api().build_matrix().values():
        c=j['config']
        if j['lane']!='tdl':continue
        spec=GridSpec.from_dict(c['grid']);x,y,z=spec.axes(np)
        assert min(abs(y))>.49*spec.dx
        assert c['z_stop']<max(z)-c['absorber_width']


def test_matrix_generation_create_only(tmp_path):
    m=api();m.write_matrix(tmp_path/'matrix')
    assert (tmp_path/'matrix/MATRIX.json').exists()
    import pytest
    with pytest.raises(FileExistsError):m.write_matrix(tmp_path/'matrix')
