"""Read already downloaded bytes; do not fetch, integrate, or run historical models."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'

def save_new(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write('\n')

def endf_number(text):
    token = text.strip()
    if not token:
        raise ValueError('Missing ENDF field is not zero')
    if 'e' not in token.lower():
        token = re.sub(r'(?<=[0-9.])([+-][0-9]+)$', r'e\1', token)
    return Decimal(token)

def read_decay(name, sha):
    p = SOURCE / name
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == sha
    numbered = [(n, line) for n, line in enumerate(raw.decode('ascii').splitlines(), 1)
                if len(line) >= 75 and line[70:72].strip() == '8'
                and line[72:75].strip() == '457']
    assert len(numbered) == 9, 'Parser scoped to these two one-branch records'
    rows = [[endf_number(line[i:i+11]) for i in range(0, 66, 11)] for _, line in numbered]
    assert rows[0][4:] == [0, 1]  # unstable, one spectrum
    assert rows[3][4:] == [6, 1]  # one decay branch
    assert rows[4][0] == 1 and rows[4][4] == 1  # beta-minus, BR1
    assert rows[5][1:4] == [1, 0, 0]  # STYP1, no continuum, no covariance
    assert rows[5][5] == 1 and rows[6][0] == 1
    assert rows[8][0:3] == [1, 1, 1]  # beta-minus, allowed, intensity1
    assert rows[2][0] == rows[6][2]  # electron-related total agrees beta mean
    assert rows[4][2] == rows[7][0]  # tabulated ER equals decay Q
    return {
        'file': name, 'bytes': len(raw), 'sha256': sha,
        'sub_library': 'ENDF/B-VIII.0 decay; EVAL-NOV05; ENSDF conversion 20111222; DIST-FEB18',
        'MF': 8, 'MT': 457, 'STYP': 1, 'TYPE': 1,
        'LCON': 0, 'continuous_beta_spectrum_supplied': False,
        'branch_probability': str(rows[4][4]), 'beta_intensity_per_decay': str(rows[8][2] * rows[6][0]),
        'decay_Q_eV': str(rows[4][2]), 'decay_Q_recorded_uncertainty_eV': str(rows[4][3]),
        'beta_ER_eV': str(rows[7][0]), 'beta_ER_recorded_uncertainty_eV': str(rows[7][1]),
        'electron_mean_kinetic_eV': str(rows[6][2]),
        'electron_mean_recorded_uncertainty_eV': str(rows[6][3]),
        'mean_uncertainty_interpretation': ('NONZERO_RECORDED_EVALUATION_UNCERTAINTY_NOT_PROPAGATED'
                                           if rows[6][3] > 0 else 'ZERO_RECORDED_DOES_NOT_ESTABLISH_ZERO_PHYSICAL_UNCERTAINTY'),
        'lifetime_admission': 'NOT_ADOPTED; original EVALUATED_DECAY_INPUTS.json remains authoritative for lifetimes',
        'energy_admission': 'CENTRAL_VALUE_CONDITIONAL_SUPPORT_AND_MOMENT_DIAGNOSTIC_ONLY',
        'endpoint_semantics': 'ER equals Q in this record; Q is used as a support ceiling and F=1 diagnostic endpoint parameter, not a precision recoil/final-state corrected endpoint',
        'records': [{'line_number': n, 'text': line} for n, line in numbered],
    }

def main():
    prior = SOURCE / 'EVALUATED_DECAY_INPUTS.json'
    prior_raw = prior.read_bytes()
    prior_data = json.loads(prior_raw)
    assert hashlib.sha256(prior_raw).hexdigest() == '683315ca3464057ea0bc75cbb00c409a4327090a48faa13bc00717ba253b7f26'
    assert not any(('energy' in k or 'endpoint' in k) for k in prior_data)
    neutron = read_decay('neutron_ENDF8_decay__decay_0001_0-Nn-1.dat', '5138d147c871939080908634685b4eddc1241528fb3d48240053edca62f5a59e')
    tritium = read_decay('tritium_ENDF8_decay__decay_0004_1-H-3.dat', 'b7f6697ea51ef8a03bc6b89b409c9da45b3985810e19b896e9448005eb8e7a0b')
    fs = ROOT.parent / 'cr_deposition' / 'upstream' / 'x_int_tables' / 'log_xi_-1.0.dat'
    fs_raw = fs.read_bytes()
    fs_sha = hashlib.sha256(fs_raw).hexdigest()
    assert fs_sha == '771458627c9f9a99773c3454d9ad370996e1b86030f71e82c011403a6572a974'
    energies = []
    numeric_lines = []
    for line in fs_raw.decode('ascii').splitlines():
        cells = line.split()
        if len(cells) == 9:
            try:
                val = Decimal(cells[0])
                [Decimal(x) for x in cells]
            except Exception:
                continue
            energies.append(val)
            numeric_lines.append(line)
    assert len(energies) == 258 and all(a < b for a, b in zip(energies, energies[1:]))
    assert energies[0] == 10 and energies[-1] == Decimal('9937.21')
    contract = {
        'schema': 'C23A_BETA_FS_DOMAIN_CONTRACT_V1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'existing_decay_input': {'commit': '9620e1fcc4bdda76e0311206f614234926600381',
            'blob': '33fd920abce6cc28ff26a850b030bb7b4fd2462e',
            'sha256': hashlib.sha256(prior_raw).hexdigest(), 'bytes': len(prior_raw),
            'energy_fields': 'ABSENT; not inferred from lifetimes or prior ODE'},
        'energy_inputs': {'neutron_beta': neutron, 'tritium_beta': tritium},
        'domain': {'carrier': 'electron', 'energy_kind': 'kinetic', 'units': 'eV',
            'lower_eV': str(energies[0]), 'upper_eV': str(energies[-1]),
            'source_file': str(fs.relative_to(ROOT.parent)), 'source_sha256': fs_sha,
            'source_bytes': len(fs_raw), 'rows': len(energies),
            'first_row': numeric_lines[0], 'last_row': numeric_lines[-1],
            'source_tar_url': 'https://cosmicdawn.astro.ucla.edu/elec_interp.tar',
            'source_tar_sha256': 'e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101',
            'header_warning': 'Upstream Photon Energy label is an electron-energy table label defect; use parent FS audit contract',
            'admission': 'ENERGY_DOMAIN_ACCOUNTING_ONLY; not deposition or bath/axis/closure approval'},
        'electron_mass_energy': {'central_eV': '510998.95069', 'standard_uncertainty_eV': '0.00016',
            'source': 'NIST 2022 CODATA',
            'url': 'https://physics.nist.gov/cuu/pdf/wall_2022.pdf',
            'retrieval_evidence': 'FORMAT_AND_CONSTANT_TOOL.json; primary indexed value',
            'uncertainty_propagation': 'NOT_RUN'},
        'model': {'name': 'ILLUSTRATIVE_ALLOWED_FERMI_ONE',
            'w': 'sqrt(T*(T+2*M))*(T+M)*(Q-T)^2',
            'not_evaluated_beta_spectrum': True, 'fit_to_evaluated_mean': False,
            'omissions': ['Coulomb/Fermi function', 'daughter recoil and weak magnetism',
                'radiative corrections and radiative branch', 'atomic or molecular final states',
                'screening/exchange', 'forbidden shape corrections', 'neutrino mass'],
            'ownership': {'input_to_FS': 'primary electron kinetic energy only',
                'neutrino': 'separate; never deposited by FS electron table',
                'daughter_recoil': 'separate unresolved physical channel, not treated as zero',
                'born_neutron_proton_kinetic': 'REJECT; requires species-specific transport/stopping',
                'low_and_high_electron_tails': 'UNRESOLVED; no zero-fill or automatic heat allocation'}},
        'acceptance': {'quad_fraction_abs_tolerance': 2e-12,
            'independent_moment_relative_tolerance': 2e-11,
            'mpmath_dps': 80, 'scipy_epsabs': 1e-13, 'scipy_epsrel': 2e-13,
            'global_error_bound': None, 'historical_ODE_calls': 0,
            'cpu_id': 5, 'native_threads_per_worker': 1, 'numerical_process_wall_budget_s': 60},
        'source_format': {'url': 'https://www-nds.iaea.org/exfor/x4guide/manuals/endf-manual.pdf',
            'section': '8.4, MF8/MT457; spectrum normalization ERAV and branch Q',
            'Q_note': 'total energy available; not necessarily maximum radiation energy'},
        'publication': 'PARENT_PENDING', 'backup': 'PARENT_PENDING',
        'high_energy_nuclear_network': 'HOLD',
    }
    save_new(SOURCE / 'EVALUATED_ENERGY_AND_DOMAIN_CONTRACT.json', contract)
    print(json.dumps({'status': 'SOURCE_CONTRACT_WRITTEN', 'isotopes': list(contract['energy_inputs']),
        'source_read_only': True, 'historical_ODE_calls': 0}, ensure_ascii=False))

if __name__ == '__main__':
    main()
