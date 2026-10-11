"""One create-only exact scalar analysis under the frozen PHYS02H budget."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import json
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT/'src'))
from exact_moments import (MomentError, check_identity, construct_model, horizon_bracket,
                           identity, load_exact, serializable)

CONTRACT_SHA256 = 'a49b1fa88c86d46c4e37cdb7ba37fbd44e5fa05511febc3a3089ab5ed5331dc4'
FRACTIONS = tuple(F(v) for v in ('0.5', '0.9', '0.95', '0.99', '0.999'))


def write(path, value):
    with path.open('x') as handle:
        json.dump(serializable(value), handle, indent=2, allow_nan=False)
        handle.write('\n')


def execute():
    started = time.monotonic()
    out = ROOT/'evidence/exact'
    contract_path = ROOT/'state/SCIENTIFIC_CONTRACT.json'
    if identity(contract_path)['sha256'] != CONTRACT_SHA256:
        raise MomentError('CONTRACT_IDENTITY_MISMATCH', str(contract_path))
    contract = json.loads(contract_path.read_text())
    pin = contract['immutable_inputs']['F_cached_artifact']
    source = REPO/pin['relative_to_repo']
    input_identity = check_identity(source, pin)
    code = {str(p.relative_to(ROOT)): identity(p) for p in
            (ROOT/'src/exact_moments.py', Path(__file__).resolve(), ROOT/'tests/test_exact_moments.py')}
    reservation = dict(start_utc=datetime.now(timezone.utc).isoformat(), command=sys.argv,
                       cwd=str(Path.cwd()), code=code, input=input_identity,
                       contract=identity(contract_path), actual_exact_analysis_runs=1,
                       call_counts=dict(G=0, pulse=0, expm=0, resolvent=0, linear_solve=0),
                       model_assignment=dict(requested='gpt-6.1-sol', role='exact_lower',
                           policy='ASTRA_TIER_ROUTING_POLICY', backend_attestation='NOT_AVAILABLE',
                           host_context_label='GPT-6 Astra Pro; not backend identity attestation'))
    write(out/'RESERVATION.json', reservation)
    receipt = dict(reservation)
    try:
        raw = load_exact(source)
        T = F(contract['exact_scalar']['constants']['T_s'])
        if raw['T_s'] != T:
            raise MomentError('INPUT_T_MISMATCH', 'source T differs from contract')
        models = {}
        for name in ('fullBED', 'legacy'):
            model = construct_model(raw['models'][name], T)
            certificates = [horizon_bracket(model, representation, fraction)
                            for representation in ('selected_record', 'birth_defined')
                            for fraction in FRACTIONS]
            models[name] = dict(model=model, certificates=certificates)
        count = sum(len(r['certificates']) for r in models.values())
        if count != 20:
            raise MomentError('CERTIFICATE_COUNT_MISMATCH', str(count))
        if time.monotonic()-started > 60:
            raise MomentError('ANALYSIS_WALL_BUDGET_EXCEEDED', '60 seconds')
        artifact = dict(schema='cr-phys02h-exact-moments.v1',
                        status='IMPLEMENTATION_VERIFIED_EXACT_RECORDED_DECIMAL_CERTIFICATES',
                        T_s=T, year_s=F(31557600), models=models, certificate_count=count,
                        scope=contract['exact_scalar']['scope'],
                        independent_review='NOT_PERFORMED_BY_IMPLEMENTATION_WORKER',
                        source=input_identity, code=code)
        write(out/'EXACT_CERTIFICATES.json', artifact)
        summary = dict(status=artifact['status'], certificate_count=count, scope=artifact['scope'],
                       models={name: dict(
                           primitive_discrepancies=r['model']['exact_selected_vs_birth_differences'],
                           certificates=[{key:c[key] for key in ('representation', 'fraction', 'lower_s',
                                          'upper_s', 'lower_years', 'upper_years', 'lower_margin', 'upper_margin')}
                                         for c in r['certificates']]) for name,r in models.items()})
        write(out/'RESULTS_SUMMARY.json', summary)
        receipt.update(actual_exit=0, status=artifact['status'],
                       outputs={p.name:identity(p) for p in (out/'EXACT_CERTIFICATES.json', out/'RESULTS_SUMMARY.json')})
        print(json.dumps(serializable(summary), indent=2))
    except Exception as error:
        receipt.update(actual_exit=1, status='FAILED_PRESERVED', error_type=type(error).__name__,
                       error_code=getattr(error, 'code', None), error=str(error),
                       evidence=getattr(error, 'evidence', None))
        raise
    finally:
        receipt.update(end_utc=datetime.now(timezone.utc).isoformat(), wall_s=time.monotonic()-started,
                       runtime=dict(python=sys.version, platform=platform.platform()))
        write(out/'EXECUTION_RECEIPT.json', receipt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true', required=True)
    parser.parse_args()
    execute()
