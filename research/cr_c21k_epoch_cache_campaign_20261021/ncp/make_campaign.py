"""Bind the reviewed 52-slot matrix; no native process or scientific import."""
from __future__ import annotations
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

from scheduler import AdmissionError, digest, file_record, read_json, validate_manifest, verify_external, write_new

HERE = Path(__file__).resolve().parent
H = 'cr_c21h_vigilode_bridge_20261019'
I = 'cr_c21i_callback_optimization_20261020'
G = 'cr_c21g_reference_refinement_20261019'
F = 'cr_c21e_event_native_20261018'
K = 'cr_c21k_epoch_cache_campaign_20261021'
H_CONTENT = '40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8'
I_CONTENT = 'fe6bbaec2de5032b938aed0713623b9618ba70e6'
KNOWN_NATIVE = '1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40'
KNOWN_BRIDGE = '717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30'
MANIFEST_PINS = {H:'7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb',
                I:'f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec',
                G:'7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed'}


def paths(binding=None):
    binding = binding or {}
    def value(key): return binding.get(key, '${' + key + '}')
    iroot, kroot = value('i_checkout'), value('k_checkout')
    result = {'PYTHON': value('python'), 'H_UNIT': iroot+'/research/'+H,
        'I_UNIT': iroot+'/research/'+I, 'G_UNIT': iroot+'/research/'+G,
        'K_UNIT': kroot+'/research/'+K, 'K_CHECKOUT_I_UNIT': kroot+'/research/'+I,
        'I_SOURCE_DIR': iroot+'/research/'+F, 'I_G_UNIT': iroot+'/research/'+G,
        'I_BASELINE_DIR': iroot+'/research/'+F+'/evidence/C21F_NATIVE_NCP_20261018T1358Z',
        'K_SOURCE_DIR': kroot+'/research/'+F, 'K_G_UNIT': kroot+'/research/'+G,
        'K_BASELINE_DIR': kroot+'/research/'+F+'/evidence/C21F_NATIVE_NCP_20261018T1358Z',
        'BRIDGE': value('bridge_binary'), 'BRIDGE_BUILD_RECEIPT': value('bridge_build_receipt'),
        'NATIVE': value('native_binary'), 'H_PUBLICATION_RECEIPT': value('h_publication_receipt'),
        'I_PUBLICATION_RECEIPT': value('i_publication_receipt'), 'K_PUBLICATION_RECEIPT': value('k_publication_receipt'),
        'EVIDENCE_DIR': value('native_return_evidence')}
    return result


def substitute(template, values):
    def sub(match):
        return str(values.get(match.group(1), match.group(0)))
    return [re.sub(r'\$\{([^}]+)\}', sub, arg) for arg in template]


def original_h_context_changes(receipt, values):
    comparisons = {
        'input_identity.manifest_path': (receipt['input_identity']['manifest_path'], str(Path(values['I_G_UNIT'])/'EXECUTION_MANIFEST.json')),
        'bridge_identity.path': (receipt['bridge_identity']['path'], values['BRIDGE']),
        'native_identity.path': (receipt['native_identity']['path'], values['NATIVE']),
    }
    return [{'field': field, 'historical': str(Path(old).resolve()), 'current': str(Path(new).resolve())}
            for field, (old, new) in comparisons.items() if Path(old).resolve() != Path(new).resolve()]


def native_job(row, inventory, values, external, replacements):
    lane = row['lane']
    local = {'OUT':'${job_out}', 'CPU':'${cpu}', 'FIXTURE':row['fixture'],
             'METHOD':row['method'], 'VARIANT':row['variant'], 'MODE':row['mode']}
    prefix = 'K' if lane == 'K' else 'I'
    local.update(SOURCE_DIR='${'+prefix+'_SOURCE_DIR}', G_UNIT='${'+prefix+'_G_UNIT}',
                 BASELINE_DIR='${'+prefix+'_BASELINE_DIR}')
    command = substitute(inventory['command_templates'][lane],local)
    deps = list(row['hard_scientific_dependencies'])
    deps = list(dict.fromkeys(replacements.get(dep, dep) for dep in deps))
    if row['variant'] == 'fd_half':
        parent = replacements.get(row['hard_scientific_dependencies'][0], row['hard_scientific_dependencies'][0])
        base_path = str(Path(external[parent]['receipt_file']).parent) if parent in external else '${job:'+parent+'}'
        command += ['--base-job',base_path]
    command = substitute(command, values)
    schema = 'C21K_JOB_RECEIPT_V1' if lane == 'K' else 'C21H_JOB_RECEIPT_V1'
    success = [{'path':'schema','equals':schema},{'path':'execution','equals':'COMPLETE'},
               {'path':'fixture_name','equals':row['fixture']},{'path':'method','equals':row['method']},
               {'path':'variant','equals':row['variant']},{'path':'native_exit_code','equals':0}]
    if lane in ('I','K'):
        success.append({'path':'c21'+lane.lower()+'_runner.optimization','equals':row['mode']})
    return {'job_id':row['job_id'],'kind':'native_'+lane.lower()+'_single_job',
        'logical_slot_id':row['job_id'],'lane':lane,'fixture':row['fixture'],'method':row['method'],
        'optimization':row['mode'],'variant':row['variant'],'scope_origin':row['scope_origin'],
        'command':command,'dependencies':deps,'timeout_seconds':300,'raw_attempt_units':1,
        'comparison_evidence_dependency':replacements.get(row.get('comparison_evidence_dependency'), row.get('comparison_evidence_dependency')),
        'comparison_dependency_is_soft':True,
        'result_receipt':'JOB_RECEIPT.json','success':success,
        'conditional_reason':'Selected by current all-pending comparison request to resolve derivative-probe sensitivity after a matching COMPLETE same-lane base.' if row['variant']=='fd_half' else None}


def verify_checkout(root, expected):
    def git(*args):
        return subprocess.run(['git','-C',str(root),*args],text=True,capture_output=True,timeout=15)
    head=git('rev-parse','HEAD'); attached=git('symbolic-ref','-q','HEAD')
    if head.returncode or head.stdout.strip()!=expected or attached.returncode!=1:
        raise AdmissionError('DETACHED_PINNED_CHECKOUT_REQUIRED '+str(root))


def closure_records(binding, values):
    records={}
    def add(path, expected=None):
        path=Path(path).resolve(); actual=file_record(path)
        if expected is not None and actual!=expected:
            raise AdmissionError('SOURCE_CLOSURE_IDENTITY_MISMATCH '+str(path))
        records[str(path)]=actual
    for root in [Path(binding['i_checkout']),Path(binding['k_checkout'])]:
        research=root/'research'
        for unit in [H,I]+([K] if root==Path(binding['k_checkout']) else []):
            mp=research/unit/'EXECUTION_MANIFEST.json'; add(mp)
            expected_manifest=MANIFEST_PINS.get(unit,read_json(binding['k_publication_receipt']).get('execution_manifest_sha256'))
            if file_record(mp)['sha256']!=expected_manifest:
                raise AdmissionError('PINNED_MANIFEST_REQUIRED '+str(mp))
            for name,record in read_json(mp)['runtime_files'].items(): add(research/unit/name,record)
        gm=research/G/'EXECUTION_MANIFEST.json';add(gm);manifest=read_json(gm)
        if file_record(gm)['sha256']!=MANIFEST_PINS[G]:
            raise AdmissionError('PINNED_G_MANIFEST_REQUIRED')
        for prefix,key in [(research/F,'c21f_runtime_files'),(research/G,'c21g_runtime_files'),
                           (research/F/'evidence/C21F_NATIVE_NCP_20261018T1358Z','baseline_files')]:
            for name,record in manifest[key].items():add(prefix/name,record)
    for key in ['python','native_binary','bridge_binary','bridge_build_receipt',
                'h_publication_receipt','i_publication_receipt','k_publication_receipt']:
        add(binding[key])
    if binding.get('native_build_dir'):
        for name in ['owner_commit.txt','build_exit.txt','input_sha256.txt','owner_source.tar']:
            add(Path(binding['native_build_dir'])/name)
    for name in ['scheduler.py','make_campaign.py','BACKLOG_INVENTORY.json','DEPENDENCY_CONTROL_SCOPE_DECISION.json']:
        add(HERE/name)
    return [{'path':path,'record':record} for path,record in sorted(records.items())]


def git_blob(root, commit, relative):
    result=subprocess.run(['git','-C',str(root),'show',commit+':'+relative],
        capture_output=True,timeout=15)
    if result.returncode:raise AdmissionError('PUBLISHED_BLOB_UNAVAILABLE '+relative)
    return result.stdout


def pure_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def verify_publication_and_build(binding,values,content):
    """Reuse K's pure stdlib publication verifier and original G owner verifier."""
    kroot=Path(binding['k_checkout']);iunit=Path(values['K_CHECKOUT_I_UNIT']);kunit=Path(values['K_UNIT'])
    # Establish byte identity before importing the publication-contract module.
    for name in ['epoch_pilot_contract.py','ncp/scheduler.py','ncp/make_campaign.py',
                 'ncp/BACKLOG_INVENTORY.json','ncp/DEPENDENCY_CONTROL_SCOPE_DECISION.json']:
        actual=(kunit/name).read_bytes() if not name.startswith('ncp/') else (HERE/Path(name).name).read_bytes()
        if actual!=git_blob(kroot,content,'research/'+K+'/'+name):
            raise AdmissionError('PUBLISHED_COORDINATOR_OR_CONTRACT_SOURCE_MISMATCH '+name)
    contract=pure_module(kunit/'epoch_pilot_contract.py','c21k_preparation_publication_contract')
    h_own,i_own,_=contract.verify_inherited_sources(iunit)
    k_own,_=contract.verify_k_source('vectorized_exact',kunit)
    publications=contract.verify_publications(binding['k_publication_receipt'],binding['i_publication_receipt'],
        binding['h_publication_receipt'],k_own,i_own,h_own,k_unit=kunit,i_unit=iunit)
    for key in ['k_publication_receipt','i_publication_receipt','h_publication_receipt']:
        if Path(binding[key]).resolve().is_relative_to(Path(binding['i_checkout']).resolve()):
            raise AdmissionError('PUBLICATION_RECEIPT_MUST_BE_OUTSIDE_I_CHECKOUT')
    authority=pure_module(Path(values['I_G_UNIT'])/'campaign_contract.py','c21k_preparation_original_g_contract')
    native=authority.verify_native_binary(binding['native_binary'],values['I_SOURCE_DIR'],binding.get('native_build_dir'))
    bridge_record=file_record(binding['bridge_binary']);build=read_json(binding['bridge_build_receipt'])
    h_manifest=read_json(Path(values['H_UNIT'])/'EXECUTION_MANIFEST.json')
    expected={key:h_manifest['runtime_files'][key] for key in ['rust_bridge/Cargo.toml','rust_bridge/Cargo.lock','rust_bridge/src/main.rs']}
    if (build.get('binary_sha256')!=bridge_record['sha256']
        or build.get('vigilode_commit')!='8a8bd409b1d96c7b7421f496d229e119fd3d284e'
        or build.get('diffsol_version')!='0.17.1' or build.get('exit_code')!=0
        or build.get('source_files')!=expected):
        raise AdmissionError('ORIGINAL_H_BRIDGE_BUILD_PROVENANCE_MISMATCH')
    return {'publication':publications,'native':native,'bridge':bridge_record,
            'bridge_build_receipt':file_record(binding['bridge_build_receipt'])}


def build(binding=None):
    if binding is not None:
        binding=copy.deepcopy(binding)
        if binding.get('native_build_dir') and not Path(binding['native_build_dir']).is_absolute():
            raise AdmissionError('ABSOLUTE_NATIVE_BUILD_DIRECTORY_REQUIRED')
        reuse=binding.get('g_reuse_directories',[])
        if not isinstance(reuse,list) or any(not isinstance(p,str) or not Path(p).is_absolute() for p in reuse):
            raise AdmissionError('ABSOLUTE_G_REUSE_DIRECTORIES_REQUIRED')
        binding['g_reuse_directories']=[str(Path(p).resolve()) for p in reuse]
        for key in ['python','i_checkout','k_checkout','bridge_binary','bridge_build_receipt','native_binary',
                    'h_publication_receipt','i_publication_receipt','k_publication_receipt','native_return_evidence','native_build_dir']:
            if binding.get(key) and Path(binding[key]).is_absolute():
                binding[key]=str(Path(binding[key]).resolve())
    inventory=read_json(HERE/'BACKLOG_INVENTORY.json')
    values=paths(binding); external={};jobs=[]; replacements={}; context_repairs=[]
    for old in inventory['completed_external_nodes']:
        receipt_path=values['EVIDENCE_DIR']+'/'+old['original_return_directory_name']+'/JOB_RECEIPT.json'
        node={'job_id':old['job_id'],'kind':'external_complete','dependencies':[],
            'receipt_file':receipt_path,'receipt_record':{k:old['receipt'][k] for k in ['bytes','sha256']},
            'success':[{'path':'execution','equals':'COMPLETE'},{'path':'command','equals':'native'},
                {'path':'native_exit_code','equals':0}],
            'context_files':[{'path':values['NATIVE'],'receipt_path':'native_identity'},
                             {'path':values['BRIDGE'],'receipt_path':'bridge_identity'}],
            'scope_origin':'HISTORICAL_COMPLETE_NATIVE_RESULT_NO_AUTOMATIC_RERUN'}
        if old['mode'] is not None:node['success'].append({'path':'c21i_runner.optimization','equals':old['mode']})
        external[node['job_id']]=node;jobs.append(node)
    content='RESOLVE_FROM_PUBLISHED_K_RECEIPT';admission=None
    input_files=[]
    if binding is not None:
        required=['python','i_checkout','k_checkout','bridge_binary','bridge_build_receipt','native_binary',
                  'h_publication_receipt','i_publication_receipt','k_publication_receipt','native_return_evidence']
        if any(not binding.get(k) or not Path(binding[k]).is_absolute() for k in required):
            raise AdmissionError('ABSOLUTE_REAL_BINDING_PATHS_REQUIRED')
        published=read_json(binding['k_publication_receipt']);content=published.get('content_commit')
        if published.get('status')!='PUBLISHED' or not isinstance(content,str) or not re.fullmatch('[0-9a-f]{40}',content):
            raise AdmissionError('ACTUAL_PUBLISHED_K_CONTENT_REQUIRED')
        verify_checkout(binding['i_checkout'],I_CONTENT);verify_checkout(binding['k_checkout'],content)
        input_files=closure_records(binding,values)
        admission=verify_publication_and_build(binding,values,content)
        bytes_changed=(admission['native']['sha256']!=KNOWN_NATIVE or admission['bridge']['sha256']!=KNOWN_BRIDGE)
        for node in external.values():
            if bytes_changed:
                node['historical_only']=True
                node['current_context_compatible']=False
                node['context_files']=[]
                node['current_context_mismatch']='Verified native or bridge build bytes differ; historical COMPLETE is preserved and not claimed as matching reuse.'
            else:node['current_context_compatible']=True
            verify_external(node)
        hkey='H_common_ic_vigilode_rodas5p_base'
        old=read_json(external[hkey]['receipt_file'])
        changes=original_h_context_changes(old,values)
        external[hkey]['fd_parent_context_compatible']=not bytes_changed and not changes
        for node in external.values():
            node['current_context_compatibility_scope']='Matching native/bridge bytes and fixed scientific inputs; original H FD absolute-path context is reported separately.'
        keys=list(external) if bytes_changed else [hkey] if changes else []
        replacements.update({key:key+'_context_control' for key in keys})
        for key in keys:
            control=next(copy.deepcopy(row) for row in inventory['logical_jobs'] if row['job_id']==key)
            control['job_id']=replacements[key]
            control['scope_origin']='PRELAUNCH_VERIFIED_BUILD_DEPENDENCY_CONTROL_NOT_FAILURE_RETRY' if bytes_changed else 'PRELAUNCH_OBSERVED_PATH_CONTEXT_REPAIR_NOT_FAILURE_RETRY'
            job=native_job(control,inventory,values,external,replacements)
            if binding.get('native_build_dir'):job['command']+=['--build-dir',binding['native_build_dir']]
            job['logical_slot_id']=key
            reason={'binary_bytes_changed':bytes_changed,'path_changes':changes if key==hkey else [],
                    'current_native_identity':admission['native'],'current_bridge_identity':admission['bridge']}
            job['context_change_evidence']=reason
            jobs.append(job)
            context_repairs.append({'job_id':control['job_id'],'reason':reason,
                'old_completed_state_preserved':True,'maximum_new_attempts':1,'retry_after_failure':False})
    for row in inventory['logical_jobs']:
        if row['lane']=='G' or row['status']=='COMPLETE_EXTERNAL_REUSE':continue
        job=native_job(row,inventory,values,external,replacements)
        if binding and binding.get('native_build_dir'):job['command']+=['--build-dir',binding['native_build_dir']]
        jobs.append(job)
    gcmd=substitute(inventory['command_templates']['G'],{'OUT':'${job_out}','CPU':'${cpu}',
        'SOURCE_DIR':'${I_SOURCE_DIR}','G_UNIT':'${I_G_UNIT}','BASELINE_DIR':'${I_BASELINE_DIR}'})
    gcmd=substitute(gcmd,values)
    if binding and binding.get('native_build_dir'):gcmd+=['--build-dir',binding['native_build_dir']]
    if binding:
        for previous in binding.get('g_reuse_directories',[]):gcmd+=['--reuse',previous]
    jobs.append({'job_id':'G_ORIGINAL_BOUNDED_CAMPAIGN','kind':'standalone_g_campaign','dependencies':[],
        'command':gcmd,'timeout_seconds':3660,'raw_attempt_units':12,'result_receipt':'RETURN_TO_CHATGPT.json',
        'success':[{'path':'schema','equals':'C21G_EXECUTION_RETURN_V1'},
            {'path':'status','one_of':['COMPLETED_BOUNDED_PILOT','PARTIAL_OR_REFERENCE_HOLD']}],
        'internal_reference_jobs':8,'internal_conditional_history_jobs':4,
        'internal_contract':'Original unchanged G run_campaign.py; all8 execution COMPLETE plus original native_source sensitivity gate before histories.'})
    result={'schema':'C21K_BOUNDED_CAMPAIGN_V1','binding_status':'BOUND' if binding else 'UNBOUND_NOT_EXECUTABLE',
        'source_identity':{'repository':'cosmosapjw-quantum/bass_cr','H_content':H_CONTENT,'I_content':I_CONTENT,
            'G_H_I_actual_execution_checkout':I_CONTENT,
            'G_H_byte_provenance':'Unchanged original G/H manifest-verified runtime bytes inherited by fe6; the original historical content commit is distinct from this actual execution checkout.',
            'K_content':content,'backlog_inventory':file_record(HERE/'BACKLOG_INVENTORY.json'),
            'scheduler':file_record(HERE/'scheduler.py'),'manifest_builder':file_record(Path(__file__))},
        'input_files':input_files,'bindings':{},'jobs':jobs,'campaign_timeout_seconds':21600,
        'publication_and_build_admission':admission,
        'maximum_raw_attempt_units':49+len(context_repairs),'context_repair_jobs':context_repairs,
        'optional_dependency_control_contract':'Exclusive branches: unchanged matching inputs add0; identical binary bytes with changed H FD context paths add1 H base; verified changed native/bridge bytes add3 H base/I vectorized base/I vectorized FD. Original completed3 stay immutable, never rewritten or automatically retried.',
        'science_jobs_accounting':{'logical_slots':52,'historical_completed':3,'nominal_pending_maximum':49,
            'historical_pending':21,'operational_expansion':28,'nominal_pending_base_or_reference':26,
            'nominal_pending_conditional':23,'new_context_control_attempts':len(context_repairs),
            'maximum_new_attempt_units':49+len(context_repairs),'top_level_pending_processes':38+len(context_repairs),
            'G_internal_maximum':12,'G_conditional':4,'nominal_FD_conditional':19,
            'additional_control_FD':sum(j.get('variant')=='fd_half' and j['job_id'].endswith('_context_control') for j in jobs)},
        'operational_override':{'source':'Current user request to prepare every remaining job using independent resource-admitted workers',
            'old_J_single_new_job_and_no_auto_submission':'Superseded only for this separately identified prepared matrix; original J packet unchanged',
            'preserved':['CPU55','original per-job worker1/budgets','G internal gate','same-lane FD parent',
                'source/native/publication admission','scientific HOLD','global_error_bound=null']},
        'global_error_bound':None,'actual_native_execution':'NOT_RUN','actual_ncp_performance':'NOT_EVALUATED'}
    return validate_manifest(result)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bindings',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        result=build(read_json(args.bindings) if args.bindings else None)
    except (OSError,ValueError,KeyError,AdmissionError) as error:
        write_new(args.out,{'schema':'C21K_CAMPAIGN_BINDING_FAILURE_V1','status':'BLOCKED_INPUT_ADMISSION',
            'error':type(error).__name__+': '+str(error),'actual_native_execution':'NOT_RUN','global_error_bound':None})
        print(str(error),file=sys.stderr);return 2
    write_new(args.out,result)
    print(json.dumps({'status':result['binding_status'],'coordinator_nodes':len(result['jobs']),
        'accounting':result['science_jobs_accounting']}));return 0


if __name__=='__main__':raise SystemExit(main())
