"""Instantaneous full S/H/D provider for TP1. No capture or propagation."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import numpy as np

from full_operator import assemble_full
from bass_foundations.radial_basis import readonly


def _freeze_record(record):
    return tuple(sorted(record.items()))


def _file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _identity(trajectory, channels, same_order, cross_order):
    import full_operator, aligned_cross
    payload={
        'trajectory': trajectory.record(),
        'channels': [c.record() for c in channels],
        'same_order': int(same_order),
        'cross_order': int(cross_order),
        'full_operator_sha256': _file_sha(full_operator.__file__),
        'aligned_cross_sha256': _file_sha(aligned_cross.__file__),
    }
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class OperatorSnapshot:
    t: float
    S: np.ndarray
    H: np.ndarray
    D: np.ndarray
    diagnostics: dict
    identity: str
    channel_records: tuple


class OperatorProvider:
    def __init__(self, trajectory, channels, *, same_order=20, cross_order=24,
                 expected_channel_records=None,
                 hermiticity_relative_max=1e-11, metric_min_ratio=1e-8):
        self.trajectory=trajectory
        self.channels=tuple(channels)
        if not self.channels:
            raise ValueError('nonempty channels required')
        self.same_order=int(same_order);self.cross_order=int(cross_order)
        records=[c.record() for c in self.channels]
        if expected_channel_records is not None and list(expected_channel_records) != records:
            raise ValueError('channel identity mismatch')
        self.channel_records=tuple(_freeze_record(x) for x in records)
        self.hermiticity_relative_max=float(hermiticity_relative_max)
        self.metric_min_ratio=float(metric_min_ratio)
        self.identity=_identity(trajectory,self.channels,self.same_order,self.cross_order)
        self._cache={}
        self.evaluation_count=0

    def at(self,t):
        t=float(t)
        if not np.isfinite(t):
            raise ValueError('finite time required')
        key=np.float64(t).tobytes()
        if key in self._cache:
            return self._cache[key]
        x=assemble_full(self.trajectory,self.channels,t,
                        same_order=self.same_order,cross_order=self.cross_order)
        S=np.asarray(x['S'],complex);H=np.asarray(x['H'],complex);D=np.asarray(x['D'],complex)
        if any(a.shape != S.shape or not np.isfinite(a).all() for a in (S,H,D)) or S.ndim != 2 or S.shape[0] != S.shape[1]:
            raise ArithmeticError('operator shape/finiteness unresolved')
        sdef=float(np.linalg.norm(S-S.conj().T)/max(np.linalg.norm(S),1e-300))
        hdef=float(np.linalg.norm(H-H.conj().T)/max(np.linalg.norm(H),1e-300))
        Sh=(S+S.conj().T)/2
        ev=np.linalg.eigvalsh(Sh)
        ratio=float(ev[0]/ev[-1]) if ev[-1] > 0 else -1.
        if sdef > self.hermiticity_relative_max or hdef > self.hermiticity_relative_max:
            raise ArithmeticError('operator Hermiticity screen failed')
        if ratio < self.metric_min_ratio:
            raise ArithmeticError('metric positivity/rank screen failed')
        diag=dict(x.get('diagnostics',{}))
        diag.update(S_hermiticity_relative=sdef,H_hermiticity_relative=hdef,
                    metric_min=float(ev[0]),metric_max=float(ev[-1]),metric_ratio=ratio)
        snap=OperatorSnapshot(t,readonly(S),readonly(H),readonly(D),diag,
                              self.identity,self.channel_records)
        self._cache[key]=snap
        self.evaluation_count+=1
        return snap


def metric_derivative_residual(provider,t,epsilon_t):
    t=float(t);epsilon_t=float(epsilon_t)
    if not np.isfinite(epsilon_t) or epsilon_t<=0:
        raise ValueError('positive finite epsilon_t required')
    m=provider.at(t-epsilon_t)
    c=provider.at(t)
    p=provider.at(t+epsilon_t)
    sdot=(p.S-m.S)/(2*epsilon_t)
    direct=c.D+c.D.conj().T
    den=max(float(np.linalg.norm(sdot)),float(np.linalg.norm(direct)),1e-300)
    return {
        't':t,'epsilon_t':epsilon_t,
        'relative_residual':float(np.linalg.norm(sdot-direct)/den),
        'Sdot_fd':readonly(sdot),'D_plus_Ddagger':readonly(direct),
        'provider_identity':provider.identity,
    }
