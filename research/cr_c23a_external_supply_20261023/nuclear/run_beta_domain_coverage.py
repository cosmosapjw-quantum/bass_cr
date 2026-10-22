"""One create-only <=60s source-coverage run; not a historical decay run."""
from pathlib import Path
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import resource
import signal
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent
RUN_ID = 'c23a_beta_fs2010_coverage_20261023_v1'
RUN = ROOT / RUN_ID
PROCESS_START = time.perf_counter()

def utc():
    return datetime.now(timezone.utc).isoformat()

def write_new(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')

def hash_file(path):
    data = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}

def budget_expired(signum, frame):
    raise TimeoutError('55 second internal numerical process budget reached')

def main():
    RUN.mkdir(exist_ok=False)
    affinity_before = sorted(os.sched_getaffinity(0))
    if 5 not in affinity_before:
        raise RuntimeError('Assigned CPU5 unavailable; do not launch science')
    os.sched_setaffinity(0, {5})
    native_vars = ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                   'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS']
    if any(os.environ.get(k) != '1' for k in native_vars):
        raise RuntimeError('Native-thread contract must be1 before imports')
    cpu_max = Path('/sys/fs/cgroup/cpu.max')
    memory_max = Path('/sys/fs/cgroup/memory.max')
    start = {'run_id': RUN_ID, 'started_utc': utc(), 'status': 'ACTIVE',
             'pid': os.getpid(), 'cpu_id': 5, 'affinity_before': affinity_before,
             'affinity_active': sorted(os.sched_getaffinity(0)),
             'cpu_max': cpu_max.read_text().strip() if cpu_max.exists() else None,
             'memory_max': memory_max.read_text().strip() if memory_max.exists() else None,
             'native_env': {k: os.environ[k] for k in native_vars},
             'lease_authority': 'parent /root explicit cooperative CPU5 assignment; no NCP or remote worker',
             'coordinator_CPU55': 'UNAVAILABLE_IN_SANDBOX; CPU5 explicitly assigned for this bounded task',
             'wall_budget_s': 60, 'internal_alarm_s': 55, 'historical_ODE_calls': 0,
             'output_policy': 'CREATE_ONLY'}
    write_new(RUN / 'LEASE_START.json', start)
    signal.signal(signal.SIGALRM, budget_expired)
    signal.alarm(55)
    status = 'FAILED'
    try:
        from beta_domain_coverage import (ElectronDomain, moment_bounds, diagnostic_segments,
             scipy_dimensionless_moment, mp_dimensionless_moment, analytic_dimensionless_moment)
        import scipy
        import mpmath as mp
        from threadpoolctl import threadpool_info
        mp.mp.dps = 80
        pools = threadpool_info()
        assert all(p['num_threads'] == 1 for p in pools)
        inputs = json.loads((ROOT / 'source/EVALUATED_ENERGY_AND_DOMAIN_CONTRACT.json').read_text())
        pin_paths = [ROOT / 'source/EVALUATED_ENERGY_AND_DOMAIN_CONTRACT.json',
                     ROOT / 'beta_domain_coverage.py', ROOT / 'run_beta_domain_coverage.py',
                     ROOT / 'THEORY_AND_CONTRACT.md', ROOT / 'prepare_source_contract.py']
        pin_paths += [ROOT / 'source' / x['file'] for x in inputs['energy_inputs'].values()]
        for src in inputs['energy_inputs'].values():
            assert hash_file(ROOT / 'source' / src['file'])['sha256'] == src['sha256']
        write_new(RUN / 'INPUT_CODE_PINS.json', [hash_file(p) for p in pin_paths])
        d = inputs['domain']
        domain = ElectronDomain(float(d['lower_eV']), float(d['upper_eV']))
        M = float(inputs['electron_mass_energy']['central_eV'])
        domain.require_source(carrier='electron', energy_kind='kinetic', units='eV')
        rejections = []
        for carrier, kind, units in [('neutron', 'kinetic', 'eV'), ('proton', 'kinetic', 'eV'),
                                     ('photon', 'kinetic', 'eV'), ('antineutrino', 'kinetic', 'eV'),
                                     ('electron', 'total', 'eV'), ('electron', 'kinetic', 'keV')]:
            try:
                domain.require_source(carrier=carrier, energy_kind=kind, units=units)
            except ValueError as exc:
                rejections.append({'carrier': carrier, 'kind': kind, 'units': units,
                                   'result': 'REJECTED', 'message': str(exc)})
            else:
                raise AssertionError('Unsupported source was admitted')
        for value in (None, float('nan'), -1.0):
            try:
                domain.classify(value, carrier='electron', energy_kind='kinetic', units='eV')
            except ValueError:
                pass
            else:
                raise AssertionError('Missing/nonphysical electron energy was accepted')
        boundary_cases = [(0.0, 'LOW_TAIL_UNRESOLVED'), (domain.lower_eV, 'IN_ENERGY_DOMAIN_ONLY'),
                          (domain.upper_eV, 'IN_ENERGY_DOMAIN_ONLY'),
                          (domain.upper_eV + 1, 'HIGH_TAIL_UNRESOLVED')]
        for energy, expected in boundary_cases:
            assert domain.classify(energy, carrier='electron', energy_kind='kinetic', units='eV') == expected
        results = {}
        comparisons = []
        csv_rows = []
        for isotope, source in inputs['energy_inputs'].items():
            Q = float(source['decay_Q_eV'])
            evaluated_mean = float(source['electron_mean_kinetic_eV'])
            bounds = moment_bounds(source['electron_mean_kinetic_eV'], source['decay_Q_eV'],
                                   d['lower_eV'], d['upper_eV'])
            diagnostic = diagnostic_segments(Q, M, domain)
            for k in range(3):
                segments = [(row['interval'], row['lower_eV'], row['upper_eV'], row['dimensionless_moments'][k])
                            for row in diagnostic['segments']]
                segments.append(('total', 0.0, Q, diagnostic['total_dimensionless_moments'][k]))
                for label, lo, hi, scipy_value in segments:
                    quad80 = mp_dimensionless_moment(k, lo, hi, Q, M)
                    analytic = analytic_dimensionless_moment(k, lo, hi, Q, M)
                    assert quad80 > 0 and analytic > 0 and scipy_value > 0
                    err_sci = abs(mp.mpf(scipy_value) - quad80) / quad80
                    err_ana = abs(analytic - quad80) / quad80
                    assert err_sci < inputs['acceptance']['independent_moment_relative_tolerance']
                    assert err_ana < inputs['acceptance']['independent_moment_relative_tolerance']
                    comparisons.append({'isotope': isotope, 'moment_k': k, 'interval': label,
                        'scipy': scipy_value, 'mpmath_80digits': mp.nstr(quad80, 82),
                        'analytic_80digits': mp.nstr(analytic, 82),
                        'scipy_vs_mp_relative': float(err_sci), 'analytic_vs_mp_relative': float(err_ana)})
                sum_segments = sum(r['dimensionless_moments'][k] for r in diagnostic['segments'])
                assert abs(sum_segments / diagnostic['total_dimensionless_moments'][k] - 1) < 2e-12
                # The same dimensionless integral after explicit eV -> keV conversion.
                kev_val, _ = scipy_dimensionless_moment(k, domain.lower_eV/1000,
                     domain.upper_eV/1000, Q/1000, M/1000)
                ev_val = diagnostic['segments'][1]['dimensionless_moments'][k]
                assert abs(kev_val/ev_val - 1) < 2e-12
            sum_p = sum(r['particle_fraction'] for r in diagnostic['segments'])
            sum_e = sum(r['kinetic_energy_fraction'] for r in diagnostic['segments'])
            assert abs(sum_p-1) < 2e-12 and abs(sum_e-1) < 2e-12
            diagnostic['mean_minus_selected_evaluated_mean_eV'] = diagnostic['mean_kinetic_eV'] - evaluated_mean
            diagnostic['mean_ratio_to_selected_evaluated_mean'] = diagnostic['mean_kinetic_eV'] / evaluated_mean
            diagnostic['mean_comparison_status'] = 'DIFFERENT_MODEL_NOT_A_FIT_OR_EVALUATION_VALIDATION'
            for row in diagnostic['segments']:
                csv_rows.append({'source': isotope, 'model': 'ILLUSTRATIVE_FERMI_ONE',
                    **{key: row[key] for key in ['interval', 'lower_eV', 'upper_eV', 'particle_fraction',
                      'kinetic_energy_per_primary_eV', 'kinetic_energy_fraction', 'deposition_status']}})
            results[isotope] = {'evaluated_input': {'Q_support_ceiling_eV': Q,
                                 'mean_electron_kinetic_eV': evaluated_mean,
                                 'continuous_spectrum_supplied': False},
                               'conditional_moment_bounds': bounds,
                               'illustrative_diagnostic': diagnostic}
        validation = {'status': 'PASS_SCOPED', 'quad_moment_interval_comparisons': len(comparisons),
            'max_scipy_vs_mp_relative': max(x['scipy_vs_mp_relative'] for x in comparisons),
            'max_analytic_vs_mp_relative': max(x['analytic_vs_mp_relative'] for x in comparisons),
            'partition_number_energy_second_moment': 'PASS', 'eV_keV_scaling': 'PASS',
            'exact_counterexample_moments': 'PASS', 'electron_only_and_units_guards': 'PASS',
            'source_rejection_cases': rejections, 'missing_and_nonphysical_energy_rejection': 'PASS',
            'boundary_classification': 'PASS', 'scope': 'numerical/domain contract, not evaluated spectrum fidelity',
            'independent_methods_same_agent': True, 'global_error_bound': None,
            'scipy_version': scipy.__version__, 'mpmath_version': mp.__version__,
            'threadpool_info': pools}
        result = {'schema': 'C23A_BETA_DOMAIN_RESULTS_V1', 'run_id': RUN_ID, 'status': 'PASS_SCOPED',
            'completed_utc': utc(), 'source_domain_eV': [domain.lower_eV, domain.upper_eV],
            'source_energy_kind': 'primary electron kinetic',
            'direct_full_beta_to_FS_admission': 'NOT_ADMITTED',
            'results': results, 'validation': validation,
            'new_ODE_calls': 0, 'historical_ODE_calls': 0, 'NCP_jobs': 0,
            'global_error_bound': None,
            'EXECUTION': 'BOUNDED_NEW_COVERAGE_CALCULATION_COMPLETE_SCOPED',
            'PUBLICATION': 'PARENT_PENDING', 'BACKUP': 'PARENT_PENDING',
            'DAG': 'source pins -> moment bounds -> F1 diagnostic -> independent checks COMPLETE_SCOPED; evaluated corrected spectrum and transport tails OPEN; full high-energy network HOLD'}
        write_new(RUN / 'RESULT.json', result)
        write_new(RUN / 'INDEPENDENT_MOMENT_CHECKS.json', comparisons)
        with (RUN / 'ILLUSTRATIVE_COVERAGE.csv').open('x', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
            writer.writeheader()
            writer.writerows(csv_rows)
        status = 'PASS_SCOPED'
        print(json.dumps({'status': status, 'run_id': RUN_ID,
            'runtime_s_before_finalization': time.perf_counter()-PROCESS_START,
            'validation': {k: validation[k] for k in ['quad_moment_interval_comparisons',
                'max_scipy_vs_mp_relative', 'max_analytic_vs_mp_relative']},
            'results': {name: {'moment_bounds': item['conditional_moment_bounds'],
                'diagnostic_mean_eV': item['illustrative_diagnostic']['mean_kinetic_eV'],
                'segments': item['illustrative_diagnostic']['segments']}
                for name, item in results.items()}}, ensure_ascii=False))
    except Exception as exc:
        write_new(RUN / 'FAILURE.json', {'status': 'FAILED', 'exception': type(exc).__name__,
            'message': str(exc), 'traceback': traceback.format_exc(), 'at_utc': utc()})
        raise
    finally:
        signal.alarm(0)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        write_new(RUN / 'LEASE_COMPLETE.json', {'run_id': RUN_ID, 'status': status,
            'lease_status': 'RELEASED', 'completed_utc': utc(),
            'wall_s': time.perf_counter()-PROCESS_START, 'user_cpu_s': usage.ru_utime,
            'system_cpu_s': usage.ru_stime, 'peak_rss_kib': usage.ru_maxrss,
            'cpu_id': 5, 'affinity_final': sorted(os.sched_getaffinity(0)),
            'native_threads_per_worker': 1, 'new_ODE_calls': 0, 'historical_ODE_calls': 0})

if __name__ == '__main__':
    main()
