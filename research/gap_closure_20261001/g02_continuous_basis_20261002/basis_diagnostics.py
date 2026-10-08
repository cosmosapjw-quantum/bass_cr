"""Independent exact-polynomial and weak-FEM diagnostics of the R4X candidate.

No candidate normalization, eigensolve, projection, or physical propagation.
The original discontinuous-to-continuous derivative difference is a broken
cellwise L2 quantity, not a global H1 difference.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2]
sys.path.insert(0, str(SOURCE/'research/foundation_rebuild/src'))
from bass_foundations.kernels import radial_fem
from basis_representation import load_candidate


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def coefficients(mode, cell):
    """Expand actual stored factored bytes using independent exact arithmetic."""
    left, right = map(F.from_float, map(float, mode.shared_endpoint_values[cell:cell+2]))
    bubble = [F.from_float(float(x)) for x in mode.bubble_coefficients[cell]]
    c = [left, right-left] + [F(0)]*len(bubble)
    for k, q in enumerate(bubble):
        c[k+1] += q
        c[k+2] -= q
    return c


def product_integral(a, b):
    return sum((x*y/F(i+j+1) for i, x in enumerate(a)
                for j, y in enumerate(b)), F(0))


def derivative(c):
    return [i*x for i, x in enumerate(c)][1:]


def value(c, s):
    return sum((x*s**k for k, x in enumerate(c)), F(0))


def analyze(candidate, inputs):
    candidate, inputs = Path(candidate), Path(inputs)
    modes = load_candidate(candidate)
    meta = json.loads((inputs/'BASIS.json').read_text())
    context = json.loads((inputs/'SCIENCE_CONTEXT.json').read_text())
    contract = json.loads((HERE/'TASK_CONTRACT.json').read_text())
    for name, expected in contract['original_inputs'].items():
        if sha(inputs/name) != expected:
            raise ValueError('original input identity mismatch: '+name)
    with np.load(inputs/'BASIS.npz', allow_pickle=False) as z:
        original = {k: np.array(z[k]) for k in z.files}
    # Archive field names are inspected, never inferred from a candidate.
    old = original['coefficients']
    if len(old) != len(modes):
        raise ValueError('original/candidate mode count mismatch')
    spec = context['context']['contract']['radial_spec']
    rows = []
    vectors = []
    exact_polys = []
    matrices = {}
    x, w = leggauss(32)
    for index, (mode, oldcoef) in enumerate(zip(modes, old)):
        if oldcoef.shape != (len(mode.edges)-1, mode.degree+1):
            raise ValueError('original/candidate dimensions differ')
        cells = [coefficients(mode, e) for e in range(len(oldcoef))]
        exact_polys.append(cells)
        mass = diffmass = oldmass = derivdiff = affine_round_mass = F(0)
        nodal_rounding_max = F(0)
        maximum_jump = F(0)
        nodal = []
        for e, (c, previous) in enumerate(zip(cells, oldcoef)):
            h = F.from_float(float(mode.edges[e+1]))-F.from_float(float(mode.edges[e]))
            a = [F.from_float(float(v)) for v in previous]
            delta = [u-v for u, v in zip(c, a)]
            affine = list(a)
            left = F.from_float(float(mode.shared_endpoint_values[e]))
            right = F.from_float(float(mode.shared_endpoint_values[e+1]))
            affine[0] += left-a[0]
            affine[1] += right-sum(a)-(left-a[0])
            round_delta = [u-v for u,v in zip(c,affine)]
            affine_round_mass += h*product_integral(round_delta,round_delta)
            mass += h*product_integral(c, c)
            oldmass += h*product_integral(a, a)
            diffmass += h*product_integral(delta, delta)
            derivdiff += product_integral(derivative(delta), derivative(delta))/h
            if e:
                maximum_jump = max(maximum_jump, abs(c[0]-sum(cells[e-1])))
            for j in range(mode.degree):
                exact_node=value(c,F(j,mode.degree))
                rounded=float(exact_node)
                nodal_rounding_max=max(nodal_rounding_max,abs(F.from_float(rounded)-exact_node))
                nodal.append(rounded)
        nodal.append(float(sum(cells[-1])))
        nodal = np.asarray(nodal)
        if not np.array_equal(nodal, mode.reconstructed_nodal_values):
            raise ValueError('candidate reconstructed nodal bytes disagree with exact polynomial')
        vectors.append(nodal[1:-1])
        if mode.l not in matrices:
            matrices[mode.l] = radial_fem(spec['radius'], spec['elements'], spec['degree'],
                l=mode.l, quad_order=spec['quad_order'], grading=spec['grading'])
        H, M, mesh = matrices[mode.l]
        if not np.array_equal(mesh['edges'], mode.edges):
            raise ValueError('weak FEM mesh identity mismatch')
        c = nodal[1:-1]
        hc, mc = H@c, M@c
        residual = float(np.linalg.norm(hc-mode.energy*mc))
        denom = (np.linalg.norm(H, 2)+abs(mode.energy)*np.linalg.norm(M, 2))*np.linalg.norm(c)
        rayleigh = float(c@hc/(c@mc))
        r = ((mode.edges[1:]+mode.edges[:-1])[:, None]/2
             +np.diff(mode.edges)[:, None]*x/2).ravel()
        weights = (np.diff(mode.edges)[:, None]*w/2).ravel()
        u, du = mode.evaluate(r)
        numeric_mass = float(np.dot(weights, u*u))
        rows.append({'mode':index, 'l':mode.l, 'principal_n':mode.principal_n,
            'identity':mode.identity, 'energy_Eh':mode.energy,
            'exact_internal_jump':str(maximum_jump),
            'exact_origin_trace':str(cells[0][0]), 'exact_outer_trace':str(sum(cells[-1])),
            'exact_norm_squared':str(mass), 'norm_squared_float':float(mass),
            'normalization_absolute_defect':float(abs(mass-1)),
            'relative_radial_L2_change':float(diffmass/oldmass)**.5,
            'relative_L2_change_from_exact_affine_lift':float(affine_round_mass/oldmass)**.5,
            'maximum_nodal_rounding_absolute':float(nodal_rounding_max),
            'cellwise_radial_derivative_L2_change':float(derivdiff)**.5,
            'derivative_difference_semantics':'BROKEN_CELLWISE_L2_NOT_GLOBAL_H1',
            'weak_FEM_residual_absolute':residual,
            'weak_FEM_residual_relative_backward':float(residual/denom),
            'weak_mass_norm_squared':float(c@mc),
            'rayleigh_energy_Eh':rayleigh,
            'rayleigh_minus_stored_energy_Eh':rayleigh-mode.energy,
            'quadrature32_norm_squared':numeric_mass,
            'quadrature32_minus_exact_norm':numeric_mass-float(mass)})
    gram = np.zeros((len(modes),len(modes)))
    for i, m in enumerate(modes):
        for j, n in enumerate(modes):
            if m.l != n.l:
                continue
            v = F(0)
            for e, (a, b) in enumerate(zip(exact_polys[i],exact_polys[j])):
                h = F.from_float(float(m.edges[e+1]))-F.from_float(float(m.edges[e]))
                v += h*product_integral(a,b)
            gram[i,j] = float(v)
    orth = float(np.max(abs(gram-np.eye(len(modes)))))
    checks = {
        'exact_continuity_and_boundaries':all(r[k]=='0' for r in rows for k in ('exact_internal_jump','exact_origin_trace','exact_outer_trace')),
        'relative_L2_change':max(r['relative_radial_L2_change'] for r in rows)<=1e-12,
        'normalization':max(r['normalization_absolute_defect'] for r in rows)<=1e-10,
        'weak_FEM_residual':max(r['weak_FEM_residual_absolute'] for r in rows)<=2e-8,
        'energy_sign_resolved':all(abs(r['energy_Eh'])>100*r['weak_FEM_residual_absolute'] for r in rows),
        'same_l_orthogonality':orth<=1e-10,
    }
    return {'schema':'BASS_R4X_BASIS_DIAGNOSTICS_V1', 'modes':rows,
        'exact_same_l_gram_rounded_to_float':gram.tolist(),
        'same_l_orthogonality_max_absolute_defect':orth,
        'mass_matrix_condition_2':{str(l):float(np.linalg.cond(v[1])) for l,v in matrices.items()},
        'checks':checks, 'status':'PASS_LOCAL_BASIS_SCREENS' if all(checks.values()) else 'FAIL_LOCAL_BASIS_SCREENS',
        'source_sha256':sha(__file__), 'task_contract_sha256':sha(HERE/'TASK_CONTRACT.json'),
        'original_inputs':{n:sha(inputs/n) for n in contract['original_inputs']},
        'candidate_files':{p.name:sha(p) for p in sorted(candidate.iterdir()) if p.is_file()},
        'physical_claim':'No original nodal-vector recovery, no new eigensolve, no global H1 difference bound, no production admission',
        'G02':'UNRESOLVED', 'production':'HOLD', 'capture':False}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',required=True);p.add_argument('--inputs',required=True)
    p.add_argument('--output',required=True)
    args=p.parse_args()
    if Path(args.output).exists():raise ValueError('create-only output required')
    result=analyze(args.candidate,args.inputs)
    Path(args.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'checks':result['checks']}))
