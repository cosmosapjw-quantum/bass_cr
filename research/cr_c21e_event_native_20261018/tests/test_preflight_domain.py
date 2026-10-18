import pytest


def test_prepared_probe_inputs_fit_original_reference_grid(tmp_path,monkeypatch):
    """Protocol input coverage; this is NOT native absorption accuracy evidence."""
    import run_experiment as runner
    class Captured(Exception):pass
    def capture(command,**kwargs):
        lines=kwargs['input'].splitlines()
        energies=[float(line.split()[8]) for line in lines if line.startswith('ABSORB')]
        assert len(energies)==7
        assert all(13.6<=e<=512. for e in energies), 'unrepresentable q at a_ref'
        raise Captured()
    monkeypatch.setattr(runner.subprocess,'run',capture)
    with pytest.raises(Captured):
        runner.native_point_parity(tmp_path/'uncompiled',runner.make_fixture(),tmp_path)
