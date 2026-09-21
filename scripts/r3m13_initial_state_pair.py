#!/usr/bin/env python3
"""R3M13 preparation-only diagnostics. No collision run or b-grid admission.

Keep this file OUTSIDE cr_repro: the existing checkpoint source_digest hashes
all cr_repro/*.py. Atomic units internally; probability intervals are floating
evaluations of an exact conditional theorem, not interval-certified results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np

# Support a source checkout without pip install, but never replace its files.
ROOT = Path(__file__).resolve().parents[1]
if (ROOT / "cr_repro").is_dir():
    sys.path.insert(0, str(ROOT))

EXPECTED_SOURCE_DIGEST = "581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b"
PREP_KEYS = {"imag_dt", "imag_steps"}
CHUNK = 65536


def _positive(x, name):
    if isinstance(x, bool):
        raise ValueError(f"{name}: boolean not allowed")
    x = float(x)
    if not math.isfinite(x) or x <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return x


def _sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def _object(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f"duplicate JSON key: {k}")
        d[k] = v
    return d


def load_json(path):
    def bad(token):
        raise ValueError(f"nonfinite JSON token: {token}")
    return json.loads(Path(path).read_text(), object_pairs_hook=_object,
                      parse_constant=bad)


def _json_digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def current_source_digest():
    from cr_repro.r3m11 import source_digest
    return source_digest()


def validate_preparation_config(cfg):
    if cfg.get("initial_state") != "imag_time":
        raise ValueError("initial_state must explicitly be imag_time")
    tau = _positive(cfg["imag_dt"], "imag_dt")
    n = cfg["imag_steps"]
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("imag_steps must be a positive integer")
    for key in ["dt", "absorber_reference_dt", "energy_keV_per_u"]:
        _positive(cfg[key], key)
    if not math.isfinite(float(cfg["b"])) or float(cfg["b"]) < 0:
        raise ValueError("invalid impact parameter")
    if not math.isfinite(float(cfg["z_start"])) or not math.isfinite(float(cfg["z_stop"])):
        raise ValueError("nonfinite trajectory limits")
    if not cfg["z_stop"] > cfg["z_start"]:
        raise ValueError("trajectory stop must exceed start")
    if any(k.startswith("_r3m11") for k in cfg):
        raise ValueError("use the original input config, not an enriched result config")
    from cr_repro.grid import GridSpec
    spec = GridSpec.from_dict(cfg["grid"])
    if min(spec.shape()) < 2:
        raise ValueError("grid must have at least two nodes per axis")
    # Catch NaN even in otherwise opaque/optional config fields.
    _json_digest(cfg)
    return tau * n


def dynamics_fingerprint(cfg):
    validate_preparation_config(cfg)
    return _json_digest({k: v for k, v in cfg.items() if k not in PREP_KEYS})


def validate_pair_configs(first, second):
    t1 = validate_preparation_config(first)
    t2 = validate_preparation_config(second)
    if dynamics_fingerprint(first) != dynamics_fingerprint(second):
        raise ValueError("dynamics/projector/grid configs differ outside preparation keys")
    if not math.isclose(t1, t2, rel_tol=2e-14, abs_tol=0):
        raise ValueError("total preparation time differs")
    return {"same_total_preparation_time": True,
            "total_preparation_time_au": t1,
            "same_dynamics_fingerprint": dynamics_fingerprint(first)}


def ray_distance(a, b, dv):
    """Weighted phase-aligned distance; never silently renormalize inputs.

    Direct aligned differences avoid cancellation in sqrt(2-2|overlap|).
    Chunked sums keep additional memory bounded for mmap input arrays.
    """
    dv = _positive(dv, "dv")
    a, b = np.asarray(a), np.asarray(b)
    if a.shape != b.shape or a.size == 0 or a.ndim < 1:
        raise ValueError("nonempty identical state shapes required")
    if a.dtype.kind not in "fc" or b.dtype.kind not in "fc":
        # Allow integer test vectors after explicit numerical conversion.
        if a.dtype.kind not in "fci" or b.dtype.kind not in "fci":
            raise ValueError("numeric real/complex states required")
    af, bf = a.reshape(-1), b.reshape(-1)
    aa, bb, re, im = [], [], [], []
    for k in range(0, af.size, CHUNK):
        x, y = af[k:k+CHUNK], bf[k:k+CHUNK]
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("nonfinite initial state")
        aa.append(float(np.vdot(x, x).real) * dv)
        bb.append(float(np.vdot(y, y).real) * dv)
        ov = np.vdot(x, y) * dv
        re.append(float(ov.real)); im.append(float(ov.imag))
    na, nb = math.fsum(aa), math.fsum(bb)
    if abs(na-1.) > 2e-10 or abs(nb-1.) > 2e-10:
        raise ValueError("states must be normalized in the supplied grid measure")
    ov = complex(math.fsum(re), math.fsum(im))
    phase = ov.conjugate() / abs(ov) if abs(ov) else 1.+0j
    dd = []
    for k in range(0, af.size, CHUNK):
        z = af[k:k+CHUNK] - phase * bf[k:k+CHUNK]
        dd.append(float(np.vdot(z, z).real) * dv)
    d = math.sqrt(max(0., math.fsum(dd)))
    if d > math.sqrt(2.) + 2e-9:
        raise ValueError("inconsistent phase-aligned distance")
    d = min(d, math.sqrt(2.))
    return dict(ray_distance=d, trace_distance=d*math.sqrt(max(0., 1.-d*d/4.)),
                abs_overlap=abs(ov), norm_first=na, norm_second=nb,
                roundoff_certified=False)


def sufficient_ray_distance(p, relative_screen):
    p = float(p); s = _positive(relative_screen, "relative_screen")
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("probability must lie in [0,1]")
    # Rationalized form avoids sqrt(1+s)-1 cancellation.
    return math.sqrt(p) * s / (math.sqrt(1.+s)+1.)


def probability_interval(p, d, relative_screen=.01):
    p, d = float(p), float(d)
    s = _positive(relative_screen, "relative_screen")
    if not math.isfinite(p) or not 0 <= p <= 1:
        raise ValueError("probability must lie in [0,1]")
    if not math.isfinite(d) or not 0 <= d <= math.sqrt(2.) + 2e-15:
        raise ValueError("invalid ray distance")
    d = min(d, math.sqrt(2.))
    D = d * math.sqrt(max(0., 1.-d*d/4.))
    lo = max(0., max(0., math.sqrt(p)-d)**2, p-D)
    hi = min(1., (math.sqrt(p)+d)**2, p+D)
    error = max(p-lo, hi-p)
    return dict(lower=lo, upper=hi, absolute_change_upper=error,
                relative_error_upper=(error/p if p > 0 else None),
                floating_pair_screen=bool(p > 0 and error <= s*p),
                relative_screen=s,
                sufficient_ray_distance=sufficient_ray_distance(p, s),
                reference_anchor_verified=False,
                roundoff_certified=False, physical_admission=False, bgrid="NO_GO",
                assumptions="NORMALIZED_INITIALS_SAME_CONTRACTIVE_K_SAME_PROJECTOR_Q_NO_POSTSELECTION",
                scope="PAIR_ONLY_NOT_GROUND_STATE_CONVERGENCE_OR_TOTAL_ERROR")


def prepare(cfg, outdir):
    """Prepare exactly the inherited initial state; no collision .run call.

    Preparation itself is not restartable. A failure retains an explicit attempt
    receipt; use a fresh output directory to retry. Completed states are reusable.
    """
    from cr_repro.r3m11 import ControlledTDLRunner
    from cr_repro.backend import asnumpy
    from cr_repro.util import atomic_json, atomic_npy
    validate_preparation_config(cfg)
    if current_source_digest() != EXPECTED_SOURCE_DIGEST:
        raise ValueError("unexpected numerical source: reconcile before execution")
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=False)
    atomic_json(out/"attempt.json", {"status": "STARTED", "config": cfg,
                "collision_propagation_executed": False})
    tic = time.monotonic()
    try:
        runner = ControlledTDLRunner(cfg)
        psi, info = runner.relaxed_initial()
        xp = runner.xp
        # The final reported historical energy can be from a previous monitoring
        # step on short fixtures. Recompute E and residual at the actual final psi.
        energy = runner.target_energy(psi)
        hp = xp.fft.ifftn(.5*runner.k2*xp.fft.fftn(psi)) + runner.Vtarget*psi
        residual = float(asnumpy(xp.sqrt(xp.sum(abs(hp-energy*psi)**2)*runner.dv)))
        info = dict(info, energy_Eh=energy, stationary_residual_Eh=residual)
        ph = xp.exp(-.5j*runner.dt_actual*runner.Vtarget)
        u0psi = ph*xp.fft.ifftn(runner.kin*xp.fft.fftn(ph*psi))
        host = asnumpy(psi)
        ray = ray_distance(host, asnumpy(u0psi), runner.dv)
        # CAP version is deliberately not renormalized.
        cp = ph*runner.cap_half
        ucap = cp*xp.fft.ifftn(runner.kin*xp.fft.fftn(cp*psi))
        cap_norm = runner.norm(ucap)
        if current_source_digest() != EXPECTED_SOURCE_DIGEST:
            raise ValueError("numerical source changed during preparation")
        atomic_npy(out/"initial.npy", host)
        receipt = dict(schema="BASS_CR_R3M13_PREPARATION_V1", status="COMPLETE",
          config=cfg, shape=list(host.shape), dv=runner.dv,
          source_digest=current_source_digest(), script_sha256=_sha(__file__),
          dynamics_fingerprint=dynamics_fingerprint(cfg),
          initial_state_sha256=_sha(out/"initial.npy"),
          initial=info, seconds=time.monotonic()-tic,
          total_preparation_time_au=cfg["imag_dt"]*cfg["imag_steps"],
          environment=dict(python=platform.python_version(), numpy=np.__version__,
                           backend=runner.backend),
          target_only=dict(projectile_potential_included=False,
                           dt_actual_au=runner.dt_actual,
                           no_cap_one_step_ray_defect=ray["ray_distance"],
                           cap_one_step_surviving_norm=cap_norm,
                           interpretation="DIAGNOSTIC_NOT_CAPTURE_PROBABILITY"),
          collision_propagation_executed=False, physical_rate_evaluated=False,
          bgrid="NO_GO", roundoff_certified=False)
        atomic_json(out/"receipt.json", receipt)
        atomic_json(out/"attempt.json", {"status": "COMPLETE"})
        return receipt
    except BaseException as exc:
        atomic_json(out/"attempt.json", {"status": "FAILED_OR_INTERRUPTED",
                    "exception": type(exc).__name__, "message": str(exc),
                    "seconds": time.monotonic()-tic,
                    "collision_propagation_executed": False})
        raise


def load_prepared(directory):
    directory = Path(directory)
    meta = load_json(directory/"receipt.json")
    if meta.get("status") != "COMPLETE" or meta.get("source_digest") != EXPECTED_SOURCE_DIGEST:
        raise ValueError("incomplete or incompatible preparation source")
    validate_preparation_config(meta["config"])
    if dynamics_fingerprint(meta["config"]) != meta["dynamics_fingerprint"]:
        raise ValueError("preparation config hash mismatch")
    p = directory/"initial.npy"
    if _sha(p) != meta["initial_state_sha256"]:
        raise ValueError("initial state hash mismatch")
    a = np.load(p, mmap_mode="r", allow_pickle=False)
    from cr_repro.grid import GridSpec
    grid = GridSpec.from_dict(meta["config"]["grid"])
    if a.shape != grid.shape() or list(a.shape) != meta["shape"] or grid.dv != meta["dv"]:
        raise ValueError("state/grid/measure mismatch")
    return a, meta


def compare(first_dir, second_dir, reference_probability, relative_screen=.01):
    a, ma = load_prepared(first_dir); b, mb = load_prepared(second_dir)
    checks = validate_pair_configs(ma["config"], mb["config"])
    if ma["source_digest"] != mb["source_digest"]:
        raise ValueError("different numerical source")
    distance = ray_distance(a, b, ma["dv"])
    return dict(schema="BASS_CR_R3M13_INITIAL_PAIR_V1", checks=checks,
      distance=distance,
      conditional_interval=probability_interval(reference_probability,
                              distance["ray_distance"], relative_screen),
      reference_probability=reference_probability, reference_anchor_verified=False,
      reference_note="SUPPLIED_SCENARIO_ANCHOR_NOT_AN_AUTOMATIC_BINDING_TO_ARCHIVED_COLLISION",
      first_state_sha256=ma["initial_state_sha256"],
      second_state_sha256=mb["initial_state_sha256"],
      first_stationary_residual_Eh=ma["initial"]["stationary_residual_Eh"],
      second_stationary_residual_Eh=mb["initial"]["stationary_residual_Eh"],
      physical_rate_evaluated=False, bgrid="NO_GO")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command", required=True)
    p=sub.add_parser("prepare"); p.add_argument("--config", required=True)
    p.add_argument("--out", required=True)
    c=sub.add_parser("compare"); c.add_argument("--first", required=True)
    c.add_argument("--second", required=True); c.add_argument("--out", required=True)
    c.add_argument("--reference-probability", type=float, required=True)
    c.add_argument("--relative-screen", type=float, default=.01)
    args=parser.parse_args()
    if args.command=="prepare":
        result=prepare(load_json(args.config), args.out)
    else:
        target=Path(args.out)
        if target.exists():
            raise FileExistsError("refuse to overwrite comparison evidence")
        result=compare(args.first,args.second,args.reference_probability,args.relative_screen)
        from cr_repro.util import atomic_json
        atomic_json(target,result)
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__ == "__main__":
    main()
