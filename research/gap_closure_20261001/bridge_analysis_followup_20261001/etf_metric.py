"""Exact arithmetic for an oscillatory-ETF Gram lower bound, no native calls."""
from fractions import Fraction as F
from pathlib import Path
import argparse
import ast
import hashlib
import json
import math
from bridge_mass_certificate import display
from certify_reference_bridge import integer_sqrt_upper


def etf_metric_bound(kappa_l0, kappa_l1, relative_speed_minimum, directional_upper=F(67, 100)):
    k0, k1, v, L = map(F, (kappa_l0, kappa_l1, relative_speed_minimum, directional_upper))
    if min(k0, k1, L) < 0 or v <= 0:
        raise ValueError('nonnegative gradient bounds and positive relative speed required')
    directional_squared = max(k0/3, k1)
    if L*L < directional_squared:
        raise ValueError('directional derivative norm upper bound is insufficient')
    overlap = 2*L/v
    if overlap >= 1:
        raise ValueError('oscillatory bound does not establish positive metric')
    return {'directional_squared_upper': directional_squared,
        'directional_upper': L, 'cross_overlap_norm_upper': overlap,
        'full_center_normalized_gram_lower': 1-overlap}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-bridge', type=Path, required=True)
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('create-only certificate')
    old = json.loads(args.reference_bridge.read_text())
    blocks = {x['l']: F(x['same_center_gradient_norm_squared_upper_exact']) for x in old['radial_certificates']}
    if set(blocks) != {0, 1}:
        raise ValueError('l=0,1 certified radial block bounds required')
    bound = etf_metric_bound(blocks[0], blocks[1], 2)
    constants = args.repo_root/'cr_repro/constants.py'
    tree = ast.parse(constants.read_text())
    values = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)}
    h, mu = values['HARTREE_EV'], values['U_OVER_ME']
    exact_speed_squared = F(200000)/(F(h)*F(mu))
    if not F(4) < exact_speed_squared < F(9):
        raise ValueError('declared 100keV/u speed does not lie strictly between 2 and 3')
    # Same operation order as the source-pinned projectile_speed_au(100.).
    binary_speed = math.sqrt(2*(1000*100./h)/mu)
    if not F(2) <= F(binary_speed) <= F(3):
        raise ValueError('frozen binary source velocity outside theorem scope')
    # Reuse the prior conservative Hardy construction, changing only the metric
    # bound and v_min=2. This is still intentionally cancellation-insensitive.
    s0 = bound['full_center_normalized_gram_lower']
    orbital_gradient = integer_sqrt_upper(max(blocks.values()))
    vmin, vmax = F(2), F(3)
    K = (orbital_gradient**2+(orbital_gradient+vmax)**2)/s0
    B = vmax*orbital_gradient+vmax**2/2
    rate = K/2+4*integer_sqrt_upper(K)+B*integer_sqrt_upper(1/s0)
    integrated = 96*rate/vmin
    sources = [constants, args.repo_root/'cr_repro/observables.py',
        args.repo_root/'research/foundation_rebuild/src/bass_foundations/two_center.py',
        args.repo_root/'research/foundation_rebuild/ncp_shared_research_20260928/r4f_parallel_migration_20260929/worker_runtime.py']
    result = {'schema': 'BASS_ETF_OSCILLATORY_CONTINUUM_METRIC_V1',
        'status': 'EXACT_REFERENCE_ALL_DISPLACEMENT_METRIC_CERTIFIED',
        'reference_coefficients_sha256': old['reference_coefficients_sha256'],
        'input_gradient_certificate_sha256': hashlib.sha256(args.reference_bridge.read_bytes()).hexdigest(),
        'scope': 'same separately named H1 reference; both centers have complete l=0,1 blocks; relative ETF wavevector v e_z',
        'separation_domain': 'every center displacement, including R=0',
        'velocity_scope_exact': {'minimum': '2', 'maximum': '3'},
        'directional_derivative_squared_upper_exact': str(bound['directional_squared_upper']),
        'directional_derivative_squared_upper_display': display(bound['directional_squared_upper']),
        'directional_derivative_norm_upper_exact': str(bound['directional_upper']),
        'cross_overlap_norm_upper_exact': str(bound['cross_overlap_norm_upper']),
        'full_center_normalized_metric_lower_exact': str(s0),
        'full_center_normalized_metric_upper_exact': str(1+bound['cross_overlap_norm_upper']),
        'full_center_normalized_metric_condition_upper_exact': str((1+bound['cross_overlap_norm_upper'])/s0),
        'coordinate_scope': 'each center separately exactly L2-orthonormalized; raw coefficient bounds require its one-center mass factors',
        'speed_binding': {'energy_keV_per_u': '100', 'real_formula_squared_exact': str(exact_speed_squared),
            'frozen_source_binary_speed_hex': binary_speed.hex(), 'frozen_source_binary_speed_exact': str(F(binary_speed)),
            'frozen_source_binary_speed_display': repr(binary_speed), 'strict_interval_verified': [2, 3]},
        'source_pins': {str(f.relative_to(args.repo_root)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sources},
        'updated_conservative_bridge': {'same_proof_as': 'NAMED_REFERENCE_BRIDGE_CERTIFICATE.json',
            'z_domain_per_side': '[32,128] and [-128,-32]', 'constant_majorant_exact': str(rate),
            'constant_majorant_display': display(rate), 'integrated_majorant_per_side_exact': str(integrated),
            'integrated_majorant_per_side_display': display(integrated), 'target_per_side_exact': '1/200000',
            'target_certified': integrated <= F(1, 200000)},
        'reference_model_adopted': False, 'archived_native_metric_error_certified': False,
        'historical_state_or_temporal_gate_transferred': False,
        'new_native_calls': 0, 'new_physical_operator_queries': 0}
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'full_center_normalized_metric_lower_exact',
        'directional_derivative_squared_upper_display', 'speed_binding', 'updated_conservative_bridge')}))


if __name__ == '__main__':
    main()
