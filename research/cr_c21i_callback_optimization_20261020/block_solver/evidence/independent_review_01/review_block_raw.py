"""Independent Decimal residual check of already-produced Rust block raw.

Does not run a solver, candidate, benchmark, or native process. Uses exact
binary64 input reconstruction and 100-digit Decimal arithmetic for W x - b.
"""
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal, localcontext
import csv,hashlib,json,math,struct

ROOT=Path('/workspace/scratch/da42c813ee8c')
UNIT=ROOT/'bass_cr/research/cr_c21i_callback_optimization_20261020/block_solver'
RAW=UNIT/'evidence/benchmark_01'
OUT=ROOT/'c21i_theory/raw/BLOCK_INDEPENDENT_RAW_REVIEW.json'
def record(path):
    data=path.read_bytes();return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
receipt=json.loads((UNIT/'evidence/BENCHMARK_RUN_RECEIPT.json').read_text())
sources={name:record(UNIT/name) for name in receipt['sources_before']}
assert all(rec['sha256']==receipt['sources_before'][name]==receipt['sources_after'][name]
           for name,rec in sources.items())
input_files=sorted(RAW.glob('input_m*_g*.csv'))
blocks={}
for path in input_files:
    m=int(path.stem.split('_')[1][1:]);g=int(path.stem.split('_')[2][1:]);n=m+g+15
    data={}
    for row in csv.DictReader(path.open()):
        value=struct.unpack('>d',bytes.fromhex(row['binary64_hex']))[0]
        assert struct.pack('>d',value)==struct.pack('>d',float(row['value']))
        assert math.isfinite(value)
        values=data.setdefault(row['block'],[])
        assert int(row['index'])==len(values)
        values.append(value)
    assert {key:len(data[key]) for key in data}=={'shift':1,'A':m*g,'B':g*m,
        'C':g*g,'P':15*m,'Q':15*g,'rhs':n}
    blocks[m,g]=data

solutions=[json.loads(line) for line in (RAW/'solutions.jsonl').read_text().splitlines()]
timings=list(csv.DictReader((RAW/'solve_repeats.csv').open()))
assert len(solutions)==len(timings)==312
unique={};row_index={}
for item,row in zip(solutions,timings):
    m,g=item['m'],item['g'];n=m+g+15
    assert (int(row['M']),int(row['G']),row['phase'],row['method'],int(row['iteration']))==(
        m,g,item['phase'],item['method'],item['iteration'])
    assert len(item['solution'])==n and all(math.isfinite(v) for v in item['solution'])
    assert float(row['full_backward_error'])<=1e-13
    key=(m,g,item['method'],tuple(struct.pack('>d',v) for v in item['solution']))
    unique.setdefault(key,item)
    row_index.setdefault((m,g,item['method']),set()).add(key)
assert all(len(keys)==1 for keys in row_index.values())

checks=[]
with localcontext() as context:
    context.prec=100
    for key,item in unique.items():
        m,g=item['m'],item['g'];n=m+g+15
        block={name:[Decimal.from_float(v) for v in values] for name,values in blocks[m,g].items()}
        shift=block['shift'][0];x=list(map(Decimal.from_float,item['solution']));rhs=block['rhs']
        # Materialize the independently assembled mathematical W, treating
        # binary64 supplied J and shift as exact real inputs. This does not
        # imitate the candidate's sequential floating-point residual routine.
        w=[[Decimal(int(i==j)) for j in range(n)] for i in range(n)]
        for i in range(m):
            for j in range(g):w[i][m+j]-=shift*block['A'][i*g+j]
        for i in range(g):
            for j in range(m):w[m+i][j]-=shift*block['B'][i*m+j]
            for j in range(g):w[m+i][m+j]-=shift*block['C'][i*g+j]
        for i in range(15):
            for j in range(m):w[m+g+i][j]-=shift*block['P'][i*m+j]
            for j in range(g):w[m+g+i][m+j]-=shift*block['Q'][i*g+j]
        residual=[sum((a*b for a,b in zip(row,x)),Decimal(0))-target for row,target in zip(w,rhs)]
        rnorm=max(map(abs,residual));wnorm=max(sum(map(abs,row),Decimal(0)) for row in w)
        denom=wnorm*max(map(abs,x))+max(map(abs,rhs))
        eta=rnorm/denom if denom else Decimal(0)
        assert eta<=Decimal('1e-13')
        checks.append({'m':m,'g':g,'method':item['method'],'n':n,
            'unique_binary64_solution_rows':1,'reused_identical_solution_rows':sum(
                s['m']==m and s['g']==g and s['method']==item['method'] for s in solutions),
            'decimal_full_residual_inf':str(rnorm),'decimal_normwise_backward_error':str(eta),
            'max_ledger_residual':str(max(map(abs,residual[m+g:]))),'status':'PASS_SCOPED'})

jvps=[json.loads(line) for line in (RAW/'jvp_outputs.jsonl').read_text().splitlines()]
jvp_csv=list(csv.DictReader((RAW/'jvp_repeats.csv').open()))
assert len(jvps)==len(jvp_csv)==240
for item,row in zip(jvps,jvp_csv):
    assert (item['m'],item['g'],item['method'],item['iteration'])==(
        int(row['M']),int(row['G']),row['method'],int(row['iteration']))
    assert len(item['output'])==item['m']+item['g']+15
    assert all(math.isfinite(v) for v in item['output'])
groups={}
for item in jvps:groups.setdefault((item['m'],item['g'],item['iteration']),{})[item['method']]=item['output']
max_jvp_diff=max(max(abs(a-b) for a,b in zip(group['structured_jvp_into'],group['dense_matvec_into']))
                 for group in groups.values())
assert max_jvp_diff==0.
files={str(p.relative_to(UNIT)):record(p) for p in [UNIT/'evidence/BENCHMARK_RUN_RECEIPT.json',
    *input_files,RAW/'solutions.jsonl',RAW/'solve_repeats.csv',RAW/'jvp_outputs.jsonl',RAW/'jvp_repeats.csv']}
assert all(record(UNIT/name)==value for name,value in sources.items())
assert all(record(UNIT/name)==value for name,value in files.items())
result={'schema':'C21I_BLOCK_INDEPENDENT_RAW_REVIEW_V1','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
    'status':'PASS_SCOPED_EXISTING_MANUFACTURED_RAW','source_identity':sources,'raw_identity':files,
    'source_and_raw_unchanged_before_after':True,'solve_rows_covered_by_exact_output_identity':len(solutions),
    'unique_solutions_recomputed':len(unique),'decimal_precision_digits':100,'checks':checks,
    'max_decimal_normwise_backward_error':str(max(Decimal(c['decimal_normwise_backward_error']) for c in checks)),
    'jvp_rows_compared':len(jvps),'max_numeric_jvp_difference':max_jvp_diff,
    'new_rust_execution':False,'new_native_execution':False,'new_benchmark':False,
    'global_error_bound':None,
    'limits':'Existing manufactured block inputs only; Decimal residual uses exact binary64 input values, not directed-rounded enclosure; no ODE/native acceptance.'}
with OUT.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({key:result[key] for key in ['status','solve_rows_covered_by_exact_output_identity',
    'unique_solutions_recomputed','max_decimal_normwise_backward_error','jvp_rows_compared',
    'max_numeric_jvp_difference','new_rust_execution','new_native_execution']},indent=2))
