"""Typed count-only provider for an explicit discrete kinetic MODEL.

No actual source, Maxwellian continuum certificate or receiver is fabricated.
Piecewise-linear nodal envelopes define a model family, not physical truth
between nodes. All coefficient arithmetic is rational/interval arithmetic.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F
import hashlib,json
from .core import ContractError,rational,nonnegative,interval,sqrt_interval

REACTION='p_CR+H_g(1s)->H_CR(1s)+p_g'
OBSERVABLE='H0_CR_1s_FORMATION_COUNT__NOT_TOTAL_GAS_HII'
MEASURE='NORMALIZED_DISCRETE_VELOCITY_PROBABILITIES'

def decode_payload(data:bytes) -> dict:
    try:
        def no_duplicates(pairs):
            out={}
            for k,v in pairs:
                if k in out: raise ContractError('duplicate JSON key')
                out[k]=v
            return out
        obj=json.loads(data,object_pairs_hook=no_duplicates,
                       parse_constant=lambda x:(_ for _ in ()).throw(ContractError('nonfinite JSON')))
        if not isinstance(obj,dict): raise ContractError('JSON object required')
        return obj
    except (UnicodeError, json.JSONDecodeError) as e:
        raise ContractError('invalid JSON payload') from e

def pinned(data:bytes,expected_sha256:str) -> dict:
    if hashlib.sha256(data).hexdigest()!=expected_sha256:
        raise ContractError('SOURCE_OR_EVENT_IDENTITY_MISMATCH')
    return decode_payload(data)

@dataclass(frozen=True)
class SourceModel:
    source_id:str
    payload_sha256:str
    energies:tuple[F,...]
    envelopes:tuple[tuple[F,F],...]

    @classmethod
    def load(cls,data:bytes,sha256:str):
        o=pinned(data,sha256)
        required={'schema','source_id','profile','reaction','energy_kind','sigma_unit',
                  'interpolation','energies','sigma_envelopes'}
        if set(o)!=required: raise ContractError('source schema keys mismatch')
        fixed={'schema':'CX_LINEAR_MODEL_V1','profile':'MODEL','reaction':REACTION,
               'energy_kind':'E_CM_J','sigma_unit':'m^2',
               'interpolation':'PIECEWISE_LINEAR_MODEL_FAMILY'}
        if any(o[k]!=v for k,v in fixed.items()):
            raise ContractError('CHANNEL_ENERGY_PROFILE_OR_MODEL_MISMATCH')
        if not isinstance(o['source_id'],str) or not o['source_id'].strip():
            raise ContractError('source_id required')
        if not isinstance(o['energies'],list) or not isinstance(o['sigma_envelopes'],list):
            raise ContractError('source arrays required')
        e=tuple(map(nonnegative,o['energies']))
        s=tuple(interval(p) for p in o['sigma_envelopes'])
        if len(e)<2 or len(e)!=len(s) or any(a>=b for a,b in zip(e,e[1:])):
            raise ContractError('invalid source knot ordering')
        return cls(o['source_id'],sha256,e,s)

    def evaluate(self,energy) -> tuple[F,F]:
        import bisect
        e=nonnegative(energy)
        if e<self.energies[0] or e>self.energies[-1]: raise ContractError('OUT_OF_DOMAIN')
        i=min(bisect.bisect_right(self.energies,e)-1,len(self.energies)-2)
        t=(e-self.energies[i])/(self.energies[i+1]-self.energies[i])
        return tuple((1-t)*self.envelopes[i][k]+t*self.envelopes[i+1][k] for k in (0,1))

def distribution(items) -> tuple:
    if not isinstance(items,list) or not items: raise ContractError('empty distribution')
    out=[]
    for a in items:
        if not isinstance(a,dict) or set(a)!={'velocity_m_s','probability'} or not isinstance(a['velocity_m_s'],list) or len(a['velocity_m_s'])!=3:
            raise ContractError('distribution entry schema')
        out.append((tuple(map(rational,a['velocity_m_s'])),nonnegative(a['probability'])))
    if sum(p for _,p in out)!=1: raise ContractError('MEASURE_NORMALIZATION_UNKNOWN')
    return tuple(out)

def evaluate_count(source_data:bytes,source_sha256:str,event_data:bytes,event_sha256:str,
                   capability='formation_count_1s',bits=128) -> dict:
    if capability!='formation_count_1s': raise ContractError('UNSUPPORTED_CAPABILITY')
    src=SourceModel.load(source_data,source_sha256); e=pinned(event_data,event_sha256)
    required={'schema','event_id','origin','frame','time','measure','density_unit',
              'projectile_mass_kg','target_mass_kg','n_CR','n_HI','projectile','target',
              'outgoing_acceptance'}
    if set(e)!=required: raise ContractError('event schema keys mismatch')
    fixed={'schema':'CX_DISCRETE_EVENT_V1','origin':'model_defined','frame':'gas_tetrad',
           'time':'proper_seconds','measure':MEASURE,'density_unit':'m^-3',
           'outgoing_acceptance':'POPULATION_LABEL_ONLY_NO_OUTGOING_THRESHOLD'}
    if any(e[k]!=v for k,v in fixed.items()): raise ContractError('FRAME_TIME_MEASURE_OR_ACCEPTANCE_MISMATCH')
    if not isinstance(e['event_id'],str) or not e['event_id'].strip(): raise ContractError('event_id')
    mp=nonnegative(e['projectile_mass_kg']); mt=nonnegative(e['target_mass_kg'])
    if not mp or not mt: raise ContractError('positive masses required')
    mu=mp*mt/(mp+mt); np=nonnegative(e['n_CR']); nh=nonnegative(e['n_HI'])
    p=distribution(e['projectile']); h=distribution(e['target'])
    lo=hi=F(0); entries=[]
    for v,pv in p:
        for w,pw in h:
            if pv*pw==0: continue
            g2=sum((x-y)**2 for x,y in zip(v,w)); energy=mu*g2/2
            sl,sh=src.evaluate(energy); gl,gh=sqrt_interval(g2,bits)
            q=pv*pw; kl=q*sl*gl; kh=q*sh*gh; lo+=kl;hi+=kh
            entries.append({'E_CM_J':str(energy),'weight':str(q),
                            'K_interval':[str(kl),str(kh)]})
    return {'schema':'CX_COUNT_REFERENCE_V1','observable':OBSERVABLE,
            'profile':'MODEL','measure':MEASURE,'source_id':src.source_id,
            'source_sha256':source_sha256,'event_sha256':event_sha256,
            'K_1s_m3_s':[str(lo),str(hi)],'R_1s_m_minus3_s':[str(np*nh*lo),str(np*nh*hi)],
            'bound_type':'DETERMINISTIC_FOR_DISCRETE_LINEAR_MODEL_FAMILY',
            'continuous_distribution_error':None,'source_model_discrepancy':None,
            'admitted_capabilities':['formation_count_1s'],
            'free_electron_source_elementary_reaction':'0',
            'momentum_or_heat':None,'reservoir_transfer':None,
            'physical_admission':False,'actual_host_bound':False,
            'pair_contributions':entries}
