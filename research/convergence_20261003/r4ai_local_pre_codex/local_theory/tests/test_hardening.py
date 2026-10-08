import json,hashlib,subprocess,sys
from pathlib import Path
from fractions import Fraction as F
import pytest
from cr_reion.core import ContractError,interval
from cr_reion.provider import SourceModel,distribution
from test_reference import objects
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'runtime_tools'))
from merge_returns import combine_verified,checked_selection,check_contract

@pytest.mark.parametrize('bad',[None,1,{},'12'])
def test_bad_interval_is_contract_error(bad):
    with pytest.raises(ContractError):interval(bad)

@pytest.mark.parametrize('bad',[None,2,{'not':'list'},'0'])
def test_malformed_source_array(bad):
    s,_=objects();s['energies']=bad;b=json.dumps(s).encode()
    with pytest.raises(ContractError):SourceModel.load(b,hashlib.sha256(b).hexdigest())

@pytest.mark.parametrize('bad',[[None],[2],[{'velocity_m_s':None,'probability':'1'}]])
def test_malformed_distribution_entry(bad):
    with pytest.raises(ContractError):distribution(bad)

def test_cli_create_only_actual_source(tmp_path):
    s,e=objects();sp=tmp_path/'s.json';ep=tmp_path/'e.json';out=tmp_path/'result.json'
    sp.write_text(json.dumps(s));ep.write_text(json.dumps(e))
    command=[sys.executable,'-m','cr_reion','--source',str(sp),'--source-sha256',hashlib.sha256(sp.read_bytes()).hexdigest(),
        '--event',str(ep),'--event-sha256',hashlib.sha256(ep.read_bytes()).hexdigest(),'--output',str(out)]
    root=Path(__file__).resolve().parents[1]
    first=subprocess.run(command,cwd=root,capture_output=True,text=True)
    assert first.returncode==0,first.stderr
    data=json.loads(out.read_text());before=out.read_bytes()
    assert data['R_1s_m_minus3_s']==['30','60'] and data['physical_admission'] is False
    second=subprocess.run(command,cwd=root,capture_output=True,text=True)
    assert second.returncode==2 and out.read_bytes()==before

def test_unknown_merge_node():
    with pytest.raises(ValueError,match='unknown'):combine_verified([{'batch_sha256':'a','packets':[{'node_id':'center'}]}])

def test_duplicate_batch():
    with pytest.raises(ValueError,match='duplicate'):combine_verified([{'batch_sha256':'a','packets':[]},{'batch_sha256':'a','packets':[]}])

def selection():return {'schema':'R4AI_MULTI_BATCH_SELECTION_V1','batches':[{'path':'/tmp/m64/BATCH.json','sha256':'a'*64,'nodes':['m64']}]}

def test_selection_valid():assert checked_selection(selection())[0]['nodes']==['m64']

@pytest.mark.parametrize('mutation',['duplicate','relative','sha','unknown','empty','keys'])
def test_bad_selection(mutation):
    x=selection()
    if mutation=='duplicate':x['batches']+=[{'path':'/tmp/next/BATCH.json','sha256':'b'*64,'nodes':['m64']}]
    if mutation=='relative':x['batches'][0]['path']='relative'
    if mutation=='sha':x['batches'][0]['sha256']='bad'
    if mutation=='unknown':x['batches'][0]['nodes']=['center']
    if mutation=='empty':x['batches']=[]
    if mutation=='keys':x['unknown']=True
    with pytest.raises(ValueError):checked_selection(x)

def test_operator_to_dual_residual():
    from cr_reion.core import coefficient_residual_upper
    assert coefficient_residual_upper(4,'1/10','1/5','3/10',2,3,'2/5',2)==F(3,4)

@pytest.mark.parametrize('which',['s','h'])
def test_operator_bound_requires_positive_metric_and_hbar(which):
    from cr_reion.core import coefficient_residual_upper
    with pytest.raises(ContractError):coefficient_residual_upper(0 if which=='s' else 1,0,0,0,1,1,0,0 if which=='h' else 1)

def static_fixture():
    from merge_returns import LOCK_SHA
    row={'z_a0':'-2049/64','geometry_path':'g','geometry_sha256':'gsha','S_path':'s','S_sha256':'ssha'}
    b={'batch_id':'id','output':'/b','root':'/root','native':'/b/native','native_sha256':'nsha','resources':{'workers':1},'shared_library_pins':{}}
    item={'node_id':'m64','output':'/b/runs/m64'}
    auth={'schema':'R4AG_BATCH_AUTHORIZATION_V1','batch_id':'id','output':'/b','attempt_cap_per_node':1,'explicit_authorization_at_runtime':True,'authorized_nodes':['m64'],'maximum_native_points':1}
    c={'schema':'R4AG_SHIFTED_POINT_EXECUTION_V1','batch_id':'id','node_id':'m64','candidate_identity':'17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef','z':'-2049/64','output':item['output'],'package_root':'/root','source_lock_sha256':LOCK_SHA,'native_path':'/b/native','native_sha256':'nsha','precision_bits':256,'rho':'2','degrees':[16,24,32,40,48,56,64],'target_radius':'1/10000000000000000','quadrature_budget':'1/1000000000000000000','max_cells':10000,'max_split_depth':5,'epoch':'ACTUAL_STORED','caps':{'point_geometry':1,'window_jet':0,'D':0,'Vother':0,'attempts':1},'resources':b['resources'],'shared_library_pins':{},'global_ceiling':{'G02':'UNRESOLVED','production':'HOLD','capture':False,'all_bound':'OPEN','b_grid':'NO_GO'}}
    c.update({k:v for k,v in row.items() if k!='z_a0'})
    return c,b,item,row,auth

def test_consumed_contract_static_fixture_not_runtime():check_contract(*static_fixture())

@pytest.mark.parametrize('field,value',[('precision_bits',128),('rho','3'),('epoch','IDEAL'),('z','-32'),('target_radius','1'),('global_ceiling',{})])
def test_consumed_method_mutation_rejected(field,value):
    c,b,i,r,a=static_fixture();c[field]=value
    with pytest.raises(ValueError):check_contract(c,b,i,r,a)

def test_unauthorized_reuse_is_rejected():
    c,b,i,r,a=static_fixture();a['authorized_nodes']=['p64']
    with pytest.raises(ValueError):check_contract(c,b,i,r,a)
