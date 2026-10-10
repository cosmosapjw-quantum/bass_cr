"""Conditional post-crossing impulses with distinct upstream event ledgers."""
from pathlib import Path
import hashlib
import importlib.util
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent
P_PATH = ROOT.parent / 'cr_phys02b_delay_20261010/causal_generator.py'
P_SHA = 'ea72b12d07bc500cb7c917c5e500325c6864da77cdd90637ddceab7aeddfa0da'
if hashlib.sha256(P_PATH.read_bytes()).hexdigest() != P_SHA:
    raise ValueError('PINNED_P02B_INPUT_MISMATCH')
spec = importlib.util.spec_from_file_location('conditional_p02b', P_PATH)
P = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = P
spec.loader.exec_module(P)

E0 = 1000.001
# Integer meV subtraction is represented once at the receiving boundary.
UPSTREAM = (
    ('HI_NIST_2p', 989797, 10204, 1, 0),
    ('HeI_NIST_singlet_1P', 978783, 21218, 0, 1),
)

def initial(generator):
    """Fresh grid projection; all downstream counters start at zero."""
    return np.column_stack([generator.impulse(row[1] / 1000) for row in UPSTREAM])

def observe(generator, states):
    rows = []
    for j, (label, residual, excitation, h_count, he_count) in enumerate(UPSTREAM):
        obs = generator.observe(states[:, j])
        obs.update({
            'upstream_channel': label,
            'residual_energy_meV': residual,
            'upstream_HI_NIST_2p_events': h_count,
            'upstream_HeI_NIST_singlet_events': he_count,
            'upstream_excitation_energy_eV': excitation / 1000,
            'downstream_HI_old_excitation_energy_eV': P.EXC[0] * obs['excitation_counts'][0],
            'downstream_HeI_old23s_excitation_energy_eV': P.EXC[1] * obs['excitation_counts'][1],
            'downstream_HeII_old_excitation_energy_eV': P.EXC[2] * obs['excitation_counts'][2],
            'combined_energy_ledger_eV': obs['energy_ledger_eV'] + excitation / 1000,
        })
        rows.append(obs)
    return rows

def channels(generator, states):
    """Resolved downstream energy channels, keeping species separate."""
    rows = observe(generator, states)
    keys = ('active_energy_eV', 'binding_energy_eV',
            'downstream_HI_old_excitation_energy_eV',
            'downstream_HeI_old23s_excitation_energy_eV',
            'downstream_HeII_old_excitation_energy_eV',
            'coulomb_heat_eV', 'cutoff_energy_eV')
    return np.array([[row[k] for k in keys] for row in rows])
