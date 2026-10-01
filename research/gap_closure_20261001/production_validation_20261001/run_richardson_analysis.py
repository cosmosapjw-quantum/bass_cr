"""Read-only extrapolation supplement after exact physical cache admission."""
from pathlib import Path
import argparse, json, sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import fresh_context_analysis as fresh
import richardson_diagnostic as rich

def analyze(manifests, raw_result, contract, output):
    declaration=fresh.read(contract)
    for name, expected in declaration['source_sha256'].items():
        if fresh.hp.sha(HERE/name)!=expected:
            raise ValueError('supplement source differs from result-blind declaration')
    plan=fresh._fixed(fresh.FD_PLAN,fresh.FD_PLAN_SHA)
    raw=fresh.read(raw_result)
    samples,provenance,context=fresh._load_lanes(manifests,[q['time_hex'] for q in plan['queries']])
    if raw['context_id']!=context['context_id'] or raw['fresh_snapshot_count']!=72:
        raise ValueError('original raw diagnostic does not match this admitted context')
    by_z={q['z_hex']:samples[q['time_hex']] for q in plan['queries']}
    results=[]
    for z in plan['centers']:
        ladder=[(h,by_z[float(z-h).hex()]['S'],by_z[float(z+h).hex()]['S']) for h in plan['h_ladder']]
        results.append({'z_a0':z,**rich.analyze_ladder(by_z[float(z).hex()]['D'],ladder,plan['identity']['velocity_au'])})
    report={'schema':'BASS_R4V_PHYSICAL_RICHARDSON_SUPPLEMENT_V1','status':'OBSERVATIONS_ONLY_NO_GATE_DECISION',
        'source_sha256':declaration['source_sha256'],'declaration_sha256':fresh.hp.sha(contract),
        'original_raw_result_sha256':fresh.hp.sha(raw_result),'original_raw_status':raw['status'],
        'context_id':context['context_id'],'provenance':provenance,'results':results,
        'new_native_calls':0,'original_acceptance_changed':False,
        'physical_G02_closed':False,'production_admission':'HOLD','capture':False,
        'rigorous_operator_error_bound':False}
    fresh.hp.write_new(output,report)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifests',nargs='+',required=True)
    for n in ('raw-result','contract','output'):p.add_argument('--'+n,required=True)
    a=p.parse_args();r=analyze(a.manifests,a.raw_result,a.contract,a.output)
    print(json.dumps({'status':r['status'],'centers':len(r['results']),'new_native_calls':0}))
