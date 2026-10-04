"""Create a fresh fixture-only validation contract; does not run any integral."""
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'source'),str(ROOT/'parent/source'),str(ROOT/'parent/vendor')]
from native_adapter import build,sha

def prepare(output,contract):
    output,contract=Path(output),Path(contract)
    if not output.is_absolute() or not contract.is_absolute():raise ValueError('absolute paths required')
    if output.exists() or output.is_symlink() or contract.exists() or contract.is_symlink():raise FileExistsError('new paths required')
    if not contract.parent.is_dir():raise FileNotFoundError('contract parent must exist')
    result=build()
    names=['source/native_adapter.py','source/weak_cell.cpp','source/run_parity.py']
    names += [str(p.relative_to(ROOT)) for folder in ['parent/source','parent/vendor'] for p in (ROOT/folder).glob('*.py')]
    names += ['parent/evidence/LIGHT_FIXTURE_RESULT.json']
    data={'schema':'R4AN_THREE_FIXTURE_RUN_V1','precision_bits':256,'actual_atomic_integral_cap':0,'native_cells':3,'max_nodes':3072,'root_finder_calls':0,'majorant_recomputations':0,'per_cell_wall_seconds':120,'total_wall_seconds':420,'native_memory_limit_bytes':512*1024**2,'target_per_complex_entry':'1/10000000000000000','output':str(output),'native_sha256':result['native_sha256'],'pins':{n:sha(ROOT/n) for n in names}}
    with contract.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2,sort_keys=True)
    return {'status':'PREPARED_FIXTURE_ONLY_NOT_EXECUTED','contract':str(contract),'sha256':sha(contract),'atomic_integrals':0}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--contract',required=True);a=p.parse_args();print(json.dumps(prepare(a.output,a.contract)))
