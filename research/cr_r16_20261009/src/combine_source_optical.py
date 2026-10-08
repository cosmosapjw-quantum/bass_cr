"""R16 conditional source + time optical-depth enclosure for one FT03 macro.

This is a deterministic Minkowski-sum transfer of TWO donor-certified error
statements under an explicit same-parameter model/clock/observable contract.
It does NOT independently certify either donor interval implementation.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,json

R15_SHA='0fe656016c1de11fa2d4d1e5dd0227bdd79d0b2e53ee1ad253b49290725ac5aa'
BRIDGE14_SHA='5fc3b77d9a17553f7cd34f61711983776edbb992ba9ebd294420b9813a818515'
REI13_SHA='a3971b386edb9dc585b8657ea095ab171159b7881a52a59f574d0ef694538b48'

class ContractError(ValueError):pass

def num(v):
    if isinstance(v,dict):return F(int(v['num']),int(v['den']))
    if v is None:raise ContractError('MISSING_BOUND')
    return F(v)

def combine_bounds(r15_interval:tuple[F,F],source_abs_upper:F):
    if r15_interval is None or len(r15_interval)!=2:
        raise ContractError('TIME_ERROR_INTERVAL_REQUIRED')
    a,b=map(num,r15_interval);d=num(source_abs_upper)
    if a>b:raise ContractError('INVALID_TIME_ERROR_INTERVAL')
    if d<0:raise ContractError('NEGATIVE_SOURCE_BOUND')
    return a-d,b+d

def encode(x):
    if isinstance(x,F):return {'num':str(x.numerator),'den':str(x.denominator),'float':float(x)}
    if isinstance(x,(tuple,list)):return [encode(y) for y in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x

def run(r15_zip:Path, bridge14_zip:Path) -> dict:
    r15_zip,bridge14_zip=map(Path,(r15_zip,bridge14_zip))
    if hashlib.sha256(r15_zip.read_bytes()).hexdigest()!=R15_SHA:
        raise ContractError('R15_IMMUTABLE_ZIP_MISMATCH')
    if hashlib.sha256(bridge14_zip.read_bytes()).hexdigest()!=BRIDGE14_SHA:
        raise ContractError('BRIDGE14_IMMUTABLE_ZIP_MISMATCH')
    with ZipFile(r15_zip) as z:
        if z.testzip() is not None:raise ContractError('R15_CRC_FAIL')
        R=json.loads(z.read('source/research/cr_xthread_r15_20261008/RESULTS.json'))
        N=json.loads(z.read('source/research/cr_xthread_r15_20261008/SOURCE_BINDING.json'))
        parent=z.read('inputs/REI_XTHREAD_BRIDGE13_20261008.zip')
        if hashlib.sha256(parent).hexdigest()!=REI13_SHA:
            raise ContractError('SOURCE_PARENT_IDENTITY')
    with ZipFile(bridge14_zip) as z:
        if z.testzip() is not None:raise ContractError('BRIDGE14_CRC_FAIL')
        r='rei_bridge14_20261008/'
        B=json.loads(z.read(r+'results/SOURCE_MEASURE_CERTIFICATE.json'))
        C=json.loads(z.read(r+'SOURCE_ERROR_AND_LEDGER_CONTRACT.json'))
        S=json.loads(z.read(r+'SOURCE_BINDING.json'))
    if S.get('parent_archive',{}).get('sha256')!=REI13_SHA:
        raise ContractError('MISMATCHED_REI13_DONOR')
    if R.get('scope')!='fixed-six-birth shadow continuum; first macro only' or R.get('time_s')!=B['domain']['time_s'] or R.get('cells')!=32:
        raise ContractError('INCOMPATIBLE_TIME_OR_SOURCE_TARGET')
    if B.get('mass',{}).get('gauss_births')!=6 or B.get('mass',{}).get('continuous_source_s_inverse')!=5e-15:
        raise ContractError('INCOMPATIBLE_GAUSS_SOURCE')
    if B.get('claim')!='CONDITIONAL_COUPLED_FINITE_SOURCE_MEASURE_UNIFORM_BOUND':
        raise ContractError('BRIDGE14_PROOF_STATUS')
    if not C.get('source_only_partial_tau_upper'):
        raise ContractError('MISSING_THOMSON_UPPER')
    assert R['physical']=='HOLD' and B['energy_identity']=='algebraic uniform exact only; native accumulated interval-ledger separate'
    dcert=num(B['decimal_upper_bounds']['partial_tau_source_only'])
    if num(C['source_only_partial_tau_upper']) != dcert:
        raise ContractError('SOURCE_BOUND_CONTRACT_MISMATCH')
    dsafe=num('1.021773e-17') # outward conservative public bound
    if dsafe<dcert:raise ContractError('PUBLIC_SOURCE_BOUND_NOT_SAFE')
    # R15 uses c_SI*sigma_SI*(cm^-3 -> m^-3); REI uses c_cgs*sigma_cgs.
    # Both represent the same dimensioned observable but their binary64 literals
    # may differ by one ulp. Conservatively dilate the donor bound if needed.
    ct_r15=F(299792458)*F.from_float(6.6524587e-29)*10**6
    ct_rei=F.from_float(29979245800.0)*F.from_float(6.6524587e-25)
    factor=max(F(1),ct_r15/ct_rei)
    source=dsafe*factor
    prior=tuple(num(t) for t in R['signed_tau_difference_interval'])
    combined=combine_bounds(prior,source)
    return {
        'task':'BASS-CR-XTHREAD-R16A',
        'status':'CONDITIONAL_CONTINUOUS_EMISSION_FIRST_MACRO_TAU_SIGN_TRANSFER',
        'same_model_checked':'FT03 prescribed FLRW same six-birth shadow and same initial theta; only source measure changed',
        'source_constant_S_photons_perH_s':'5e-15',
        'source_REI13_SHA256':REI13_SHA,'source_BRIDGE14_SHA256':BRIDGE14_SHA,
        'R15_SHA256':R15_SHA,'time_s':R['time_s'],
        'time_error_signed':prior,
        'source_only_original_decimal_upper':dcert,
        'source_only_safe_contract_upper':dsafe,
        'Thomson_CT_R15_over_donor':ct_r15/ct_rei,
        'source_only_used_upper':source,
        'combined_contS_continuum_minus_native':combined,
        'combined_sign_strict_positive':combined[0]>0,
        'native_tau':tuple(num(t) for t in R['tau_native_piecewise_defined']),
        'continuous_emission_tau':(num(R['tau_native_piecewise_defined'][0])+combined[0],num(R['tau_native_piecewise_defined'][1])+combined[1]),
        'proof_basis':'R15 signed interval + BRIDGE14 source-only BV/CDF gas feedback uniform bound + triangle inequality',
        'not_certified':['new independent interval backend','physical atomic-fit accuracy','whole history or observer tail','compiled native gas/work ledger','Bianchi', 'HE/RCT/HH/CR ON']
    }

if __name__=='__main__':
    arg=argparse.ArgumentParser();arg.add_argument('--r15-zip',required=True,type=Path);arg.add_argument('--bridge14-zip',required=True,type=Path);arg.add_argument('--output',required=True,type=Path)
    a=arg.parse_args();result=run(a.r15_zip,a.bridge14_zip)
    if a.output.exists():raise FileExistsError('CREATE_ONLY_OUTPUT')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(encode(result),indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:encode(result[k]) for k in ('time_error_signed','source_only_used_upper','combined_contS_continuum_minus_native','combined_sign_strict_positive')},indent=2))
